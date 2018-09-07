class MimeError(Exception):
    pass


class DecodingError(MimeError):
    """Thrown when there is an encoding error."""

    def __str__(self):
        return MimeError.__str__(self)[:256]


class EncodingError(MimeError):
    """Thrown when there is an decoding error."""

    def __str__(self):
        return MimeError.__str__(self)[:256]
