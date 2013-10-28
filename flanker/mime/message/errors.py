class MimeError(Exception):
    pass

class DecodingError(MimeError):
    """Thrown when there is an encoding error."""
    pass

class EncodingError(MimeError):
    """Thrown when there is an decoding error."""
    pass
