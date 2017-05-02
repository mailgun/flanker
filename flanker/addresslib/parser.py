import ply.yacc as yacc
from lexer import tokens, lexer
from collections import namedtuple
import logging


logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

Mailbox = namedtuple('Mailbox', ['display_name', 'local_part', 'domain'])
Url     = namedtuple('Url',     ['address'])


# Parsing rules

start = 'mailbox_or_url_list'

precedence = (
    ('left', 'FWSP', 'ATEXT', 'QTEXT', 'QPAIR', 'DTEXT'),
    ('left', 'DOT', 'AT'),
    ('left', 'RANGLE', 'RBRACKET', 'DQUOTE'),
    ('left', 'COMMA', 'SEMICOLON'),
)

def p_expression_mailbox_or_url_list(p):
    '''mailbox_or_url_list : mailbox_or_url_list delim mailbox_or_url
                           | mailbox_or_url_list delim
                           | mailbox_or_url'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 3:
        p[0] = p[1]
    elif len(p) == 2:
        p[0] = [p[1]]

def p_expression_delim(p):
    '''delim : delim delim
             | COMMA ofwsp
             | SEMICOLON ofwsp'''

def p_expression_mailbox_or_url(p):
    '''mailbox_or_url : mailbox
                      | url'''
    p[0] = p[1]

def p_expression_url(p):
    'url : ofwsp URL ofwsp'
    p[0] = Url(p[2])

def p_expression_mailbox(p):
    '''mailbox : addr_spec
               | name_addr
               | angle_addr''' # NOTE: `angle_addr` is invalid here but has been added for backwards compatability
    p[0] = p[1]

def p_expression_name_addr(p):
    '''name_addr : phrase angle_addr
                 | phrase addr_spec''' # NOTE: `phrase addr_spec` is invalid here but has been added for backwards compatability
    p[0] = Mailbox(p[1], p[2].local_part, p[2].domain)

def p_expression_angle_addr(p):
    'angle_addr : ofwsp LANGLE addr_spec RANGLE ofwsp'
    p[0] = p[3]

def p_expression_addr_spec(p):
    '''addr_spec : local_part AT domain'''
    p[0] = Mailbox('', p[1], p[3])

def p_expression_local_part(p):
    '''local_part : dot_atom
                  | atom
                  | quoted_string'''
    p[0] = p[1]

def p_expression_domain(p):
    '''domain : dot_atom
              | atom
              | domain_literal'''
    p[0] = p[1]

def p_expression_quoted_string(p):
    '''quoted_string : ofwsp DQUOTE quoted_string_text DQUOTE ofwsp'''
    p[0] = '"{}"'.format(p[3])

def p_expression_quoted_string_text(p):
    '''quoted_string_text : quoted_string_text QTEXT
                          | quoted_string_text QPAIR
                          | quoted_string_text fwsp
                          | QTEXT
                          | QPAIR
                          | fwsp
                          |''' # NOTE: `empty` is invalid but has been added for backwards compatability
    if len(p) == 3:
        p[0] = '{}{}'.format(p[1], p[2])
    elif len(p) == 2:
        p[0] = p[1]
    elif len(p) == 1:
        p[0] = ''

def p_expression_domain_literal(p):
    '''domain_literal : ofwsp LBRACKET domain_literal_text RBRACKET ofwsp'''
    p[0] = '[{}]'.format(p[3])

def p_expression_domain_literal_text(p):
    '''domain_literal_text : domain_literal_text DTEXT
                           | domain_literal_text fwsp
                           | DTEXT
                           | fwsp'''
    if len(p) == 3:
        p[0] = '{}{}'.format(p[1], p[2])
    elif len(p) == 2:
        p[0] = p[1]

def p_expression_phrase(p):
    '''phrase : phrase dot_atom
              | phrase atom
              | phrase quoted_string
              | phrase DOT
              | dot_atom
              | atom
              | quoted_string
              | DOT'''
    if len(p) == 3:
        p[0] = '{} {}'.format(p[1], p[2])
    elif len(p) == 2:
        p[0] = p[1]

# NOTE: Our expression for dot_atom here differs from RFC 5322. In the RFC
# dot_atom is expressed as a superset of atom. That makes it difficult to write
# unambiguous parsing rules so we've defined it here in such a way that it
# doesn't conflict. As a result, any higher order rules that accept dot_atom
# should also accept atom.
def p_expression_dot_atom(p):
    'dot_atom : ofwsp dot_atom_text ofwsp'
    p[0] = p[2]

def p_expression_dot_atom_text(p):
    '''dot_atom_text : dot_atom_text DOT ATEXT
                     | ATEXT DOT ATEXT'''
    p[0] = '{}.{}'.format(p[1], p[3])

def p_expression_atom(p):
    'atom : ofwsp ATEXT ofwsp'
    p[0] = p[2]

def p_expression_ofwsp(p):
    '''ofwsp : fwsp
             |'''
    if len(p) == 2:
        p[0] = p[1]
    if len(p) == 1:
        p[0] = ''

def p_expression_fwsp(p):
    'fwsp : FWSP'
    p[0] = p[1].replace('\r\n', '')

def p_error(p):
    if p:
        raise SyntaxError('syntax error: token=%s, lexpos=%s' % (p.value, p.lexpos))
    raise SyntaxError('syntax error: eof')


# Build the parsers

log.info('building mailbox parser')
mailbox_parser = yacc.yacc(
    start='mailbox', errorlog=log)

log.info('building addr_spec parser')
addr_spec_parser = yacc.yacc(
    start='addr_spec', errorlog=log)

log.info('building url parser')
url_parser = yacc.yacc(
    start='url', errorlog=log)

log.info('building mailbox_or_url parser')
mailbox_or_url_parser = yacc.yacc(
    start='mailbox_or_url', errorlog=log)

log.info('building mailbox_or_url_list parser')
mailbox_or_url_list_parser = yacc.yacc(
    start='mailbox_or_url_list', errorlog=log)


# Interactive prompt for easy debugging
if __name__ == '__main__':
    while True:
        try:
            s = raw_input('\nflanker> ')
        except KeyboardInterrupt:
            break
        except EOFError:
            break
        if s == '': continue

        print '\nTokens list:\n'
        lexer.input(s)
        while True:
            tok = lexer.token()
            if not tok:
                break
            print tok

        print '\nParsing behavior:\n'
        result = mailbox_or_url_list_parser.parse(s, debug=log)

        print '\nResult:\n'
        print result
