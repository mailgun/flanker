## API Reference

Below is the public API reference, for details on how to use Flanker (as well as examples) and details on how
its internals work see the [User Manual](User Manual.md).

### Address Parsing

#### Classes

##### EmailAddress

EmailAddress represents a fully parsed email address with built-in support for MIME
encoding. Display names are always returned in Unicode, i.e. ready to be displayed on
web forms.

| Parameter	     | Type      |  Description                                |
| -------------- | --------- | ------------------------------------------- |
| mailbox        | Property  | localpart (part before the `@`)             |
| hostname       | Property  | domain (part after the `@`)                 |
| address        | Property  | Address spec                                |
| display_name   | Property  | Display name                                |
| full_spec()    | Method    | Display name and address. RFC-2822 compliant, safe to be included into MIME |
| to_unicode()   | Method    | Display name and address in unicode         |


##### UrlAddress

Represents a parsed URL.

| Parameter	     | Type      |  Description                                |
| -------------- | --------- | ------------------------------------------- |
| address        | Property  |                                             |
| hostname       | Property  |                                             |
| port           | Property  | Port of URL, typically 80 for webservices   |
| scheme         | Property  |                                             |
| path           | Property  |                                             |
| full_spec()    | Method    | Full URL                                    |
| to_unicode()   | Method    | Converts address to unicode                 |


All of the following functions are in the `flanker.addresslib.address` module.

#### Parse Single Address

Parse a single address or URL. Can parse just the address spec or the full mailbox.

```python
parse(address, addr_spec_only=False)
```

| Parameter	     | Description                                                                                |
| -------------- | ------------------------------------------------------------------------------------------ |
| address        | An address to parse. (Maximum: 512 characters)                                             |
| addr_spec_only | Boolean to set if only parsing the address, not the display name as well. (Default: False) |

*Return Value*: An EmailAddress object or None.

#### Parse Address List

Parse a list of addresses., operates in strict or relaxed modes. Strict
mode will fail at the first instance of invalid grammar, relaxed modes
tries to recover and continue.

```python
parse_list(address_list, strict=False, as_tuple=False)
```

| Parameter      | Description                                                                                                 |
| -------------- | ----------------------------------------------------------------------------------------------------------- |
| address_list   | A delimiter (either `,` or `;`) separated list of addresses. (Maximum: 524288 characters)                   |
| strict         | Operate parser in strict (stop at any error) or relaxed (attempt to recover and continue). (Default: False) |
| as_tuple       | Return just the parsed list addresses, or also the unparsed portions. (Default: False)                      |

*Return Value*: If opearting in strict mode, returns a list of parsed EmailAddress objects. If operating
in relaxed mode, can return a tuple that contains the parsed addresses and unparsable portions or just
the parsed addresses in a list.

#### Validate Address

Validates (parse, plus dns, mx check, and custom grammar) a single
address spec. In the case of a valid address returns an EmailAddress
object, otherwise returns None.

```python
validate_address(addr_spec)
```

| Parameter	     | Description                                                                                |
| -------------- | ------------------------------------------------------------------------------------------ |
| address        | An address to parse. (Maximum: 512 characters)                                             |

*Return Value*: An EmailAddress object or None.

#### Validate Address List

Validates an address list, and returns a tuple of parsed and unparsed
portions. Can parse syntax only mode (no dns, mx check, or custom
grammar).

```python
validate_list(addr_list, as_tuple=True)
```

| Parameter      | Description                                                                               |
| -------------- | ----------------------------------------------------------------------------------------- |
| address_list   | A delimiter (either `,` or `;`) separated list of addresses. (Maximum: 524288 characters) |
| as_tuple       | Return just the parsed list addresses, or also the unparsed portions. (Default: False)    |

*Return Value*: If opearting in strict mode, returns a list of parsed EmailAddress objects. If operating
in relaxed mode, can return a tuple that contains the parsed addresses and unparsable portions or just
the parsed addresses in a list.

### MIME Parsing

#### Classes

##### MimePart

| Function       | Type   | Description                          |
| -------------- | ------ | ------------------------------------ |
| size           | Method | Returns message size in bytes        |
| headers        | Method | Returns multi dictionary with headers converted to unicode |
| content_type   | Method | Returns object with properties: main - main part of content type, sub - subpart of content type, params - dictionary with parameters |
| content_disposition   | Method    |  |
| content_encoding      | Method    |  |
| body                  | Method    | Returns decoded body |
| charset               | Property  |  |
| message_id            | Property  |  |
| subject               | Property  |  |
| clean_subject         | Method    |  |
| references            | Method    | Retunrs message-ids referencing the message in accordance to jwz threading algo |
| detected_format       | Method    |  |
| detected_subtype      | Method    |  |
| detected_content_type | Method    | Returns content type based on the body, content, file name and original content type supplied inside the message |
| is_root               | Method    | |
| set_root              | Method    | |
| to_string             | Method    | Returns MIME representation of the message |
| to_stream             | Method    | Serialzes the message using file like object |
| was_changed           | Method    | |
| walk                  | Method    | Returns iterator object traversing through the message parts, if you want to include the top level part into the iteration, use 'with_self' parameter. If you don't want to include parts of enclosed messages, use 'skip_enclosed' parameter. Each part itself provides headers, content_type and body members.|
| is_attachment         | Method      | |
| is_body               | Method      | |
| is_inline             | Method      | |
| is_delivery_notification | Method   | Tells whether a message is a system delivery notification |
| get_attached_message     | Method   | Returns attached message if found, None otherwize |
| remove_headers           | Method   | Removes all passed headers name in one operation |
| to_python_message        | Method   | |
| bounce                   | Property | If the message is bounce, retuns bounce object|
| is_bounce                | Method   | Determines whether the message is a bounce message based on given threshold. 0.3 is a good conservative base|
| enclose                  | Method   | |
| append                   | Method   | |
| decode_body              | Method   | |
|decode_transfer_encoding  | Method   | |
|decode_charset            | Method   | |
|encode_body               | Method   | |
|encode_charset            | Method   | |
|encode_transfer_encoding  | Method   | |
|choose_text_encoding      | Method   | |
|stronger_encoding         | Method   | |
|has_long_lines            | Method   | Returns True if text contains lines longer than a certain length. Some SMTP servers (Exchange) refuse to accept messages "wider" than certain length. |


##### MimeHeaders

Dictionary-like object that preserves the order and supports multiple values for the same key, knows whether it has been changed after the creation

| Function       | Type   | Description                          |
| -------------- | ------ | ------------------------------------ |
| prepend        | Method |                                      |
| add            | Method | Adds header without changing the existing headers with same name |
| keys           | Method | Returns the keys. (message header names) It remembers the order in which they were added, what is really important|
| transform      | Method | Accepts a function, getting a key, val and returning a new pair of key, val and applies the function to all header, value pairs in the message. |
| items          | Method | Returns header,val pairs in the preserved order. |
| iteritems      | Method | Returns iterator header,val pairs in the preserved order. |
| get            | Method | Returns header value (case-insensitive). |
| getall         | Method | Returns all header values by the given header name (case-insensitive) |
| have_changed   | Method | Tells whether someone has altered the headers after creation|
| from_stream    | Method | Takes a stream and reads the headers, decodes headers to unicode dict like object |
| to_stream      | Method | Takes a stream and serializes headers in a mime format |


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
