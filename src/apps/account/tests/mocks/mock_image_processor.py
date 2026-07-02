class MockImageProcessor:
    def __init__(self):
        self.resize_called = False

    def resize(self, image_file):
        self.resize_called = True
        return image_file
