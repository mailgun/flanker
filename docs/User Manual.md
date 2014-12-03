## User Manual

### Table of Contents

* [Inroduction](#introduction)
* [Address Parsing](#address-parsing)
    * [Parsing](#parsing)
        * [Grammar](#grammar)
        * [Parsing Single Address](#parsing-single-address)
        * [Parsing Address List](#parsing-address-list)
    * [Validating](#validating)
* [MIME Parsing](#mime-parsing)
    * [Rationale](#rationale)
    * [Drawbacks](#drawbacks)
    * [Parsing MIME Messages](#parsing-mime-messages)
    * [Creating MIME Messages](#creating-mime-messages)

### Introduction

Flanker is an open source parsing library written in Python by the Mailgun Team.
Flanker currently consists of an address parsing library (`flanker.addresslib`) as
well as a MIME parsing library (`flanker.mime`).

This document provides an overview of both address parsing and MIME parsing capabilities.

### Address Parsing

`flanker.addresslib` can both parse addresses as well as validate addresses. Parsing
simply consists of parsing the email address based off a context free grammar. Validation
consists of the previous parsing step, but also includes DNS lookups on the domain,
Mail Exchanger (MX) validation, and testing against custom grammar for the particular Email
Service Provider (ESP) if it exists.

#### Parsing

The address parser is an implementation of a recursive descent parser for email addresses
and urls. The grammar supported by the parser (as well as other limitations) are outlined
below. For email addresses, the grammar tries to stick to RFC 5322 as much as possible,
but includes relaxed (lax) grammar as well to support for common realistic uses of email
addresses on the Internet.

##### Grammar

```
address-list     -> address { delimiter address }
mailbox          -> name-addr-rfc | name-addr-lax | addr-spec | url

name-addr-rfc    -> [ display-name-rfc ] angle-addr-rfc
display-name-rfc -> [ whitespace ] word { whitespace word }
angle-addr-rfc   -> [ whitespace ] < addr-spec > [ whitespace ]

name-addr-lax    -> [ display-name-lax ] angle-addr-lax
display-name-lax -> [ whitespace ] word { whitespace word } whitespace
angle-addr-lax   -> addr-spec [ whitespace ]

addr-spec        -> [ whitespace ] local-part @ domain [ whitespace ]
local-part       -> dot-atom | quoted-string
domain           -> dot-atom

word             -> word-ascii | word-unicode
word-ascii       -> atom | quoted-string
word-unicode     -> unicode-alphanum | unicode-qstring
whitespace       -> whitespace-ascii | whitespace-unicode
```

Additional limitations on email addresses:

1. local-part:
    * Must not be greater than 128 octets
2. domain:
    * No more than 127 levels
    * Each level no more than 63 octets
    * Textual representation can not exceed 253 characters
    * No level can begin or end with -
3. Maximum mailbox length is len(local-part) + len('@') + len(domain) which
is 64 + 1 + 253 = 318 characters. Allow 194 characters for a display
name and the (very generous) limit becomes 512 characters. Allow 1024
mailboxes and the total limit on a mailbox-list is 524288 characters.

##### Parsing Single Address

The parser can be used to parse mailboxes, here a mailbox is defined as a
display name as well as a address spec. The parser can parse the entire
mailbox (both display name and address spec) or the address spec alone.

###### Example: Parsing a full mailbox

```python
>>> from flanker.addresslib import address
>>>
>>> address.parse('Foo foo@example.com')
Foo <foo@example.com>
```

###### Example: Parsing the address spec only

```python
>>> from flanker.addresslib import address
>>>
>>> address.parse('foo@example.com', addr_spec_only=True)
foo@example.com
```

###### Example: Parsing an invalid address

```python
>>> from flanker.addresslib import address
>>>
>>> print address.parse('@example.com')
None
```

##### Parsing Address List

The address parser can also be used the parse a list of addresses. When given
a string of email addresses and/or urls separated by a delimiter (comma `,` or
semi-colon `;`), the parser will return returns an iterable list representing
parsed email addresses and urls.

The parser can operate in strict or relaxed modes. In strict mode the parser will
quit at the first occurrence of error and return what has been parsed so far. In
relaxed mode the parser will attempt to seek to to known valid location (the delimiter)
and continue parsing. In relaxed mode the parser can return a tuple representing the
valid parsed addresses and unparsable portions respectively.

###### Example: Parse a list of addresses (relaxed mode)

```python
>>> from flanker.addresslib import address
>>>
>>> address.parse_list('foo@example.com, bar@example.com, @example.com')
[foo@example.com, bar@example.com]
```

###### Example: Parse a list of addresses (relaxed mode)

```python
>>> from flanker.addresslib import address
>>>
>>> address.parse_list('foo@example.com, bar@example.com, @example.com', as_tuple=True)
[foo@example.com, bar@example.com], ['@example.com']
```

###### Example: Parse a list of addresses (strict mode)

```python
>>> from flanker.addresslib import address
>>>
>>> address.parse_list('foo@example.com, bar@example.com, @example.com', strict=True)
[foo@example.com, bar@example.com]
```

#### Validating

Validation includes the parsing steps outlined above, then:

1. **DNS Lookup.** Once an address is parsed, the validator attempts a DNS lookup on the
domain. MX records are checked first, if they don't exist, the validator will fall back to
A records. If neither MX or A records exist, the address is considered invalid.

    By default, `flanker` uses the `dnsq` library (also written by Mailgun) to perform DNS
    lookups, however use of `dnsq` is not required. Any DNS lookup library can be used as
    long as it conforms to the same interface as that of a `dict`. See 
    [flanker/addresslib/drivers/dns_lookup.py](../flanker/addresslib/drivers/dns_lookup.py)
    for an example.

2. **MX Existance.** If the DNS lookup in the previous step returned a valid MX or A record
that address is checked to ensure that a Mail Exchanger responds on port `25`. If no Mail
Exchanger responds, the domain is considered invalid.

    DNS Lookup then Mail Exchanger existence checks are expensive, and the result of the
    above two steps can be cached to improve performance. `flanker` by default uses Redis
    for this cache, but use of Redis is not required. Similar to the DNS lookup library,
    any cache can be used here, as long as the interface as the same as that of a `dict`.
    See [flanker/addresslib/drivers/redis_driver.py](../flanker/addresslib/drivers/redis_driver.py)
    for an example.

3. **Custom Grammar.** Large ESPs rarely if ever support the full grammar that the RFC allows
for email addresses, in fact most have a fairly restrictive grammar. For example, a Yahoo! Mail
address must be between 4-32 characters and can only use alphanum, dot `.` and underscore `_`.
If the mail exchanger in the previous step matches the mail exchanger for a ESP with known
grammar, then the validator will run that additional check on the localpart of the address.

    Custom grammar can be added by adding a plugin for the specific ESP to the
    `flanker/addresslib/plugins` directory. Then update
    [flanker/addresslib/__init__.py](../flanker/addresslib/__init__.py) to include the MX pattern
    for the ESP you wish to add and add it to the `CUSTOM_GRAMMAR_LIST`.

4. **Alternate Suggestion.** A separate, though related step, is spelling correction on the
domain portion of an email address. This can be used to correct common typos like `gmal.com`
instead of `gmail.com`. The spelling corrector uses `difflib` which in turn uses the
[Ratcliff-Obershelp](http://xlinux.nist.gov/dads/HTML/ratcliffObershelp.html) algorithm
to compute the similarity of two strings. This is a very fast and accurate algorithm for
domain spelling correction.

###### Example: Validate a single email address

```python
>>> from flanker.addresslib import address
>>>
>>> address.validate_address('foo@mailgun.com')
foo@mailgun.com
```

###### Example: Validate an address list

```python
>>> from flanker.addresslib import address
>>>
>>> address.validate_list('foo@mailgun.com, bar@mailgun.com, @mailgun.com', as_tuple=True)
([foo@mailgun.com, bar@mailgun.com], ['@mailgun.com'])
```

###### Example: Use the spelling corrector

```python
>>> from flanker.addresslib import validate
>>> validate.suggest_alternate('foo@mailgu.net')
'foo@mailgun.net'
```

###### Example: Use a custom DNS lookup library

```python
>>> import flanker.addresslib
>>> flanker.addresslib.set_dns_lookup(custom_dns_lookup_library)
```

###### Example: Use a custom MX cache

```python
>>> import flanker.addresslib
>>> flanker.addresslib.set_mx_cache(custom_mx_cache_library)
```

### MIME Parsing

`flanker.mime` is a complete MIME handling package for parsing and creating MIME
messages. `flanker.mime` is is faster and more memory efficient than the
standard Python MIME parser. The parser also attempts to preserve encodings when
possible.

#### Rationale

Mailgun parses a lot of MIME, and therefore requires a fast and efficient
MIME handling package. Depending on the MIME message being processed, `flanker.mime`
can be up to **20x faster** than the standard Python MIME parsing package,
use **0.47x the memory**, and make up to **730x fewer function calls**.

Where flanker really shines is header parsing. Flanker doesn't parse the entire
message if you are only interested in the headers, this gives you fast
access to headers if your MIME message is 1 KB or 10 MB.

More details are provided on our [Benchmarking](Benchmarks.md) page.

#### Some more differences

| `email.parser`                           | `flanker.mime`                            |
| ---------------------------------------- | ----------------------------------------- |
| Splits the message into array of lines, then joins them after the parsing. | Stores the message in one string. |
| Does not preserve the original encodings when altering the message. | Converts headers to unicode, detects and preserves encodings when possible. |
| Does not return unchanged parts upon serialization. |Tracks changes and returns unchanged parts unchanged upon serialization. |

#### Drawbacks

If processing a broken MIME message, falls back to `flanker.mime.fallback.FallbackMessage`
which relies on the standard Python parser `email.parser` to fix the broken MIME and
force broken encodings in bodies and headers. However, beware that it
can loose some information because of broken or unknown encodings.

#### Parsing MIME messages

For the following examples, the below MIME messages will be used as examples, they will be
refered to as `message_singlepart` and `message_multipart` respectivly.

**message_singlepart**:
```
MIME-Version: 1.0
Content-Type: text/plain
From: Bob <bob@example.com>
To: Alice <alice@example.com>
Subject: hello, singlepart message
Date: Mon, 16 Sep 2013 12:43:03 -0700

Hello Alice, this is a single part message.
```

**message_multipart**:
```
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary=001a11c1d71697c7f004e6856996
From: Bob <bob@example.com>
To: Alice <alice@example.com>
Subject: hello, multipart message
Date: Mon, 16 Sep 2013 12:43:03 -0700

--001a11c1d71697c7f004e6856996
Content-Type: text/plain; charset=us-ascii

Hello, *Alice*

--001a11c1d71697c7f004e6856996
Content-Type: text/html; charset=us-ascii

<p>Hello, <b>Alice</b></p>

--001a11c1d71697c7f004e6856996--
```

###### Example: Parse MIME messages

```python
>>> from flanker import mime
>>>
>>> msg = mime.from_string(message_string)
```

###### Example: Print all MIME message headers

```python
>>> from flanker import mime
>>>
>>> # parse singlepart message
>>> msg = mime.from_string(message_multipart)
>>> msg.headers.items()
[('Mime-Version', '1.0'),
 ('Content-Type', ('text/plain', {})),
 ('From', 'Bob <bob@example.com>'),
 ('To', 'Alice <alice@example.com>'),
 ('Subject', 'hello, singlepart message'),
 ('Date', 'Mon, 16 Sep 2013 12:43:03 -0700')]
>>>
>>> # parse multipart message
>>> msg = mime.from_string(message_multipart)
>>> msg.headers.items()
[('Mime-Version', '1.0'),
 ('Content-Type',
  ('multipart/alternative', {'boundary': u'001a11c1d71697c7f004e6856996'})),
 ('From', 'Bob <bob@example.com>'),
 ('To', 'Alice <alice@example.com>'),
 ('Subject', 'hello, world'),
 ('Date', 'Mon, 16 Sep 2013 12:43:03 -0700')]
```

###### Example: Find the content_type with predicates

```python
>>> from flanker import mime
>>>
>>> # parse the singlepart message
>>> msg = mime.from_string(message_singlepart)
>>> msg.content_type.is_singlepart()
True
>>> msg.content_type.is_multipart()
False
>>>
>>> # parse the multipart message
>>> msg = mime.from_string(message_multipart)
>>> msg.content_type.is_singlepart()
False
>>> msg.content_type.is_multipart()
True
```

###### Example: Decode the body of a message

```python
>>> from flanker import mime
>>>
>>> # parse singlepart message
>>> msg = mime.from_string(message_singlepart)
>>> msg.body
u'Hello Alice, this is a single part message.\n'
>>>
>>> # parse multipart message
>>> msg = mime.from_string(message_multipartpart)
>>> for part in msg.parts:
       print 'Content-Type: {} Body: {}'.format(part, part.body)

Content-Type: (text/plain) Body: Hello, *Alice*
Content-Type: (text/html) Body: <p>Hello, <b>Alice</b></p>
```

###### Example: Miscellaneous message properties

```python
>>> from flanker import mime
>>>
>>> # parse singlepart message
>>> msg = mime.from_string(message_singlepart)
>>> msg.content_type
('text/plain', {})
>>> msg.content_encoding
('7bit', {})
>>> msg.charset
'ascii'
>>> msg.subject
'hello, singlepart message'
>>>
>>> # parse multipart message
>>> msg = mime.from_string(message_multipartpart)
>>> msg.content_type
('multipart/alternative', {'boundary': u'001a11c1d71697c7f004e6856996'})
>>> msg.content_encoding
('7bit', {})
>>> msg.charset
'ascii'
>>> msg.subject
'hello, multipart message'
```

#### Creating MIME messages

###### Example: Create simple singlepart message

```python
>>> from flanker.mime import create
>>>
>>> message = create.text("plain", "hello, world")
>>> message.headers['From'] = u'Alice <alice@example.com>'
>>> message.headers['To'] = u'Bob <bob@example.com>'
>>> message.headers['Subject'] = u"hey"
>>> message = create.from_string(message.to_string())
>>> print message.to_string()
Mime-Version: 1.0
Content-Type: text/plain; charset="ascii"
From: Alice <alice@example.com>
To: Bob <bob@example.com>
Subject: hey
Content-Transfer-Encoding: 7bit

hello, world
```

###### Example: Create simple multipart message

```python
>>> from flanker.mime import create
>>>
>>> message = create.multipart("mixed")
>>> message.headers['From'] = u'Alice <alice@example.com>'
>>> message.headers['To'] = u'Bob <bob@example.com>'
>>> message.headers['Subject'] = u"hey"
>>> message.append(
   create.text("plain", "hello, world"),
   create.text("html", "<html>hello, world</html>"))
>>> print message.to_string()
Content-Type: multipart/mixed; boundary="4061c73ddfd74b2fbd8e67d386408bc1"
Mime-Version: 1.0
From: Alice <alice@example.com>
To: Bob <bob@example.com>
Subject: hey

--4061c73ddfd74b2fbd8e67d386408bc1
Mime-Version: 1.0
Content-Type: text/plain; charset="ascii"
Content-Transfer-Encoding: 7bit

hello, world
--4061c73ddfd74b2fbd8e67d386408bc1
Mime-Version: 1.0
Content-Type: text/html; charset="ascii"
Content-Transfer-Encoding: 7bit

<html>hello, world</html>
--4061c73ddfd74b2fbd8e67d386408bc1--
```

###### Example: Create multipart message with attachment

This example assumes you have a file on your disk called `hi.png`.

```python
>>> from flanker.mime import create
>>>
>>> message = create.multipart("mixed")
>>> message.headers['From'] = u'Alice <alice@example.com>'
>>> message.headers['To'] = u'Bob <bob@example.com>'
>>> message.headers['Subject'] = u"hey"
>>> filename = "hi"
>>> attach_file = open('hi.png').read()
>>> message.append(
       create.text("plain", "hello, world"),
       create.text("html", "<html>hello, world</html>"),
       create.binary(
          "image", "png", attach_file,
           filename, "attachment"))
>>> print message.to_string()
Content-Type: multipart/mixed; boundary="98f09b51060d48ecbdc780ffc1a66219"
Mime-Version: 1.0
From: Alice <alice@example.com>
To: Bob <bob@example.com>
Subject: hey

--98f09b51060d48ecbdc780ffc1a66219
Mime-Version: 1.0
Content-Type: text/plain; charset="ascii"
Content-Transfer-Encoding: 7bit

hello, world
--98f09b51060d48ecbdc780ffc1a66219
Mime-Version: 1.0
Content-Type: text/html; charset="ascii"
Content-Transfer-Encoding: 7bit

<html>hello, world</html>
--98f09b51060d48ecbdc780ffc1a66219
Mime-Version: 1.0
Content-Type: image/png; charset="ascii"; name="hi"
Content-Disposition: attachment; filename="hi"
Content-Transfer-Encoding: base64

iVBORw0KGgoAAAANSUhEUgAAAAcAAAAGCAYAAAAPDoR2AAAALklEQVQI12P8////fwYcgImBgYGB
kZERRRDGZ8KmA2YYE7JqmA4MndisZsTnIADHtg4MwlUWUgAAAABJRU5ErkJggg==
--98f09b51060d48ecbdc780ffc1a66219--
```

###### Example: Create multipart nested message

```python
>>> from flanker.mime import create
>>>
>>> message = create.multipart("mixed")
>>> nested = create.multipart("alternative")
>>> nested.append(
    create.text("plain", u"hello, world"),
    create.text("html", u"<html>hello, world</html>"))
>>> message.append(
    create.text("plain", "goodbye"),
    nested)
>>> message2 = create.from_string(message.to_string())
>>> print message2.to_string()
Content-Type: multipart/mixed; boundary="e171233d2cf24767b020b410eb0024a8"
Mime-Version: 1.0

--e171233d2cf24767b020b410eb0024a8
Mime-Version: 1.0
Content-Type: text/plain; charset="ascii"
Content-Transfer-Encoding: 7bit

goodbye
--e171233d2cf24767b020b410eb0024a8
Content-Type: multipart/alternative; boundary="81690f11390b4d9f8d74c092183507f4"
Mime-Version: 1.0

--81690f11390b4d9f8d74c092183507f4
Mime-Version: 1.0
Content-Type: text/plain; charset="ascii"
Content-Transfer-Encoding: 7bit

hello, world
--81690f11390b4d9f8d74c092183507f4
Mime-Version: 1.0
Content-Type: text/html; charset="ascii"
Content-Transfer-Encoding: 7bit

<html>hello, world</html>
--81690f11390b4d9f8d74c092183507f4--

--e171233d2cf24767b020b410eb0024a8--
```

###### Example: Create enclosed message

```python
>>> from flanker.mime import create
>>>
>>> message = create.text("plain", u"hello, world")
>>> message.headers['From'] = u'Alice <alice@example.com>'
>>> message.headers['To'] = u'Bob <bob@example.com>'
>>> message.headers['Subject'] = u"hi"
>>> message = create.message_container(message)
>>> message2 = create.from_string(message.to_string())
>>> print message2.to_string()
Content-Type: message/rfc822
Mime-Version: 1.0

Mime-Version: 1.0
Content-Type: text/plain; charset="ascii"
From: Alice <alice@example.com>
To: Bob <bob@example.com>
Subject: hi
Content-Transfer-Encoding: 7bit

hello, world
```

###### Example: Create enclosed nested message

```python
>>> from flanker.mime import create
>>>
>>> nested = create.multipart("alternative")
>>> nested.append(
    create.text("plain", u"hello, world"),
    create.text("html", u"<html>hello, world</html>"))
>>> message = create.multipart("mailgun-recipient-variables")
>>> variables = {"name": u"<b>Alice</b>"}
>>> message.append(
    create.binary("application", "json", json.dumps(variables)),
    create.message_container(nested))
>>> message2 = create.from_string(message.to_string())
>>> print message2.to_string()
Content-Type: multipart/mailgun-recipient-variables; boundary="13f551bddf2e4759b125f70674288048"
Mime-Version: 1.0

--13f551bddf2e4759b125f70674288048
Mime-Version: 1.0
Content-Type: application/json; charset="ascii"
Content-Transfer-Encoding: base64

eyJuYW1lIjogIjxiPkFsaWNlPC9iPiJ9
--13f551bddf2e4759b125f70674288048
Content-Type: message/rfc822
Mime-Version: 1.0

Content-Type: multipart/alternative; boundary="9b7c73fe7191458f8757e26dacffc966"
Mime-Version: 1.0

--9b7c73fe7191458f8757e26dacffc966
Mime-Version: 1.0
Content-Type: text/plain; charset="ascii"
Content-Transfer-Encoding: 7bit

hello, world
--9b7c73fe7191458f8757e26dacffc966
Mime-Version: 1.0
Content-Type: text/html; charset="ascii"
Content-Transfer-Encoding: 7bit

<html>hello, world</html>
--9b7c73fe7191458f8757e26dacffc966--

--13f551bddf2e4759b125f70674288048--
```
