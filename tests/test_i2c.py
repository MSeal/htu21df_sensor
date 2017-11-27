# This import fixes sys.path issues
from . import parentpath

import unittest
import sys
import fcntl
import array
from mock import patch
from .fakebus import FakeBus
from htu21.rawi2c import I2C, CRC8Error, bus_path, available_bus, array_to_int, crc8check, any_py_bytes

python_2 = sys.version_info[0] == 2

class I2CUtils(unittest.TestCase):
    def test_bus_path(self):
        self.assertEqual(bus_path(0), "/dev/i2c-0")
        self.assertEqual(bus_path(2), "/dev/i2c-2")
        self.assertEqual(bus_path('3'), "/dev/i2c-3")

    @patch('os.access', return_value=False)
    def test_available_bus_no_devices(self, *mocks):
        self.assertRaises(IOError, available_bus)

    @patch('os.access', side_effect=[False, False, True])
    def test_available_bus_no_devices(self, access_mock):
        self.assertEqual(available_bus(), 2)

    def test_array_to_int(self):
        self.assertEqual(array_to_int([1, 255, 56], True), 130872)
        self.assertEqual(array_to_int([1, 255, 56], False), 3735297)
        self.assertEqual(array_to_int([], False), 0)

    def test_crc8check(self):
        self.assertTrue(crc8check([104, 124, 231], True))
        self.assertTrue(crc8check([231, 124, 104], False))
        self.assertTrue(crc8check([125, 194, 94], True))
        self.assertTrue(crc8check([94, 194, 125], False))

        self.assertFalse(crc8check([104, 124, 232], True))
        self.assertFalse(crc8check([231, 124, 105], False))
        self.assertFalse(crc8check([0, 194, 94], True))
        self.assertFalse(crc8check([94, 94, 125], False))

class I2CTest(unittest.TestCase):
    @patch('fcntl.ioctl')
    @patch('htu21.rawi2c.open', FakeBus)
    @patch('os.access', return_value=True)
    def setUp(self, *mocks):
        self.i2c = I2C(1)
        self.fake_bus = self.i2c._fd

    def test_read_basics(self):
        values = map(any_py_bytes, 'test')
        self.fake_bus.add_many_read_bytes(values)
        self.assertEqual(self.i2c.read(), b't')
        self.assertEqual(self.i2c.read(), b'e')
        self.assertEqual(self.i2c.read(), b's')
        self.assertEqual(self.i2c.read(), b't')
        self.assertRaises(IOError, self.i2c.read)

    def test_read_many_basics(self):
        values = list(map(any_py_bytes, [52, 21]))
        self.fake_bus.add_many_read_bytes(values)
        self.assertEqual(list(map(any_py_bytes, self.i2c.read_many(2))), values)
        self.fake_bus.add_many_read_bytes(values)
        # Endianess is only used for crc
        self.assertEqual(list(map(any_py_bytes, self.i2c.read_many(2, False))), values)
        self.assertRaises(IOError, self.i2c.read_many, 2)

    def test_read_many_crc(self):
        values = list(map(any_py_bytes, [104, 124]))
        checksum = 231
        payload = list(map(any_py_bytes, values + [checksum]))
        self.fake_bus.add_many_read_bytes(payload)
        self.assertEqual(list(map(any_py_bytes, self.i2c.read_many(2, True, True))), values)
        self.fake_bus.add_many_read_bytes(reversed(payload))
        self.assertEqual(list(map(any_py_bytes, self.i2c.read_many(2, False, True))), list(map(any_py_bytes, reversed(values))))
        self.fake_bus.add_many_read_bytes(map(any_py_bytes, [255, 124, checksum]))
        self.assertRaises(CRC8Error, self.i2c.read_many, 2, True, True)

    def test_read_int(self):
        values = list(map(any_py_bytes, [52, 21]))
        self.fake_bus.add_many_read_bytes(values)
        self.assertEqual(self.i2c.read_int(), 52)
        self.assertEqual(self.i2c.read_int(), 21)
        self.fake_bus.add_many_read_bytes(values)
        self.assertEqual(self.i2c.read_int(2), 13333)
        self.fake_bus.add_many_read_bytes(values)
        self.assertEqual(self.i2c.read_int(2, False), 5428)
        self.assertRaises(IOError, self.i2c.read_int, 2)

    def test_read_int_crc(self):
        values = list(map(any_py_bytes, [104, 124]))
        checksum = 231
        payload = list(map(any_py_bytes, values + [checksum]))
        self.fake_bus.add_many_read_bytes(payload)
        self.assertEqual(self.i2c.read_int(2, True, True), 26748)
        self.fake_bus.add_many_read_bytes(reversed(payload))
        self.assertEqual(self.i2c.read_int(2, False, True), 26748)
        self.fake_bus.add_many_read_bytes(map(any_py_bytes, [255, 124, checksum]))
        self.assertRaises(CRC8Error, self.i2c.read_many, 2, True, True)

    def test_write_basics(self):
        self.i2c.write(chr(54))
        self.assertEqual(self.fake_bus.write_array[-1], chr(54).encode('charmap'))
        self.i2c.write(54)
        self.assertEqual(self.fake_bus.write_array[-1], chr(54).encode('charmap'))
        self.i2c.write('54')
        self.assertEqual(self.fake_bus.write_array[-1], b'54')

    @patch('fcntl.ioctl')
    def test_set_address(self, mock_ioctl):
        new_addr = 20
        self.i2c.set_address(new_addr)
        self.assertEqual(self.i2c.addr, new_addr)
        mock_ioctl.assert_called_once_with(self.fake_bus, I2C.I2C_SLAVE, new_addr)
