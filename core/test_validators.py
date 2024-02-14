from django.core.exceptions import ValidationError
from django.test import TestCase

from . import validators

class ValidateColorTests(TestCase):
    def test_allows_w3c_color(self):
        validators.validate_color('olive')
        validators.validate_color('Olive')

    def test_allows_cross_browser_color(self):
        validators.validate_color('blanchedalmond')
        validators.validate_color('BlanchedAlmond')

    def test_does_not_allow_spaces(self):
        with self.assertRaises(ValidationError):
            validators.validate_color('blanched almond')

    def test_allows_3_digit_hex(self):
        validators.validate_color('#C4b')

    def test_allows_6_digit_hex(self):
        validators.validate_color('#B10bb3')

    def test_does_not_allow_wrong_number_of_hex(self):
        with self.assertRaises(ValidationError):
            validators.validate_color('#deadbeef')

    def test_does_not_allox_non_hex_characters(self):
        with self.assertRaises(ValidationError):
            validators.validate_color('#haxxor')
