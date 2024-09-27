import base64

class Decryptor:
    def __init__(self, key):
        self.key_bytes = base64.b64decode(key)

    def decrypt(self, data):
        result = bytearray(len(data))
        key_length = len(self.key_bytes)

        for i in range(len(data)):
            result[i] = data[i] ^ self.key_bytes[i % key_length]

        return bytes(result)