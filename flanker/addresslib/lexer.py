import ply.lex as lex
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

states = (
    ('domain','exclusive'),
    ('quote', 'exclusive'),
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

# NOTE: Our expression for dot_atom here differs from RFC 5322. In the RFC
# dot_atom is expressed as a superset of atom. That makes it difficult to write
# unambiguous parsing rules so we've defined it here in such a way that it
# doesn't conflict. As a result, any rules that accept dot_atom should also
# accept atom.
t_DOT_ATOM = r'''
             ( [a-zA-Z0-9\!\#\$\%\&\'\*\+\-\/\=\?\^\_\`\{\|\}\~] # Visable ASCII characters not including specials
             | [\xC2-\xDF][\x80-\xBF]                            # UTF8-2
             | \xE0[\xA0-\xBF][\x80-\xBF]                        # UTF8-3
             | [\xE1-\xEC][\x80-\xBF]{2}
             | \xED[\x80-\x9F][\x80-\xBF]
             | [\xEE-\xEF][\x80-\xBF]{2}
             | \xF0[\x90-\xBF][\x80-\xBF]{2}                     # UTF8-4
             | [\xF1-\xF3][\x80-\xBF]{3}
             | \xF4[\x80-\x8F][\x80-\xBF]{2}
             )+
             (
             \.
             ( [a-zA-Z0-9\!\#\$\%\&\'\*\+\-\/\=\?\^\_\`\{\|\}\~] # Visable ASCII characters not including specials
             | [\xC2-\xDF][\x80-\xBF]                            # UTF8-2
             | \xE0[\xA0-\xBF][\x80-\xBF]                        # UTF8-3
             | [\xE1-\xEC][\x80-\xBF]{2}
             | \xED[\x80-\x9F][\x80-\xBF]
             | [\xEE-\xEF][\x80-\xBF]{2}
             | \xF0[\x90-\xBF][\x80-\xBF]{2}                     # UTF8-4
             | [\xF1-\xF3][\x80-\xBF]{3}
             | \xF4[\x80-\x8F][\x80-\xBF]{2}
             )+
             )+
             '''

t_ATOM =     r'''
             ( [a-zA-Z0-9\!\#\$\%\&\'\*\+\-\/\=\?\^\_\`\{\|\}\~] # Visable ASCII characters not including specials
             | [\xC2-\xDF][\x80-\xBF]                            # UTF8-2
             | \xE0[\xA0-\xBF][\x80-\xBF]                        # UTF8-3
             | [\xE1-\xEC][\x80-\xBF]{2}
             | \xED[\x80-\x9F][\x80-\xBF]
             | [\xEE-\xEF][\x80-\xBF]{2}
             | \xF0[\x90-\xBF][\x80-\xBF]{2}                     # UTF8-4
             | [\xF1-\xF3][\x80-\xBF]{3}
             | \xF4[\x80-\x8F][\x80-\xBF]{2}
             )+
             '''

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
                 ( [\x21-\x5A]                   # Visable ASCII characters not
                 | [\x5E-\x7E]                   #   including '[', ']', or '\'
                 | [\xC2-\xDF][\x80-\xBF]        # UTF8-2
                 | \xE0[\xA0-\xBF][\x80-\xBF]    # UTF8-3
                 | [\xE1-\xEC][\x80-\xBF]{2}
                 | \xED[\x80-\x9F][\x80-\xBF]
                 | [\xEE-\xEF][\x80-\xBF]{2}
                 | \xF0[\x90-\xBF][\x80-\xBF]{2} # UTF8-4
                 | [\xF1-\xF3][\x80-\xBF]{3}
                 | \xF4[\x80-\x8F][\x80-\xBF]{2}
                 )+
                 '''

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
                ( \x21                          # Visable ASCII characters not
                | [\x23-\x5B]                   #   including '\' or '"'
                | [\x5D-\x7E]
                | [\xC2-\xDF][\x80-\xBF]        # UTF8-2
                | \xE0[\xA0-\xBF][\x80-\xBF]    # UTF8-3
                | [\xE1-\xEC][\x80-\xBF]{2}
                | \xED[\x80-\x9F][\x80-\xBF]
                | [\xEE-\xEF][\x80-\xBF]{2}
                | \xF0[\x90-\xBF][\x80-\xBF]{2} # UTF8-4
                | [\xF1-\xF3][\x80-\xBF]{3}
                | \xF4[\x80-\x8F][\x80-\xBF]{2}
                )+
                '''
t_quote_QPAIR = r'''
                \\                              # '/'
                ( [\x21-\x7E]                   # Visible ASCII character
                | \s                            # ' ', technically not valid
                | [\xC2-\xDF][\x80-\xBF]        # UTF8-2
                | \xE0[\xA0-\xBF][\x80-\xBF]    # UTF8-3
                | [\xE1-\xEC][\x80-\xBF]{2}
                | \xED[\x80-\x9F][\x80-\xBF]
                | [\xEE-\xEF][\x80-\xBF]{2}
                | \xF0[\x90-\xBF][\x80-\xBF]{2} # UTF8-4
                | [\xF1-\xF3][\x80-\xBF]{3}
                | \xF4[\x80-\x8F][\x80-\xBF]{2}
                )
                '''

t_quote_FWSP = r'([\s\t]*\r\n)?[\s\t]+' # folding whitespace

def t_quote_error(t):
    log.warning("syntax error in quoted string lexer, token=%s", t)


# Build the lexer
lexer = lex.lex(errorlog=log)
