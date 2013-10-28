## API Reference

Below is the public API reference, for details on how to use Flanker (as well as examples) and details on how
its internals work see the [User Manual](User Manual.md).

### Address Parsing

#### Classes

##### EmailAddress

EmailAddress represents a fully parsed email address with built-in support for MIME
encoding. Display names are always returned in Unicode, i.e. ready to be displayed on
web forms.

| Parameter 	   | Type      |  Description                                                                                |
| -------------- | --------- | ------------------------------------------- |
| mailbox 	     | Property  | localpart (part before the `@`)             |
| hostname       | Property  | domain (part after the `@`)                 |
| address        | Property  | Address spec                                |
| display_name   | Property  | Display name                                |
| full_spec()    | Method    | Display name and address.                   |
| to_unicode()   | Method    | Converts display name and address to unicode|


##### UrlAddress

Represents a parsed URL.

| Parameter 	   | Type      |  Description                                                                                |
| -------------- | --------- | ------------------------------------------- |
| address 	     | Property  |                                             |
| hostname       | Property  |                                             |
| port           | Property  | Port of URL, typically 80 for webservices   |
| scheme         | Property  |                                             |
| path           | Property  |                                             |
| full_spec()    | Method    | Full URL.                                   |
| to_unicode()   | Method    | Converts address to unicode                 |


All of the following functions are in the `flanker.addresslib.address` module.

#### Parse Single Address

Parse a single address or URL. Can parse just the address spec or the full mailbox.

```python
parse(address, addr_spec_only=False, strict=False)
```

| Parameter 	   | Description                                                                                |
| -------------- | ------------------------------------------------------------------------------------------ |
| address 	     | An address to parse. (Maximum: 512 characters)                                             |
| addr_spec_only | Boolean to set if only parsing the address, not the display name as well. (Default: False) |
| strict         | Operate parser in strict mode to relaxed mode.                                             |

*Return Value*: An EmailAddress object or None. 

#### Parse Address List

Parse a list of addresses., operates in strict or relaxed modes. Strict
mode will fail at the first instance of invalid grammar, relaxed modes
tries to recover and continue.

```python
parse_list(address_list, strict=False)
```

| Parameter 	   | Description                                                                                         |
| -------------- | --------------------------------------------------------------------------------------------------- |
| address_list   | A delimiter (either `,` or `;`) separated list of addresses. (Maximum: 524288 characters)           |                                            |
| strict | Operate parser in strict (stop at any error) or relaxed (attempt to recover and continue). (Default: False) |
| strict         | Operate parser in strict mode to relaxed mode.                                                      |

*Return Value*: If opearting in strict mode, returns a list of parsed EmailAddress objects. If operating
in relaxed mode, returns a tuple that contains the parsed addresses and unparsable portions.

#### Validate Address

Validates (parse, plus dns, mx check, and custom grammar) a single
address spec. In the case of a valid address returns an EmailAddress
object, otherwise returns None.

```python
validate_address(addr_spec)
```

| Parameter 	   | Description                                                                                |
| -------------- | ------------------------------------------------------------------------------------------ |
| address 	     | An address to parse. (Maximum: 512 characters)                                             |

*Return Value*: An EmailAddress object or None.

#### Validate Address List

Validates an address list, and returns a tuple of parsed and unparsed
portions. Can parse syntax only mode (no dns, mx check, or custom
grammar).

```python
validate_list(addr_list, syntax_only=True)
```

| Parameter 	   | Description                                                                               |
| -------------- | ----------------------------------------------------------------------------------------- |
| address_list   | A delimiter (either `,` or `;`) separated list of addresses. (Maximum: 524288 characters) |                                            |
| syntax_only    | Perform only syntax checks or DNS and ESP specific validation as well. (Default: True)    |

*Return Value*: If operating in strict mode, returns a list of parsed EmailAddress objects. If operating
in relaxed mode, returns a tuple that contains the parsed addresses and unparsable portions.

### MIME Parsing

Classes

All of the following functions are in the `flanker.mime.create` module.

#### Parsing a string into a `MIMEPart` object.

If you are parsing MIME messages, the is the function you should be calling.

```python
from_string(string)
```

| Parameter 	   | Description                                |
| -------------- | ------------------------------------------ |
| string         | The string to parse into a MIMEPart object |

*Return Value*: A MIMEPart object representing the parsed string.

#### Creating a `MIMEPart` object

The following methods are used to create various MIME objects. Examples of how to use them
to create full MIME messages are in the [User Manual](User Manual.md).

##### Create Multipart Message 

Creates an empty multipart MIME message.

```python
multipart(subtype)
```

| Parameter 	   | Description                                |
| -------------- | ------------------------------------------ |
| subtype        | Subtype of message content (second part of `Content-Type`). Common subtypes are `plain`, `html`, `mixed`, `alternative`

*Return Value*: `flanker.mime.message.part.MimePart` object.

##### Create Multipart Message 

Creates a message container.

```python
message_container(message)
```

| Parameter 	   | Description                                |
| -------------- | ------------------------------------------ |
| message        | MIME message                               |

*Return Value*: `flanker.mime.message.part.MimePart` object.

##### Create a MIME text content object

Creates a MIME text content object.

```python
text(subtype, body, charset=None, disposition=None, filename=None)
```

| Parameter 	   | Description                                |
| -------------- | ------------------------------------------ |
| subtype        | Subtype of message content (second part of `Content-Type`). Common subtypes are `plain`, `html`, `mixed`, `alternative`
| body           | The content itself                         |
| charset        | The character set of the message. A common value is `ascii` |
| disposition    | Specifies the presentation style. Common disposition values are `inline` and `attachment` |
| filename       | Name of the file                           |

*Return Value*: `flanker.mime.message.part.MimePart` object.

##### Create a MIME binary content object

Creates a MIME binary content object.

```python
binary(maintype, subtype, body, filename=None, disposition=None, charset=None)
```

| Parameter 	   | Description                                |
| -------------- | ------------------------------------------ |
| maintype       | Type of the message content (first part of `Content-Type`). Common values are `text`, `image`, and `multipart` |                                           |
| subtype        | Subtype of message content (second part of `Content-Type`). Common subtypes are `plain`, `html`, `mixed`, `alternative`
| body           | The content itself                         |
| charset        | The character set of the message. A common value is `ascii` |
| disposition    | Specifies the presentation style. Common disposition values are `inline` and `attachment` |
| filename       | Name of the file                           |

*Return Value*: `flanker.mime.message.part.MimePart` object.

##### Create a MIME attachment content object

Creates a MIME attachment content object.

```python
attachment(content_type, body, filename=None, disposition=None, charset=None)
```

| Parameter 	   | Description                                |
| -------------- | ------------------------------------------ |
| content_type   | Type of the message content. Common values are `text/plain` and `image/png` |
| body           | The content itself                         |
| charset        | The character set of the message. A common value is `ascii` |
| disposition    | Specifies the presentation style. Common disposition values are `inline` and `attachment` |
| filename       | Name of the file                           |

*Return Value*: `flanker.mime.message.part.MimePart` object.
