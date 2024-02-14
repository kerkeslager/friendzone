from collections import namedtuple

_ImageCrop = namedtuple(
    'ImageCrop',
    (
        'image_width',
        'image_height',
        'x0',
        'x1',
        'y0',
        'y1',
    ),
)

class ImageCrop(_ImageCrop):
    @property
    def crop_width(self):
        return self.x1 - self.x0

    @property
    def crop_height(self):
        return self.y1 - self.y0

    @property
    def apply_left(self):
        return -100 * self.x0 / self.crop_width

    @property
    def apply_top(self):
        return -100 * self.y0 / self.crop_height

    @property
    def apply_width(self):
        return 100 * self.image_width / self.crop_width

    @property
    def apply_height(self):
        return 100 * self.image_height / self.crop_height

    @property
    def show_left(self):
        return 100 * self.x0 / self.image_width

    @property
    def show_top(self):
        return 100 * self.y0 / self.image_height

    @property
    def show_width(self):
        return 100 * self.crop_width / self.image_width

    @property
    def show_height(self):
        return 100 * self.crop_height / self.image_height
