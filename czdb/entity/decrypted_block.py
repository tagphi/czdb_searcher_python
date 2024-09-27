import base64
from Crypto.Cipher import AES
from czdb.utils.byte_util import ByteUtil

class DecryptedBlock:
    def __init__(self):
        self.client_id = None
        self.expiration_date = None
        self.random_size = None

    def get_client_id(self):
        return self.client_id

    def set_client_id(self, client_id):
        self.client_id = client_id

    def get_expiration_date(self):
        return self.expiration_date

    def set_expiration_date(self, expiration_date):
        self.expiration_date = expiration_date

    def get_random_size(self):
        return self.random_size

    def set_random_size(self, random_size):
        self.random_size = random_size

    @staticmethod
    def decrypt(key, encrypted_bytes):
        key_bytes = base64.b64decode(key)
        cipher = AES.new(key_bytes, AES.MODE_ECB)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        decrypted_bytes = list(decrypted_bytes)

        decrypted_block = DecryptedBlock()
        decrypted_block.set_client_id(ByteUtil.get_int_long(decrypted_bytes, 0) >> 20)
        decrypted_block.set_expiration_date(ByteUtil.get_int_long(decrypted_bytes, 0) & 0xFFFFF)
        decrypted_block.set_random_size(ByteUtil.get_int_long(decrypted_bytes, 4))
        return decrypted_block