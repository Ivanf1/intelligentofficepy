import unittest
from datetime import datetime
from unittest.mock import patch, Mock, PropertyMock
import mock.GPIO as GPIO
from mock.SDL_DS3231 import SDL_DS3231
from mock.adafruit_veml7700 import VEML7700
from src.intelligentoffice import IntelligentOffice, IntelligentOfficeError


class TestIntelligentOffice(unittest.TestCase):

    @patch.object(GPIO, "input")
    def test_check_occupancy(self, mock_distance_sensor: Mock):
        mock_distance_sensor.return_value = True
        system = IntelligentOffice()
        occupied = system.check_quadrant_occupancy(system.INFRARED_PIN1)
        self.assertTrue(occupied)

    def test_check_occupancy_raises_error(self):
        system = IntelligentOffice()
        self.assertRaises(IntelligentOfficeError, system.check_quadrant_occupancy, -1)

    @patch.object(IntelligentOffice, "change_servo_angle")
    @patch.object(SDL_DS3231, "read_datetime")
    def test_should_open_blinds(self, mock_time_of_day: Mock, mock_servo: Mock):
        d = datetime(2024, 11, 27, 8, 0)
        mock_time_of_day.return_value = d
        system = IntelligentOffice()
        system.manage_blinds_based_on_time()
        mock_servo.assert_called_with(12)
        self.assertTrue(system.blinds_open)

    @patch.object(IntelligentOffice, "change_servo_angle")
    @patch.object(SDL_DS3231, "read_datetime")
    def test_should_close_the_blinds(self, mock_time_of_day: Mock, mock_servo: Mock):
        d = datetime(2024, 11, 27, 20, 0)
        mock_time_of_day.return_value = d
        system = IntelligentOffice()
        system.manage_blinds_based_on_time()
        mock_servo.assert_called_with(2)
        self.assertFalse(system.blinds_open)

    @patch.object(IntelligentOffice, "change_servo_angle")
    @patch.object(SDL_DS3231, "read_datetime")
    def test_should_not_open_blinds_if_saturday(self, mock_time_of_day: Mock, mock_servo: Mock):
        d = datetime(2024, 11, 30, 8, 0)
        mock_time_of_day.return_value = d
        system = IntelligentOffice()
        system.manage_blinds_based_on_time()
        mock_servo.assert_called_with(2)
        self.assertFalse(system.blinds_open)
