import base64
from datetime import datetime
from czdb.entity.decrypted_block import DecryptedBlock
from czdb.entity.hyper_header_block import HyperHeaderBlock

class HyperHeaderDecoder:

    @staticmethod
    def decrypt(is_, key):
        # Read the header bytes
        header_bytes = is_.read(HyperHeaderBlock.HEADER_SIZE)

        # Extract version, client_id, and encrypted_block_size
        version = int.from_bytes(header_bytes[0:4], byteorder='little')
        client_id = int.from_bytes(header_bytes[4:8], byteorder='little')
        encrypted_block_size = int.from_bytes(header_bytes[8:12], byteorder='little')

        # Read the encrypted bytes
        encrypted_bytes = is_.read(encrypted_block_size)

        # Decrypt the encrypted bytes
        decrypted_block = DecryptedBlock.decrypt(key, encrypted_bytes)

        # Validate client_id
        if decrypted_block.get_client_id() != client_id:
            raise Exception("Wrong clientId")

        # Validate expiration_date
        current_date = int(datetime.now().strftime("%y%m%d"))
        if decrypted_block.get_expiration_date() < current_date:
            raise Exception("DB is expired")

        # Create and return HyperHeaderBlock instance
        hyper_header_block = HyperHeaderBlock()
        hyper_header_block.set_version(version)
        hyper_header_block.set_client_id(client_id)
        hyper_header_block.set_encrypted_block_size(encrypted_block_size)
        hyper_header_block.set_decrypted_block(decrypted_block)

        return hyper_header_block