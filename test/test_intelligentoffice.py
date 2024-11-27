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

    @patch.object(GPIO, "input")
    @patch.object(IntelligentOffice, "change_servo_angle")
    @patch.object(SDL_DS3231, "read_datetime")
    def test_should_not_open_blinds_if_sunday(self, mock_time_of_day: Mock, mock_servo: Mock, mock_distance_sensor: Mock):
        mock_distance_sensor.side_effect = [True, False, False, False]
        d = datetime(2024, 12, 1, 8, 0)
        mock_time_of_day.return_value = d
        system = IntelligentOffice()
        system.manage_blinds_based_on_time()
        mock_servo.assert_called_with(2)
        self.assertFalse(system.blinds_open)

    @patch.object(GPIO, "input")
    @patch.object(VEML7700, "lux", new_callable=PropertyMock)
    @patch.object(GPIO, "output")
    def test_should_turn_on_light(self, mock_light: Mock, mock_light_sensor: Mock, mock_distance_sensor: Mock):
        mock_distance_sensor.side_effect = [True, False, False, False]
        mock_light_sensor.return_value = 499
        system = IntelligentOffice()
        system.manage_light_level()
        mock_light.assert_called_with(system.LED_PIN, True)
        self.assertTrue(system.light_on)

    @patch.object(GPIO, "input")
    @patch.object(VEML7700, "lux", new_callable=PropertyMock)
    @patch.object(GPIO, "output")
    def test_should_turn_off_light(self, mock_light: Mock, mock_light_sensor: Mock, mock_distance_sensor: Mock):
        mock_distance_sensor.side_effect = [True, False, False, False]
        mock_light_sensor.return_value = 551
        system = IntelligentOffice()
        system.manage_light_level()
        mock_light.assert_called_with(system.LED_PIN, False)
        self.assertFalse(system.light_on)

    @patch.object(GPIO, "input")
    @patch.object(VEML7700, "lux", new_callable=PropertyMock)
    @patch.object(GPIO, "output")
    def test_should_not_turn_on_light_if_office_empty(self, mock_light: Mock, mock_light_sensor: Mock, mock_distance_sensor:Mock):
        mock_distance_sensor.side_effect = [False, False, False, False]
        mock_light_sensor.return_value = 400
        system = IntelligentOffice()
        system.manage_light_level()
        mock_light.assert_called_with(system.LED_PIN, False)
        self.assertFalse(system.light_on)

    @patch.object(GPIO, "output")
    @patch.object(GPIO, "input")
    def test_should_turn_on_buzzer_if_smoke_detected(self, mock_smoke_detector: Mock, mock_buzzer: Mock):
        mock_smoke_detector.return_value = True
        system = IntelligentOffice()
        system.monitor_air_quality()
        mock_buzzer.assert_called_with(system.BUZZER_PIN, True)
        self.assertTrue(system.buzzer_on)

    @patch.object(GPIO, "output")
    @patch.object(GPIO, "input")
    def test_should_turn_off_buzzer_if_no_smoke_detected(self, mock_smoke_detector: Mock, mock_buzzer: Mock):
        mock_smoke_detector.return_value = False
        system = IntelligentOffice()
        system.monitor_air_quality()
        mock_buzzer.assert_called_with(system.BUZZER_PIN, False)
        self.assertFalse(system.buzzer_on)


