class HeaderBlock:
    def __init__(self, index_start_ip, index_ptr):
        self.index_start_ip = index_start_ip
        self.index_ptr = index_ptr

    def get_index_start_ip(self):
        return self.index_start_ip

    def set_index_start_ip(self, index_start_ip):
        self.index_start_ip = index_start_ip
        return self

    def get_index_ptr(self):
        return self.index_ptr

    def set_index_ptr(self, index_ptr):
        self.index_ptr = index_ptr
        return self

    def get_bytes(self):
        b = [0] * 20
        for key, value in enumerate(self.index_start_ip):
            if key < 16:
                b[key] = value
        b[16] = (self.index_ptr >> 24) & 0xFF
        b[17] = (self.index_ptr >> 16) & 0xFF
        b[18] = (self.index_ptr >> 8) & 0xFF
        b[19] = self.index_ptr & 0xFF
        return b