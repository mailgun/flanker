flanker
=======

Flanker is an open source parsing library written in Python by the Mailgun Team.
Flanker currently consists of an address parsing library (`flanker.addresslib`) as
well as a MIME parsing library (`flanker.mime`).

Detailed documentation is provided in the [User Manual](docs/User Manual.md) as well as the
[API Reference](docs/API Reference.md). A Quickstart Guide is provided below.

## Quickstart Guide

### Address Parsing

To parse a single mailbox (display name as well as email address):

```python
>>> from flanker.addresslib import address
>>>
>>> address.parse('Foo foo@example.com')
Foo <foo@example.com>
```

An invalid address is returned as `None`:

```python
>>> from flanker.addresslib import address
>>>
>>> print address.parse('@example.com')
None
```

To parse a single email address (no display name):

```python
>>> from flanker.addresslib import address
>>>
>>> address.parse('foo@example.com', True)
foo@example.com
```

To parse an address list (Note: `parse_list` returns a tuple containing the parsed 
addresses and the unparsable portions):

```python
>>> from flanker.addresslib import address
>>>
>>> address.parse_list('foo@example.com, bar@example.com, @example.com')
([foo@example.com, bar@example.com], ['@example.com'])
```

To parse an address list in strict mode (stop at the first failure):

```python
>>> from flanker.addresslib import address
>>>
>>> address.parse_list('foo@example.com, bar@example.com, @example.com', True)
[foo@example.com, bar@example.com]
```

To validate an email address (parse as well as DNS, MX existence, and ESP grammar checks):

```python
>>> from flanker.addresslib import address
>>>
>>> address.validate_address('foo@mailgun.com')
foo@mailgun.com
```

To validate an address list:

```python
>>> from flanker.addresslib import address
>>>
>>> address.validate_list('foo@mailgun.com, bar@mailgun.com, @mailgun.com')
([foo@mailgun.com, bar@mailgun.com], ['@mailgun.com'])
```

### MIME Parsing

For the following examples, `message_string` will be set to the following MIME message:

```
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary=001a11c1d71697c7f004e6856996
From: Bob <bob@example.com>
To: Alice <alice@example.com>
Subject: hello, world
Date: Mon, 16 Sep 2013 12:43:03 -0700

--001a11c1d71697c7f004e6856996
Content-Type: text/plain; charset=us-ascii

Hello, *Alice*

--001a11c1d71697c7f004e6856996
Content-Type: text/html; charset=us-ascii

<p>Hello, <b>Alice</b></p>

--001a11c1d71697c7f004e6856996--
```

To parse a MIME message:

```python
>>> from flanker import mime
>>>
>>> msg = mime.from_string(message_string)
```

MIME message headers (unicode multi-value dictionary with headers):

```python
>>> from flanker import mime
>>>
>>> msg = mime.from_string(message_string)
>>> msg.headers.items()
[('Mime-Version', '1.0'),
 ('Content-Type',
  ('multipart/alternative', {'boundary': u'001a11c1d71697c7f004e6856996'})),
 ('From', 'Bob <bob@example.com>'),
 ('To', 'Alice <alice@example.com>'),
 ('Subject', 'hello, world'),
 ('Date', 'Mon, 16 Sep 2013 12:43:03 -0700')]
```

Useful content_type member with predicates:

```python
>>> from flanker import mime
>>> msg = mime.from_string(message_string)
>>>
>>> msg.content_type.is_multipart()
True
>>>
>>> msg.content_type.is_singlepart()
False
>>>
>>> msg.content_type.is_message_container()
False 
```

Decoded body of a message:

```python
>>> from flanker import mime
>>> msg = mime.from_string(message_string)
>>>
>>> # None because message is multipart
>>> print msg.body
None
>>>
>>> for part in msg.parts:
       print 'Content-Type: {} Body: {}'.format(part, part.body)

Content-Type: (text/plain) Body: Hello, *Alice*
Content-Type: (text/html) Body: <p>Hello, <b>Alice</b></p>

>>> # None because no enclosed messages exist
>>> print msg.enclosed
None
```
