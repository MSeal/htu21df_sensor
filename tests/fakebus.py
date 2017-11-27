from htu21.rawi2c import any_py_bytes

class FakeBus(object):
    def __init__(self, *args, **kwargs):
        self.open()
        self.clear_buffers()

    def clear_buffers(self):
        self.write_array = []
        self.read_array = []

    def add_read_byte(self, value):
        self.read_array.append(any_py_bytes(value))

    def add_many_read_bytes(self, values):
        for val in values:
            self.add_read_byte(val)

    def write(self, byte):
        if not self.connected:
            raise IOError('Device is disconnected')
        self.write_array.append(byte)

    def read_byte(self):
        if not self.connected:
            raise IOError('Device is disconnected')
        if not self.read_array:
            raise IOError('No readable values available')
        return self.read_array.pop(0)

    def read(self, num_bytes=1):
        return ''.join(self.read_byte().decode('charmap') for _ in range(num_bytes))

    def close(self):
        self.connected = False

    def open(self):
        self.connected = True
