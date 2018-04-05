import logging
from collections import namedtuple

import ply.yacc as yacc

from flanker.addresslib._parser.lexer import lexer, tokens

log = logging.getLogger(__name__)

Mailbox = namedtuple('Mailbox', ['display_name', 'local_part', 'domain'])
Url     = namedtuple('Url',     ['address'])


# Parsing rules

start = 'mailbox_or_url_list'

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

def p_delim(p):
    '''delim : delim fwsp COMMA
             | delim fwsp SEMICOLON
             | COMMA
             | SEMICOLON'''

def p_expression_mailbox_or_url(p):
    '''mailbox_or_url : mailbox
                      | url'''
    p[0] = p[1]

def p_expression_url(p):
    'url : ofwsp URL ofwsp'
    p[0] = Url(p[2])

def p_expression_mailbox(p):
    '''mailbox : addr_spec
               | angle_addr
               | name_addr'''
    p[0] = p[1]

def p_expression_name_addr(p):
    'name_addr : ofwsp phrase angle_addr'
    p[0] = Mailbox(p[2], p[3].local_part, p[3].domain)

def p_expression_angle_addr(p):
    'angle_addr : ofwsp LANGLE addr_spec RANGLE ofwsp'
    p[0] = Mailbox('', p[3].local_part, p[3].domain)

def p_expression_addr_spec(p):
    'addr_spec : ofwsp local_part AT domain ofwsp'
    p[0] = Mailbox('', p[2], p[4])

def p_expression_local_part(p):
    '''local_part : DOT_ATOM
                  | ATOM
                  | quoted_string'''
    p[0] = p[1]

def p_expression_domain(p):
    '''domain : DOT_ATOM
              | ATOM
              | domain_literal'''
    p[0] = p[1]

def p_expression_quoted_string(p):
    '''quoted_string : DQUOTE quoted_string_text DQUOTE
                     | DQUOTE DQUOTE'''
    if len(p) == 4:
        p[0] = '"{}"'.format(p[2])
    elif len(p) == 3:
        p[0] = '""'

def p_expression_quoted_string_text(p):
    '''quoted_string_text : quoted_string_text QTEXT
                          | quoted_string_text QPAIR
                          | quoted_string_text fwsp
                          | QTEXT
                          | QPAIR
                          | fwsp'''
    p[0] = ''.join(p[1:])

def p_expression_domain_literal(p):
    '''domain_literal : LBRACKET domain_literal_text RBRACKET
                      | LBRACKET RBRACKET'''
    if len(p) == 4:
        p[0] = '[{}]'.format(p[2])
    elif len(p) == 3:
        p[0] = '[]'

def p_expression_domain_literal_text(p):
    '''domain_literal_text : domain_literal_text DTEXT
                           | domain_literal_text fwsp
                           | DTEXT
                           | fwsp'''
    p[0] = ''.join(p[1:])

def p_expression_comment(p):
    '''comment : LPAREN comment_text RPAREN
               | LPAREN RPAREN'''
    p[0] = ''

def p_expression_comment_text(p):
    '''comment_text : comment_text CTEXT
                    | comment_text fwsp
                    | CTEXT
                    | fwsp'''
    p[0] = ''.join(p[1:])

def p_expression_phrase(p):
    '''phrase : phrase fwsp ATOM
              | phrase fwsp DOT_ATOM
              | phrase fwsp DOT
              | phrase fwsp quoted_string
              | phrase ATOM
              | phrase DOT_ATOM
              | phrase DOT
              | phrase quoted_string
              | ATOM
              | DOT_ATOM
              | DOT
              | quoted_string'''
    if len(p) == 4:
        p[0] = '{} {}'.format(p[1], p[3])
    if len(p) == 3:
        p[0] = '{}{}'.format(p[1], p[2])
    elif len(p) == 2:
        p[0] = p[1]

def p_expression_ofwsp(p):
    '''ofwsp : fwsp comment fwsp
             | fwsp comment
             | comment fwsp
             | comment
             | fwsp
             |'''
    p[0] = ''.join(p[1:])

def p_expression_fwsp(p):
    'fwsp : FWSP'
    p[0] = p[1].replace('\r\n', '')

def p_error(p):
    if p:
        raise SyntaxError('syntax error: token=%s, lexpos=%s' % (p.value, p.lexpos))
    raise SyntaxError('syntax error: eof')


# Build the parsers
log.debug('building mailbox parser')
mailbox_parser = yacc.yacc(start='mailbox',
                           errorlog=log,
                           tabmodule='mailbox_parsetab')

log.debug('building addr_spec parser')
addr_spec_parser = yacc.yacc(start='addr_spec',
                             errorlog=log,
                             tabmodule='addr_spec_parsetab')

log.debug('building url parser')
url_parser = yacc.yacc(start='url',
                       errorlog=log,
                       tabmodule='url_parsetab')

log.debug('building mailbox_or_url parser')
mailbox_or_url_parser = yacc.yacc(start='mailbox_or_url',
                                  errorlog=log,
                                  tabmodule='mailbox_or_url_parsetab')

log.debug('building mailbox_or_url_list parser')
mailbox_or_url_list_parser = yacc.yacc(start='mailbox_or_url_list',
                                       errorlog=log,
                                       tabmodule='mailbox_or_url_list_parsetab')


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

        print('\nTokens list:\n')
        lexer.input(s)
        while True:
            tok = lexer.token()
            if not tok:
                break
            print(tok)

        print('\nParsing behavior:\n')
        result = mailbox_or_url_list_parser.parse(s, debug=log)

        print('\nResult:\n')
        print(result)
