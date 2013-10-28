"""This is complete MIME handling package, provides fast parser
and models for handling mime.

Rationale
--------
* Standard python parser is slow at parsing big messages, it takes ~1 second
and a couple of millions of ops to parse 11MB message.
* Not very memory efficient, as it splits the message into array of lines,
and joins them after the parsing.
* Does not preserve the original encodings when altering the message.

The new parser is:

* Fast, it takes ~50 millisecond and ~2K operations to parse 11 MB message.
* Memory efficient, as it stores the message in one string.
* Tracks changes and returns unchanged parts unchanged upon serialization.
* Converts headers to unicode, detects and preserves encodings when possible.

Parser drawbacks:

* Parser is strict, when the MIME is broken, raises MimeError and does
not attempt to fix anything except simple errors (like mistyped charsets)

Alternatives:

If you still need to process the broken MIME, use flanker.mime.fallback.FallbackMessage
that relies on python parser in terms of fixing the broken MIME and forces broken
encodings in bodies and headers, but beware that it can loose some information because
of broken or unknown encodings.

Examples
-------

>> from flanker import mime
>> msg = mime.from_string(message_string)

# unicode multi-value dictionary with headers
msg.headers

# useful content_type member with predicates:

msg.content_type.is_multipart()
msg.content_type.is_singlepart()
msg.content_type.is_message_container()

#decoded body of the message

if msg.content_type.is_singlepart():
    msg.body

# parts if message is multipart
if msg.content_type.is_multipart():
    msg.parts

# enclosed message
if msg.content_type.is_message_container():
    msg.enclosed

read more in package details.
"""
from flanker.mime.message.errors import DecodingError, EncodingError, MimeError
from flanker.mime import create
from flanker.mime.create import from_string
from flanker.mime.message.fallback.create import from_string as recover
from flanker.mime.message.utils import python_message_to_string
from flanker.mime.message.headers.parametrized import fix_content_type
