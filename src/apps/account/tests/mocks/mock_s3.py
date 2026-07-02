class MockS3Uploader:
    """
    Mock que simula o serviço de upload.
    """

    def __init__(self):
        self.upload_called = False
        self.last_filename = None

    def upload(self, file_buffer, filename):
        self.upload_called = True
        self.last_filename = filename

        return filename
