import struct

from czdb.entity.data_block import DataBlock
from czdb.entity.index_block import IndexBlock
from czdb.utils.decryptor import Decryptor
from czdb.utils.hyper_header_decoder import HyperHeaderDecoder
from czdb.utils.byte_util import ByteUtil

class DbSearcher:
    SUPER_PART_LENGTH = 17
    FIRST_INDEX_PTR = 5
    END_INDEX_PTR = 13
    HEADER_BLOCK_PTR = 9
    FILE_SIZE_PTR = 1

    QUERY_TYPE_MEMORY = "MEMORY"
    QUERY_TYPE_BTREE = "BTREE"

    def __init__(self, db_file, query_type, key):
        self.query_type = query_type
        self.file_name = db_file
        self.raf = open(db_file, "rb")
        header_block = HyperHeaderDecoder.decrypt(self.raf, key)

        self.header_sip = []
        self.header_ptr = []

        offset = header_block.get_header_size()
        self.header_size = offset

        self.raf.seek(offset)
        super_bytes = self.raf.read(DbSearcher.SUPER_PART_LENGTH)
        super_bytes = list(super_bytes)

        self.db_type = 4 if (super_bytes[0] & 1) == 0 else 6
        self.ip_bytes_length = 4 if self.db_type == 4 else 16

        self.load_geo_setting(key)

        if query_type == self.QUERY_TYPE_MEMORY:
            self.initialize_for_memory_search()
        elif query_type == self.QUERY_TYPE_BTREE:
            self.init_btree_mode_param()

    def search(self, ip):
        ip_bytes = self.get_ip_bytes(ip)

        data_block = None

        if self.query_type == self.QUERY_TYPE_MEMORY:
            data_block = self.memory_search(ip_bytes)
        elif self.query_type == self.QUERY_TYPE_BTREE:
            data_block = self.b_tree_search(ip_bytes)

        if data_block is None:
            return None
        else:
            return data_block.get_region(self.geo_map_data, self.column_selection)

    def close(self):
        if self.raf:
            self.raf.close()
            self.raf = None

        self.db_bin_str = None
        self.header_sip = []
        self.header_ptr = []
        self.geo_map_data = None

    def compare_bytes(self, bytes1, bytes2, length):
        for i in range(length):
            byte1 = bytes1[i]
            byte2 = bytes2[i]

            if byte1 != byte2:
                return -1 if byte1 < byte2 else 1
        return 0

    def memory_search(self, ip):
        l = 0
        h = self.total_index_blocks

        data_ptr = 0
        data_len = 0

        block_len = IndexBlock.get_index_block_length(self.db_type)

        while l <= h:
            m = (l + h) // 2
            p = self.first_index_ptr + m * block_len
            sip = self.db_bin_str[p:p + self.ip_bytes_length]
            eip = self.db_bin_str[p + self.ip_bytes_length:p + 2 * self.ip_bytes_length]

            cmp_start = self.compare_bytes(ip, sip, self.ip_bytes_length)
            cmp_end = self.compare_bytes(ip, eip, self.ip_bytes_length)

            if cmp_start >= 0 and cmp_end <= 0:
                data_ptr = struct.unpack_from("<L", self.db_bin_str, p + 2 * self.ip_bytes_length)[0]
                data_len = self.db_bin_str[p + 2 * self.ip_bytes_length + 4]
                break
            elif cmp_start < 0:
                h = m - 1
            else:
                l = m + 1

        if data_ptr == 0:
            return None

        region = self.db_bin_str[data_ptr:data_ptr + data_len]

        return DataBlock(region, data_ptr)

    def b_tree_search(self, ip):
        sptr, eptr = self.search_in_header(ip)

        if sptr == 0:
            return None

        block_len = eptr - sptr
        blen = IndexBlock.get_index_block_length(self.db_type)

        self.fseek(self.raf, sptr)
        i_buffer = self.raf.read(block_len + blen)

        l = 0
        h = block_len // blen

        data_ptr = 0
        data_len = 0

        while l <= h:
            m = (l + h) // 2
            p = m * blen
            sip = i_buffer[p:p + self.ip_bytes_length]
            eip = i_buffer[p + self.ip_bytes_length:p + 2 * self.ip_bytes_length]

            cmp_start = self.compare_bytes(ip, sip, self.ip_bytes_length)
            cmp_end = self.compare_bytes(ip, eip, self.ip_bytes_length)

            if cmp_start >= 0 and cmp_end <= 0:
                data_ptr = struct.unpack_from("<L", i_buffer, p + 2 * self.ip_bytes_length)[0]
                data_len = i_buffer[p + 2 * self.ip_bytes_length + 4]
                break
            elif cmp_start < 0:
                h = m - 1
            else:
                l = m + 1

        if data_ptr == 0:
            return None

        self.fseek(self.raf, data_ptr)
        region = self.raf.read(data_len)

        return DataBlock(region, data_ptr)

    def get_ip_bytes(self, ip):
        if self.db_type == 4:
            if not self.validate_ip(ip, 4):
                raise Exception(f"IP [{ip}] format error for {self.db_type}")
            ip_bytes = self.inet_pton(ip)
        else:
            if not self.validate_ip(ip, 6):
                raise Exception(f"IP [{ip}] format error for {self.db_type}")
            ip_bytes = self.inet_pton(ip)
        return list(ip_bytes)

    def search_in_header(self, ip):
        l = 0
        h = self.header_length - 1
        sptr = 0
        eptr = 0

        while l <= h:
            m = (l + h) // 2
            cmp = self.compare_bytes(ip, self.header_sip[m], self.ip_bytes_length)

            if cmp < 0:
                h = m - 1
            elif cmp > 0:
                l = m + 1
            else:
                sptr = self.header_ptr[m - 1 if m > 0 else m]
                eptr = self.header_ptr[m]
                break

        if l == 0 and h <= 0:
            return [0, 0]

        if l > h:
            if l < self.header_length:
                sptr = self.header_ptr[l - 1]
                eptr = self.header_ptr[l]
            elif h >= 0 and h + 1 < self.header_length:
                sptr = self.header_ptr[h]
                eptr = self.header_ptr[h + 1]
            else:
                sptr = self.header_ptr[self.header_length - 1]
                block_len = IndexBlock.get_index_block_length(self.db_type)
                eptr = sptr + block_len

        return [sptr, eptr]

    def load_geo_setting(self, key):
        self.fseek(self.raf, self.END_INDEX_PTR)
        data = self.raf.read(4)
        end_index_ptr = ByteUtil.get_int_long(data, 0)

        column_selection_ptr = end_index_ptr + IndexBlock.get_index_block_length(self.db_type)
        self.fseek(self.raf, column_selection_ptr)
        data = self.raf.read(4)
        self.column_selection = ByteUtil.get_int_long(data, 0)

        if self.column_selection == 0:
            self.geo_map_data = None
            return

        geo_map_ptr = column_selection_ptr + 4
        self.fseek(self.raf, geo_map_ptr)

        data = self.raf.read(4)
        geo_map_size = ByteUtil.get_int_long(data, 0)

        self.fseek(self.raf, geo_map_ptr + 4)
        self.geo_map_data = self.raf.read(geo_map_size)

        decryptor = Decryptor(key)
        self.geo_map_data = decryptor.decrypt(self.geo_map_data)

    def initialize_for_memory_search(self):
        self.fseek(self.raf, 0)
        file_size = self.get_file_size() - self.header_size
        self.db_bin_str = self.raf.read(file_size)

        self.total_header_block_size = struct.unpack_from("<L", self.db_bin_str, self.HEADER_BLOCK_PTR)[0]

        file_size_in_file = struct.unpack_from("<L", self.db_bin_str, self.FILE_SIZE_PTR)[0]

        if file_size != file_size_in_file:
            raise Exception("FileSize not match with the file")

        self.first_index_ptr = struct.unpack_from("<L", self.db_bin_str, self.FIRST_INDEX_PTR)[0]
        last_index_ptr = struct.unpack_from("<L", self.db_bin_str, self.END_INDEX_PTR)[0]
        self.total_index_blocks = ((last_index_ptr - self.first_index_ptr) // IndexBlock.get_index_block_length(self.db_type)) + 1

        header_block_bytes = self.db_bin_str[self.SUPER_PART_LENGTH:self.SUPER_PART_LENGTH + self.total_header_block_size]
        self.init_header_block(header_block_bytes, self.total_header_block_size)

    def init_btree_mode_param(self):
        self.fseek(self.raf, 0)
        data = self.raf.read(self.SUPER_PART_LENGTH)
        self.total_header_block_size = struct.unpack_from("<L", data, self.HEADER_BLOCK_PTR)[0]

        data = self.raf.read(self.total_header_block_size)

        self.init_header_block(data, self.total_header_block_size)

    def init_header_block(self, header_bytes, size):
        index_length = 20

        idx = 0

        for i in range(0, size, index_length):
            data_ptr_segment = header_bytes[i + 16:i + 20]
            data_ptr = struct.unpack_from("<L", data_ptr_segment)[0]

            if data_ptr == 0:
                break

            self.header_sip.append(list(header_bytes[i:i + 16]))
            self.header_ptr.append(data_ptr)
            idx += 1

        self.header_length = idx

    def fseek(self, handler, offset):
        handler.seek(self.header_size + offset)

    def validate_ip(self, ip, version):
        import socket
        try:
            socket.inet_pton(socket.AF_INET if version == 4 else socket.AF_INET6, ip)
        except socket.error:
            return False
        return True

    def inet_pton(self, ip):
        import socket
        return socket.inet_pton(socket.AF_INET if self.db_type == 4 else socket.AF_INET6, ip)

    def get_file_size(self):
        import os
        return os.path.getsize(self.file_name)