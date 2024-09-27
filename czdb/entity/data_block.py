import msgpack

class DataBlock:
    def __init__(self, region, data_ptr):
        self.region = region
        self.data_ptr = data_ptr

    def get_region(self, geo_map_data, column_selection):
        try:
            return self.unpack(geo_map_data, column_selection)
        except Exception:
            return None

    def set_region(self, region):
        self.region = region
        return self

    def get_data_ptr(self):
        return self.data_ptr

    def set_data_ptr(self, data_ptr):
        self.data_ptr = data_ptr
        return self

    def unpack(self, geo_map_data, column_selection):
        unpacker = msgpack.Unpacker()
        unpacker.feed(self.region)
        geo_pos_mix_size = unpacker.unpack()
        other_data = unpacker.unpack()

        if geo_pos_mix_size == 0:
            return other_data

        data_len = (geo_pos_mix_size >> 24) & 0xFF
        data_ptr = geo_pos_mix_size & 0x00FFFFFF

        region_data = geo_map_data[data_ptr:data_ptr + data_len]
        sb = []

        unpacker = msgpack.Unpacker()
        unpacker.feed(region_data)
        columns = unpacker.unpack()

        for i, column in enumerate(columns):
            column_selected = (column_selection >> (i + 1) & 1) == 1
            column = "null" if column == "" else column

            if column_selected:
                sb.append(column + "\t")

        return "".join(sb) + other_data