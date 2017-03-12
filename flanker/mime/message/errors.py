class MimeError(Exception):
    pass


class DecodingError(MimeError):
    """Thrown when there is an encoding error."""

    def __str__(self):
        return self.message[:256]


class EncodingError(MimeError):
    """Thrown when there is an decoding error."""

    def __str__(self):
        return self.message[:256]

class DecodingDataCorruptionError(MimeError):

    def __str__(self):
        return self.message[:256]
