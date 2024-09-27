class ByteUtil:
    @staticmethod
    def write(b, offset, v, bytes):
        for i in range(bytes):
            b[offset] = (v >> (8 * i)) & 0xFF
            offset += 1

    @staticmethod
    def write_int_long(b, offset, v):
        b[offset] = (v >> 0) & 0xFF
        b[offset + 1] = (v >> 8) & 0xFF
        b[offset + 2] = (v >> 16) & 0xFF
        b[offset + 3] = (v >> 24) & 0xFF

    @staticmethod
    def get_int_long(b, offset):
        return (
                (b[offset] & 0xFF) |
                ((b[offset + 1] << 8) & 0xFF00) |
                ((b[offset + 2] << 16) & 0xFF0000) |
                ((b[offset + 3] << 24) & 0xFF000000)
        )

    @staticmethod
    def get_int3(b, offset):
        return (
                (b[offset] & 0xFF) |
                ((b[offset + 1] & 0xFF) << 8) |
                ((b[offset + 2] & 0xFF) << 16)
        )

    @staticmethod
    def get_int2(b, offset):
        return (
                (b[offset] & 0xFF) |
                ((b[offset + 1] & 0xFF) << 8)
        )

    @staticmethod
    def get_int1(b, offset):
        return b[offset] & 0xFF