import ply.lex as lex
import logging

import six

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

states = (
    ('domain',  'exclusive'),
    ('quote',   'exclusive'),
    ('comment', 'exclusive'),
)

tokens = (
    'FWSP',
    'AT',
    'DOT',
    'COMMA',
    'SEMICOLON',
    'LANGLE',
    'RANGLE',
    'ATOM',
    'DOT_ATOM',
    'LBRACKET',
    'RBRACKET',
    'DTEXT',
    'DQUOTE',
    'QTEXT',
    'QPAIR',
    'LPAREN',
    'RPAREN',
    'CTEXT',
    'URL'
)

# Urls - Not a part of the message format RFC but we permit these currently

def t_URL(t):
    r'http(s)?://[^\s<>{}|^~\[\]`;,]+'
    return t

# Atoms - https://tools.ietf.org/html/rfc5322#section-3.2.3

t_FWSP      = r'([\s\t]*\r\n)?[\s\t]+' # folding whitespace
t_AT        = r'\@'                    # '@'
t_DOT       = r'\.'                    # '.'
t_COMMA     = r'\,'                    # ','
t_LANGLE    = r'\<'                    # '<'
t_RANGLE    = r'\>'                    # '>'
t_SEMICOLON = r'\;'                    # ';'

if six.PY2:
    _UTF8_2 = r'[\xC2-\xDF][\x80-\xBF]'
    _UTF8_3 = (r'(\xE0[\xA0-\xBF][\x80-\xBF]'    
               r'|[\xE1-\xEC][\x80-\xBF]{2}'
               r'|\xED[\x80-\x9F][\x80-\xBF]'
               r'|[\xEE-\xEF][\x80-\xBF]{2}'
               r')')

    _UTF8_4 = (r'(\xF0[\x90-\xBF][\x80-\xBF]{2}'
    
               r'|[\xF1-\xF3][\x80-\xBF]{3}'
               r'|\xF4[\x80-\x8F][\x80-\xBF]{2}'
               r')')
else:
    _UTF8_2 = r'[\u0080-\u07ff]'
    _UTF8_3 = (r'([\u0800-\u0fff]'
               r'|[\u1000-\ucfff]'
               r'|[\ud000-\ud7ff]'
               r'|[\ue000-\uffff]'
               r')')
    _UTF8_4 = (r'([\U00010000-\U0003ffff]'
               r'|[\U00040000-\U000fffff]'
               r'|[\U00100000-\U0010ffff]'
               r')')

_UNICODE_CHAR = '({}|{}|{})'.format(_UTF8_2, _UTF8_3, _UTF8_4)


t_ATOM = r'''
    ( [a-zA-Z0-9!#$%&\'*+\-/=?^_`{{|}}~]  # Visible ASCII except (),.:;<>@[\]
    | {unicode_char}
    )+
'''.format(unicode_char=_UNICODE_CHAR)

# NOTE: Our expression for dot_atom here differs from RFC 5322. In the RFC
# dot_atom is expressed as a superset of atom. That makes it difficult to write
# unambiguous parsing rules so we've defined it here in such a way that it
# doesn't conflict. As a result, any rules that accept dot_atom should also
# accept atom.
t_DOT_ATOM = r'{atom}(\.{atom})+'.format(atom=t_ATOM)


def t_error(t):
    log.warning("syntax error in default lexer, token=%s", t)

# Domain literals - https://tools.ietf.org/html/rfc5322#section-3.4.1


def t_LBRACKET(t):
    r'\['
    t.lexer.begin('domain')
    return t


def t_domain_RBRACKET(t):
    r'\]'
    t.lexer.begin('INITIAL')
    return t


t_domain_DTEXT = r'''
    ( [\x21-\x5A\x5E-\x7E] # Visible ASCII except '[', '\', ']',
    | {unicode_char}
    )+
'''.format(unicode_char=_UNICODE_CHAR)

t_domain_FWSP = r'([\s\t]*\r\n)?[\s\t]+' # folding whitespace


def t_domain_error(t):
    log.warning("syntax error in domain lexer, token=%s", t)

# Quoted strings - https://tools.ietf.org/html/rfc5322#section-3.2.4


def t_DQUOTE(t):
    r'\"'
    t.lexer.begin('quote')
    return t


def t_quote_DQUOTE(t):
    r'\"'
    t.lexer.begin('INITIAL')
    return t


t_quote_QTEXT = r'''
    ( [\x21\x23-\x5B\x5D-\x7E]  # Visible ASCII except '"', '\'
    | {unicode_char}
    )+
'''.format(unicode_char=_UNICODE_CHAR)

t_quote_QPAIR = r'''
    \\             # '\'
    ( [\x21-\x7E]  # Visible ASCII
    | \s           # ' ' technically not valid
    | {unicode_char}
    )
'''.format(unicode_char=_UNICODE_CHAR)

t_quote_FWSP = r'([\s\t]*\r\n)?[\s\t]+' # folding whitespace


def t_quote_error(t):
    log.warning("syntax error in quoted string lexer, token=%s", t)


# Comments - https://tools.ietf.org/html/rfc5322#section-3.2.2


def t_LPAREN(t):
    r'\('
    t.lexer.begin('comment')
    return t


def t_comment_RPAREN(t):
    r'\)'
    t.lexer.begin('INITIAL')
    return t


t_comment_CTEXT = r'''
    ( [\x21-\x27\x2A-\x5B\x5D-\x7E]  # Visible ASCII except '(', ')', or '\'
    | {unicode_char} )+
'''.format(unicode_char=_UNICODE_CHAR)


# Folding whitespace.
t_comment_FWSP = r'([\s\t]*\r\n)?[\s\t]+'

def t_comment_error(t):
    log.warning("syntax error in comment lexer, token=%s", t)


# Build the lexer
lexer = lex.lex(errorlog=log)
