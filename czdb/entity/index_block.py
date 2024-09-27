class IndexBlock:
    def __init__(self, start_ip, end_ip, data_ptr, data_len, db_type):
        self.start_ip = start_ip
        self.end_ip = end_ip
        self.data_ptr = data_ptr
        self.data_len = data_len
        self.db_type = db_type

    def get_start_ip(self):
        return self.start_ip

    def set_start_ip(self, start_ip):
        self.start_ip = start_ip
        return self

    def get_end_ip(self):
        return self.end_ip

    def set_end_ip(self, end_ip):
        self.end_ip = end_ip
        return self

    def get_data_ptr(self):
        return self.data_ptr

    def set_data_ptr(self, data_ptr):
        self.data_ptr = data_ptr
        return self

    def get_data_len(self):
        return self.data_len

    def set_data_len(self, data_len):
        self.data_len = data_len
        return self

    @staticmethod
    def get_index_block_length(db_type):
        return 13 if db_type == 4 else 37

    def get_bytes(self):
        ip_bytes_length = 4 if self.db_type == 'IPV4' else 16
        b = [0] * self.get_index_block_length(self.db_type)

        for i in range(ip_bytes_length):
            b[i] = ord(self.start_ip[i])
            b[i + ip_bytes_length] = ord(self.end_ip[i])

        self.write_int_long(b, ip_bytes_length * 2, self.data_ptr)
        self.write(b, ip_bytes_length * 2 + 4, self.data_len, 1)

        return b

    def write_int_long(self, b, offset, value):
        b[offset] = (value >> 24) & 0xFF
        b[offset + 1] = (value >> 16) & 0xFF
        b[offset + 2] = (value >> 8) & 0xFF
        b[offset + 3] = value & 0xFF

    def write(self, b, offset, value, length):
        for i in range(length):
            b[offset + i] = (value >> (8 * (length - i - 1))) & 0xFF