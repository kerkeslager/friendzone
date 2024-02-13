from collections import namedtuple

class ImageCrop(namedtuple('ImageCrop', ('original_width', 'original_height', 'x0', 'x1', 'y0', 'y1'))):
    @property
    def left(self):
        return self.x0

    @property
    def right(self):
        return self.x1 - self.original_width

    @property
    def top(self):
        return self.y0

    @property
    def bottom(self):
        return self.y1 - self.original_height

    @property
    def left_percent(self):
        return 100 * self.left // self.original_width

    @property
    def right_percent(self):
        return 100 * self.right // self.original_width

    @property
    def top_percent(self):
        return 100 * self.top // self.original_height

    @property
    def bottom_percent(self):
        return 100 * self.bottom // self.original_height

    @property
    def width(self):
        return self.x1 - self.x0

    @property
    def width_percent(self):
        return 100 * self.width // self.original_width

    @property
    def height(self):
        return self.y1 - self.y0

    @property
    def height_percent(self):
        return 100 * self.height // self.original_height

    @property
    def apply_left(self):
        return -100 * self.left // self.width

    @property
    def apply_top(self):
        return -100 * self.top // self.height

    @property
    def apply_width(self):
        return 100 * self.original_width // self.width

    @property
    def apply_height(self):
        return 100 * self.original_height // self.height
