from czdb.utils.byte_util import ByteUtil

class HyperHeaderBlock:
    HEADER_SIZE = 12

    def __init__(self):
        self.version = None
        self.client_id = None
        self.encrypted_block_size = None
        self.encrypted_data = None
        self.decrypted_block = None

    def get_version(self):
        return self.version

    def set_version(self, version):
        self.version = version

    def get_client_id(self):
        return self.client_id

    def set_client_id(self, client_id):
        self.client_id = client_id

    def get_encrypted_block_size(self):
        return self.encrypted_block_size

    def set_encrypted_block_size(self, encrypted_block_size):
        self.encrypted_block_size = encrypted_block_size

    def get_encrypted_data(self):
        return self.encrypted_data

    def set_encrypted_data(self, encrypted_data):
        self.encrypted_data = encrypted_data

    def get_decrypted_block(self):
        return self.decrypted_block

    def set_decrypted_block(self, decrypted_block):
        self.decrypted_block = decrypted_block

    @staticmethod
    def from_bytes(bytes):
        version = ByteUtil.get_int_long(bytes, 0)
        client_id = ByteUtil.get_int_long(bytes, 4)
        encrypted_block_size = ByteUtil.get_int_long(bytes, 8)

        header_block = HyperHeaderBlock()
        header_block.set_version(version)
        header_block.set_client_id(client_id)
        header_block.set_encrypted_block_size(encrypted_block_size)

        return header_block

    def get_header_size(self):
        return 12 + self.encrypted_block_size + self.decrypted_block.get_random_size()