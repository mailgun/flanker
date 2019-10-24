# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [0.9.9] - 2019-09-25
### Changed
- Replace the leading '.' in an quoted-printable encoded mime part to avoid
  obscure SMTP bug

## [0.9.0] - 2018-05-16
### Changed
- Support for Python 3 was added with preserving the Python 2 behavior in mind.
  As a result Python 3 specific logic may be not that efficient due to extra
  conversions between text and bytes, but that is left for future improvements; 
- CRLF is now consistently used when a parsed mime is serialized into a string. 
- Dependency on cchardet was made optional. Ported from [PR84](https://github.com/mailgun/flanker/pull/84)
- [PR94](https://github.com/mailgun/flanker/pull/94) Local Redis cache was made
 configurable via environment variables REDIS_HOST, REDIS_PORT, and REDIS_DB
 with the defaults matching the original behavior.

## [0.8.5] - 2018-03-30
### Changed
- MAX_HEADER_LENGTH (8000) and MAX_LINE_LENGTH (10000) parser limits were
 removed. 
- A bunch of implementation details were "hidden" in underscore prefixed
 files/folders. This change is technically breaking, but those files were
 never supposed to be used directly. 

## [0.8.4] - 2018-02-01
The change log has not been kept up to release v0.8.5. The only reliable
 source of information is the commit log on [GitHub](https://github.com/mailgun/flanker/commits/master).
