from django.test import TestCase

from . import images

class ApplyCropTests(TestCase):
    def test_apply_top(self):
        crop = images.ImageCrop(
            image_width=5,
            image_height=200,
            x0=2,
            x1=4,
            y0=34,
            y1=134,
        )

        self.assertEqual(crop.apply_top, -34)

    def test_apply_left(self):
        crop = images.ImageCrop(
            image_width=200,
            image_height=5,
            x0=34,
            x1=134,
            y0=2,
            y1=4,
        )

        self.assertEqual(crop.apply_left, -34)

    def test_apply_width(self):
        crop = images.ImageCrop(
            image_width=300,
            image_height=5,
            x0=17,
            x1=167,
            y0=2,
            y1=4,
        )

        self.assertEqual(crop.apply_width, 200)

    def test_apply_height(self):
        crop = images.ImageCrop(
            image_width=5,
            image_height=300,
            x0=2,
            x1=4,
            y0=17,
            y1=167,
        )

        self.assertEqual(crop.apply_height, 200)

class ShowCropTests(TestCase):
    def test_show_top(self):
        crop = images.ImageCrop(
            image_width=5,
            image_height=300,
            x0=2,
            x1=4,
            y0=75,
            y1=167,
        )

        self.assertEqual(crop.show_top, 25)

    def test_show_left(self):
        crop = images.ImageCrop(
            image_width=300,
            image_height=5,
            x0=75,
            x1=167,
            y0=2,
            y1=4,
        )

        self.assertEqual(crop.show_left, 25)

    def test_show_width(self):
        crop = images.ImageCrop(
            image_width=300,
            image_height=5,
            x0=17,
            x1=167,
            y0=2,
            y1=4,
        )

        self.assertEqual(crop.show_width, 50)

    def test_show_height(self):
        crop = images.ImageCrop(
            image_width=5,
            image_height=300,
            x0=2,
            x1=4,
            y0=17,
            y1=167,
        )

        self.assertEqual(crop.show_height, 50)
