.. image:: https://drone.io/github.com/mailgun/flanker/status.png

*******
Flanker
*******

Flanker is an open source parsing library written in Python by the Mailgun Team.
Flanker currently consists of an address parsing library (`flanker.addresslib`) as
well as a MIME parsing library (`flanker.mime`).

Detailed documentation is provided in the `User Manual <https://github.com/mailgun/flanker/blob/master/docs/User%20Manual.md>`_ as well as the
`API Reference <https://github.com/mailgun/flanker/blob/master/docs/API%20Reference.md>`_. A Quickstart Guide is provided below.

Quickstart Guide
################

Installing
**********

**Flanker was built and tested with Python 2.7.2.**

You can install flanker via `pip` or clone the repo from GitHub.

You'll need Python headers files before you start working with flanker, so install them first:

.. code-block:: bash

   # ubuntu 
   sudo apt-get install python-dev
   # fedora 
   sudo yum install python-devel

If you are using `pip`, simply type:


.. code-block:: bash

   pip install flanker

*Note about installing from PyPi. Installing without specifying a version number will
install the latest version from PyPi that does not pin version dependences. This version
of Flanker will most likely work, but is not guaranteed. If you want to run a guaranteed
to work version of Flanker, run the version where we pin dependences, which is one lower
major version number. For example, if the current release is `0.4.4` then the stabled
pinned dependency version is `0.3.4`.*

If you are cloning from GitHub, you can type:

.. code-block:: bash

   git clone git@github.com:mailgun/flanker.git
   cd flanker
   python setup.py install

Address Parsing
***************

To parse a single mailbox (display name as well as email address):

.. code-block:: py

   >>> from flanker.addresslib import address
   >>>
   >>> address.parse('Foo foo@example.com')
   Foo <foo@example.com>

An invalid address is returned as `None`:

.. code-block:: py

   >>> from flanker.addresslib import address
   >>>
   >>> print address.parse('@example.com')
   None

To parse a single email address (no display name):

.. code-block:: py

   >>> from flanker.addresslib import address
   >>>
   >>> address.parse('foo@example.com', addr_spec_only=True)
   foo@example.com

To parse an address list:

.. code-block:: py

   >>> from flanker.addresslib import address
   >>>
   >>> address.parse_list('foo@example.com, bar@example.com, @example.com')
   [foo@example.com, bar@example.com]

To parse an address list as well as return a tuple containing the parsed 
addresses and the unparsable portions

.. code-block:: py

   >>> from flanker.addresslib import address
   >>>
   >>> address.parse_list('foo@example.com, bar@example.com, @example.com', as_tuple=True)
   [foo@example.com, bar@example.com], ['@example.com']

To parse an address list in strict mode:

.. code-block:: py

   >>> from flanker.addresslib import address
   >>>
   >>> address.parse_list('foo@example.com, bar@example.com, @example.com', strict=True)
   [foo@example.com, bar@example.com]

To validate an email address (parse as well as DNS, MX existence, and ESP grammar checks):

.. code-block:: py

   >>> from flanker.addresslib import address
   >>>
   >>> address.validate_address('foo@mailgun.com')
   foo@mailgun.com

To validate an address list:

.. code-block:: py

   >>> from flanker.addresslib import address
   >>>
   >>> address.validate_list('foo@mailgun.com, bar@mailgun.com, @mailgun.com', as_tuple=True)
   ([foo@mailgun.com, bar@mailgun.com], ['@mailgun.com'])

MIME Parsing
************

For the following examples, `message_string` will be set to the following MIME message:

::

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
   
To parse a MIME message:

.. code-block:: py

   >>> from flanker import mime
   >>>
   >>> msg = mime.from_string(message_string)

MIME message headers (unicode multi-value dictionary with headers):

.. code-block:: py

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

Useful content_type member with predicates:

.. code-block:: py

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

Decoded body of a message:

.. code-block:: py

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
