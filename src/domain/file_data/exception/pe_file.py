class ExtractingFileError(Exception):
    __slots__ = ("message",)

    def __init__(self, message: str):
        self.message = message
