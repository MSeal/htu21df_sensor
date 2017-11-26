# This import fixes sys.path issues
from . import parentpath

import unittest
import sys
import time
from mock import patch, MagicMock
from .fakebus import FakeBus
from htu21 import (
    HTU21,
    HTU21DF_READ_TEMP_NO_HOLD,
    HTU21DF_READ_HUM_NO_HOLD,
    HTU21DF_READ_REG,
    HTU21DF_RESET,
    HTU21DF_RESET_REG_VALUE
)

python_2 = sys.version_info[0] == 2

@patch('time.sleep', return_value=None)
class HTUTest(unittest.TestCase):
    def decoded_values(self, values):
        return [chr(v) if python_2 else chr(v).encode('charmap') for v in values]

    @patch('fcntl.ioctl')
    @patch('htu21.rawi2c.open', FakeBus)
    @patch('os.access', return_value=True)
    def setUp(self, *mocks):
        self.htu = HTU21(False)
        self.fake_bus = self.htu.i2c._fd
        self.fake_bus.add_read_byte(HTU21DF_RESET_REG_VALUE)
        self.htu.start_sensor()
        self.fake_bus.clear_buffers()

    def test_reset(self, patched_sleep):
        self.fake_bus.add_read_byte(HTU21DF_RESET_REG_VALUE)
        self.htu.reset()
        self.assertEqual(self.fake_bus.write_array, self.decoded_values([HTU21DF_RESET, HTU21DF_READ_REG]))
        patched_sleep.assert_called_once_with(0.015)

    def test_start_sensor(self, patched_sleep):
        self.htu.reset = MagicMock()
        self.htu.start_sensor()
        self.htu.reset.assert_called_once()
        self.assertEqual(self.fake_bus.write_array, [])

    def test_read_temperature(self, patched_sleep):
        self.fake_bus.add_many_read_bytes([104, 112, 154])
        t = self.htu.read_temperature()
        self.assertEqual(self.fake_bus.write_array, self.decoded_values([HTU21DF_READ_TEMP_NO_HOLD]))
        self.assertAlmostEqual(t, 24.84, 2)
        patched_sleep.assert_called_once_with(0.05)

    def test_read_temperature_chechsum_failure(self, patched_sleep):
        self.fake_bus.add_many_read_bytes([104, 112, 255]) # Bad bytes
        self.fake_bus.add_read_byte(HTU21DF_RESET_REG_VALUE) # Reset on bad read
        self.fake_bus.add_many_read_bytes([104, 112, 154]) # Good bytes
        t = self.htu.read_temperature()
        self.assertEqual(self.fake_bus.write_array, self.decoded_values([HTU21DF_READ_TEMP_NO_HOLD, HTU21DF_RESET, HTU21DF_READ_REG, HTU21DF_READ_TEMP_NO_HOLD]))
        self.assertAlmostEqual(t, 24.84, 2)

    def test_humidity(self, patched_sleep):
        self.fake_bus.add_many_read_bytes([126, 106, 54])
        h = self.htu.read_humidity()
        self.assertEqual(self.fake_bus.write_array, self.decoded_values([HTU21DF_READ_HUM_NO_HOLD]))
        self.assertAlmostEqual(h, 55.73, 2)
        patched_sleep.assert_called_once_with(0.016)

    def test_read_temperature_chechsum_failure(self, patched_sleep):
        self.fake_bus.add_many_read_bytes([126, 106, 255]) # Bad bytes
        self.fake_bus.add_read_byte(HTU21DF_RESET_REG_VALUE) # Reset on bad read
        self.fake_bus.add_many_read_bytes([126, 106, 54]) # Good bytes
        h = self.htu.read_humidity()
        self.assertEqual(self.fake_bus.write_array, self.decoded_values([HTU21DF_READ_HUM_NO_HOLD, HTU21DF_RESET, HTU21DF_READ_REG, HTU21DF_READ_HUM_NO_HOLD]))
        self.assertAlmostEqual(h, 55.73, 2)
