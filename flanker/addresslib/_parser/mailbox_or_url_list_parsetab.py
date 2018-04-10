
# mailbox_or_url_list_parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'mailbox_or_url_listFWSP AT DOT COMMA SEMICOLON LANGLE RANGLE ATOM DOT_ATOM LBRACKET RBRACKET DTEXT DQUOTE QTEXT QPAIR LPAREN RPAREN CTEXT URLmailbox_or_url_list : mailbox_or_url_list delim mailbox_or_url\n                           | mailbox_or_url_list delim\n                           | mailbox_or_urldelim : delim fwsp COMMA\n             | delim fwsp SEMICOLON\n             | COMMA\n             | SEMICOLONmailbox_or_url : mailbox\n                      | urlurl : ofwsp URL ofwspmailbox : addr_spec\n               | angle_addr\n               | name_addrname_addr : ofwsp phrase angle_addrangle_addr : ofwsp LANGLE addr_spec RANGLE ofwspaddr_spec : ofwsp local_part AT domain ofwsplocal_part : DOT_ATOM\n                  | ATOM\n                  | quoted_stringdomain : DOT_ATOM\n              | ATOM\n              | domain_literalquoted_string : DQUOTE quoted_string_text DQUOTE\n                     | DQUOTE DQUOTEquoted_string_text : quoted_string_text QTEXT\n                          | quoted_string_text QPAIR\n                          | quoted_string_text fwsp\n                          | QTEXT\n                          | QPAIR\n                          | fwspdomain_literal : LBRACKET domain_literal_text RBRACKET\n                      | LBRACKET RBRACKETdomain_literal_text : domain_literal_text DTEXT\n                           | domain_literal_text fwsp\n                           | DTEXT\n                           | fwspcomment : LPAREN comment_text RPAREN\n               | LPAREN RPARENcomment_text : comment_text CTEXT\n                    | comment_text fwsp\n                    | CTEXT\n                    | fwspphrase : phrase fwsp ATOM\n              | phrase fwsp DOT_ATOM\n              | phrase fwsp DOT\n              | phrase fwsp quoted_string\n              | phrase ATOM\n              | phrase DOT_ATOM\n              | phrase DOT\n              | phrase quoted_string\n              | ATOM\n              | DOT_ATOM\n              | DOT\n              | quoted_stringofwsp : fwsp comment fwsp\n             | fwsp comment\n             | comment fwsp\n             | comment\n             | fwsp\n             |fwsp : FWSP'

_lr_action_items = {'FWSP': ([0, 2, 4, 9, 13, 15, 16, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 36, 37, 38, 39, 40, 44, 45, 46, 47, 48, 49, 50, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 74, 75, 76, 77, 78, 79, 80], [4, 4, -61, 4, 4, 4, 4, -51, 4, -52, 4, -54, -53, -42, 4, -38, -41, -7, 4, -6, -30, -29, -28, -24, 4, -48, -47, -50, -49, -40, -37, -39, 4, 4, 4, -20, -21, -22, -27, -26, -25, -23, -44, -43, -46, -45, -5, -4, -36, -35, 4, -32, -34, -33, -31]), 'LANGLE': ([0, 1, 2, 3, 4, 13, 14, 18, 20, 21, 22, 23, 26, 28, 29, 30, 31, 39, 41, 42, 44, 45, 46, 47, 49, 51, 65, 66, 67, 68, 69, 70, 71], [-60, -59, -58, 15, -61, -56, -57, -51, -52, -60, -54, -53, -38, -7, -60, -6, -55, -24, -59, 15, -48, -47, -50, -49, -37, -59, -23, -44, -43, -46, -45, -5, -4]), 'QPAIR': ([4, 19, 36, 37, 38, 40, 62, 63, 64], [-61, 37, -30, -29, -28, 63, -27, -26, -25]), 'SEMICOLON': ([1, 2, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 16, 26, 28, 29, 30, 31, 34, 43, 49, 51, 52, 56, 57, 59, 60, 61, 70, 71, 72, 73, 77, 80], [-59, -58, -61, -13, -11, -3, -8, 28, -12, -9, -56, -57, -60, -38, -7, -2, -6, -55, -10, -14, -37, 70, -1, -60, -60, -20, -21, -22, -5, -4, -15, -16, -32, -31]), 'URL': ([0, 1, 2, 3, 4, 13, 14, 26, 28, 29, 30, 31, 49, 51, 70, 71], [-60, -59, -58, 16, -61, -56, -57, -38, -7, -60, -6, -55, -37, -59, -5, -4]), 'QTEXT': ([4, 19, 36, 37, 38, 40, 62, 63, 64], [-61, 38, -30, -29, -28, 64, -27, -26, -25]), 'RPAREN': ([4, 9, 24, 25, 27, 48, 50], [-61, 26, -42, 49, -41, -40, -39]), 'DTEXT': ([4, 58, 74, 75, 76, 78, 79], [-61, 75, -36, -35, 79, -34, -33]), 'DQUOTE': ([0, 1, 2, 3, 4, 13, 14, 15, 18, 19, 20, 21, 22, 23, 26, 28, 29, 30, 31, 32, 36, 37, 38, 39, 40, 41, 44, 45, 46, 47, 49, 51, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71], [-60, -59, -58, 19, -61, -56, -57, -60, -51, 39, -52, 19, -54, -53, -38, -7, -60, -6, -55, 19, -30, -29, -28, -24, 65, 19, -48, -47, -50, -49, -37, -59, -27, -26, -25, -23, -44, -43, -46, -45, -5, -4]), 'LBRACKET': ([35], [58]), 'DOT_ATOM': ([0, 1, 2, 3, 4, 13, 14, 15, 18, 20, 21, 22, 23, 26, 28, 29, 30, 31, 32, 35, 39, 41, 44, 45, 46, 47, 49, 51, 65, 66, 67, 68, 69, 70, 71], [-60, -59, -58, 20, -61, -56, -57, -60, -51, -52, 44, -54, -53, -38, -7, -60, -6, -55, 53, 59, -24, 66, -48, -47, -50, -49, -37, -59, -23, -44, -43, -46, -45, -5, -4]), 'COMMA': ([1, 2, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 16, 26, 28, 29, 30, 31, 34, 43, 49, 51, 52, 56, 57, 59, 60, 61, 70, 71, 72, 73, 77, 80], [-59, -58, -61, -13, -11, -3, -8, 30, -12, -9, -56, -57, -60, -38, -7, -2, -6, -55, -10, -14, -37, 71, -1, -60, -60, -20, -21, -22, -5, -4, -15, -16, -32, -31]), 'AT': ([17, 18, 20, 22, 39, 53, 54, 55, 65], [35, -18, -17, -19, -24, -17, -18, -19, -23]), 'LPAREN': ([0, 1, 4, 15, 16, 18, 20, 21, 22, 23, 28, 29, 30, 39, 41, 44, 45, 46, 47, 51, 56, 57, 59, 60, 61, 65, 66, 67, 68, 69, 70, 71, 77, 80], [9, 9, -61, 9, 9, -51, -52, 9, -54, -53, -7, 9, -6, -24, 9, -48, -47, -50, -49, 9, 9, 9, -20, -21, -22, -23, -44, -43, -46, -45, -5, -4, -32, -31]), 'ATOM': ([0, 1, 2, 3, 4, 13, 14, 15, 18, 20, 21, 22, 23, 26, 28, 29, 30, 31, 32, 35, 39, 41, 44, 45, 46, 47, 49, 51, 65, 66, 67, 68, 69, 70, 71], [-60, -59, -58, 18, -61, -56, -57, -60, -51, -52, 45, -54, -53, -38, -7, -60, -6, -55, 54, 60, -24, 67, -48, -47, -50, -49, -37, -59, -23, -44, -43, -46, -45, -5, -4]), 'RANGLE': ([1, 2, 4, 13, 14, 26, 31, 33, 49, 57, 59, 60, 61, 73, 77, 80], [-59, -58, -61, -56, -57, -38, -55, 56, -37, -60, -20, -21, -22, -16, -32, -31]), 'RBRACKET': ([4, 58, 74, 75, 76, 78, 79], [-61, 77, -36, -35, 80, -34, -33]), 'CTEXT': ([4, 9, 24, 25, 27, 48, 50], [-61, 27, -42, 50, -41, -40, -39]), 'DOT': ([0, 1, 2, 3, 4, 13, 14, 18, 20, 21, 22, 23, 26, 28, 29, 30, 31, 39, 41, 44, 45, 46, 47, 49, 51, 65, 66, 67, 68, 69, 70, 71], [-60, -59, -58, 23, -61, -56, -57, -51, -52, 47, -54, -53, -38, -7, -60, -6, -55, -24, 69, -48, -47, -50, -49, -37, -59, -23, -44, -43, -46, -45, -5, -4]), '$end': ([1, 2, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 16, 26, 28, 29, 30, 31, 34, 43, 49, 52, 56, 57, 59, 60, 61, 70, 71, 72, 73, 77, 80], [-59, -58, -61, -13, -11, -3, -8, 0, -12, -9, -56, -57, -60, -38, -7, -2, -6, -55, -10, -14, -37, -1, -60, -60, -20, -21, -22, -5, -4, -15, -16, -32, -31])}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x, _y in zip(_v[0], _v[1]):
      if not _x in _lr_action: _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'fwsp': ([0, 2, 9, 13, 15, 16, 19, 21, 25, 29, 40, 56, 57, 58, 76], [1, 14, 24, 31, 1, 1, 36, 41, 48, 51, 62, 1, 1, 74, 78]), 'comment': ([0, 1, 15, 16, 21, 29, 41, 51, 56, 57], [2, 13, 2, 2, 2, 2, 13, 13, 2, 2]), 'domain': ([35], [57]), 'comment_text': ([9], [25]), 'name_addr': ([0, 29], [5, 5]), 'ofwsp': ([0, 15, 16, 21, 29, 56, 57], [3, 32, 34, 42, 3, 72, 73]), 'mailbox_or_url_list': ([0], [10]), 'angle_addr': ([0, 21, 29], [11, 43, 11]), 'mailbox_or_url': ([0, 29], [7, 52]), 'local_part': ([3, 32], [17, 17]), 'delim': ([10], [29]), 'domain_literal_text': ([58], [76]), 'mailbox': ([0, 29], [8, 8]), 'quoted_string_text': ([19], [40]), 'url': ([0, 29], [12, 12]), 'addr_spec': ([0, 15, 29], [6, 33, 6]), 'phrase': ([3], [21]), 'quoted_string': ([3, 21, 32, 41], [22, 46, 55, 68]), 'domain_literal': ([35], [61])}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> mailbox_or_url_list", "S'", 1, None, None, None),
  ('mailbox_or_url_list -> mailbox_or_url_list delim mailbox_or_url', 'mailbox_or_url_list', 3, 'p_expression_mailbox_or_url_list', 'parser.py', 19),
  ('mailbox_or_url_list -> mailbox_or_url_list delim', 'mailbox_or_url_list', 2, 'p_expression_mailbox_or_url_list', 'parser.py', 20),
  ('mailbox_or_url_list -> mailbox_or_url', 'mailbox_or_url_list', 1, 'p_expression_mailbox_or_url_list', 'parser.py', 21),
  ('delim -> delim fwsp COMMA', 'delim', 3, 'p_delim', 'parser.py', 30),
  ('delim -> delim fwsp SEMICOLON', 'delim', 3, 'p_delim', 'parser.py', 31),
  ('delim -> COMMA', 'delim', 1, 'p_delim', 'parser.py', 32),
  ('delim -> SEMICOLON', 'delim', 1, 'p_delim', 'parser.py', 33),
  ('mailbox_or_url -> mailbox', 'mailbox_or_url', 1, 'p_expression_mailbox_or_url', 'parser.py', 36),
  ('mailbox_or_url -> url', 'mailbox_or_url', 1, 'p_expression_mailbox_or_url', 'parser.py', 37),
  ('url -> ofwsp URL ofwsp', 'url', 3, 'p_expression_url', 'parser.py', 41),
  ('mailbox -> addr_spec', 'mailbox', 1, 'p_expression_mailbox', 'parser.py', 45),
  ('mailbox -> angle_addr', 'mailbox', 1, 'p_expression_mailbox', 'parser.py', 46),
  ('mailbox -> name_addr', 'mailbox', 1, 'p_expression_mailbox', 'parser.py', 47),
  ('name_addr -> ofwsp phrase angle_addr', 'name_addr', 3, 'p_expression_name_addr', 'parser.py', 51),
  ('angle_addr -> ofwsp LANGLE addr_spec RANGLE ofwsp', 'angle_addr', 5, 'p_expression_angle_addr', 'parser.py', 55),
  ('addr_spec -> ofwsp local_part AT domain ofwsp', 'addr_spec', 5, 'p_expression_addr_spec', 'parser.py', 59),
  ('local_part -> DOT_ATOM', 'local_part', 1, 'p_expression_local_part', 'parser.py', 63),
  ('local_part -> ATOM', 'local_part', 1, 'p_expression_local_part', 'parser.py', 64),
  ('local_part -> quoted_string', 'local_part', 1, 'p_expression_local_part', 'parser.py', 65),
  ('domain -> DOT_ATOM', 'domain', 1, 'p_expression_domain', 'parser.py', 69),
  ('domain -> ATOM', 'domain', 1, 'p_expression_domain', 'parser.py', 70),
  ('domain -> domain_literal', 'domain', 1, 'p_expression_domain', 'parser.py', 71),
  ('quoted_string -> DQUOTE quoted_string_text DQUOTE', 'quoted_string', 3, 'p_expression_quoted_string', 'parser.py', 75),
  ('quoted_string -> DQUOTE DQUOTE', 'quoted_string', 2, 'p_expression_quoted_string', 'parser.py', 76),
  ('quoted_string_text -> quoted_string_text QTEXT', 'quoted_string_text', 2, 'p_expression_quoted_string_text', 'parser.py', 83),
  ('quoted_string_text -> quoted_string_text QPAIR', 'quoted_string_text', 2, 'p_expression_quoted_string_text', 'parser.py', 84),
  ('quoted_string_text -> quoted_string_text fwsp', 'quoted_string_text', 2, 'p_expression_quoted_string_text', 'parser.py', 85),
  ('quoted_string_text -> QTEXT', 'quoted_string_text', 1, 'p_expression_quoted_string_text', 'parser.py', 86),
  ('quoted_string_text -> QPAIR', 'quoted_string_text', 1, 'p_expression_quoted_string_text', 'parser.py', 87),
  ('quoted_string_text -> fwsp', 'quoted_string_text', 1, 'p_expression_quoted_string_text', 'parser.py', 88),
  ('domain_literal -> LBRACKET domain_literal_text RBRACKET', 'domain_literal', 3, 'p_expression_domain_literal', 'parser.py', 92),
  ('domain_literal -> LBRACKET RBRACKET', 'domain_literal', 2, 'p_expression_domain_literal', 'parser.py', 93),
  ('domain_literal_text -> domain_literal_text DTEXT', 'domain_literal_text', 2, 'p_expression_domain_literal_text', 'parser.py', 100),
  ('domain_literal_text -> domain_literal_text fwsp', 'domain_literal_text', 2, 'p_expression_domain_literal_text', 'parser.py', 101),
  ('domain_literal_text -> DTEXT', 'domain_literal_text', 1, 'p_expression_domain_literal_text', 'parser.py', 102),
  ('domain_literal_text -> fwsp', 'domain_literal_text', 1, 'p_expression_domain_literal_text', 'parser.py', 103),
  ('comment -> LPAREN comment_text RPAREN', 'comment', 3, 'p_expression_comment', 'parser.py', 107),
  ('comment -> LPAREN RPAREN', 'comment', 2, 'p_expression_comment', 'parser.py', 108),
  ('comment_text -> comment_text CTEXT', 'comment_text', 2, 'p_expression_comment_text', 'parser.py', 112),
  ('comment_text -> comment_text fwsp', 'comment_text', 2, 'p_expression_comment_text', 'parser.py', 113),
  ('comment_text -> CTEXT', 'comment_text', 1, 'p_expression_comment_text', 'parser.py', 114),
  ('comment_text -> fwsp', 'comment_text', 1, 'p_expression_comment_text', 'parser.py', 115),
  ('phrase -> phrase fwsp ATOM', 'phrase', 3, 'p_expression_phrase', 'parser.py', 119),
  ('phrase -> phrase fwsp DOT_ATOM', 'phrase', 3, 'p_expression_phrase', 'parser.py', 120),
  ('phrase -> phrase fwsp DOT', 'phrase', 3, 'p_expression_phrase', 'parser.py', 121),
  ('phrase -> phrase fwsp quoted_string', 'phrase', 3, 'p_expression_phrase', 'parser.py', 122),
  ('phrase -> phrase ATOM', 'phrase', 2, 'p_expression_phrase', 'parser.py', 123),
  ('phrase -> phrase DOT_ATOM', 'phrase', 2, 'p_expression_phrase', 'parser.py', 124),
  ('phrase -> phrase DOT', 'phrase', 2, 'p_expression_phrase', 'parser.py', 125),
  ('phrase -> phrase quoted_string', 'phrase', 2, 'p_expression_phrase', 'parser.py', 126),
  ('phrase -> ATOM', 'phrase', 1, 'p_expression_phrase', 'parser.py', 127),
  ('phrase -> DOT_ATOM', 'phrase', 1, 'p_expression_phrase', 'parser.py', 128),
  ('phrase -> DOT', 'phrase', 1, 'p_expression_phrase', 'parser.py', 129),
  ('phrase -> quoted_string', 'phrase', 1, 'p_expression_phrase', 'parser.py', 130),
  ('ofwsp -> fwsp comment fwsp', 'ofwsp', 3, 'p_expression_ofwsp', 'parser.py', 139),
  ('ofwsp -> fwsp comment', 'ofwsp', 2, 'p_expression_ofwsp', 'parser.py', 140),
  ('ofwsp -> comment fwsp', 'ofwsp', 2, 'p_expression_ofwsp', 'parser.py', 141),
  ('ofwsp -> comment', 'ofwsp', 1, 'p_expression_ofwsp', 'parser.py', 142),
  ('ofwsp -> fwsp', 'ofwsp', 1, 'p_expression_ofwsp', 'parser.py', 143),
  ('ofwsp -> <empty>', 'ofwsp', 0, 'p_expression_ofwsp', 'parser.py', 144),
  ('fwsp -> FWSP', 'fwsp', 1, 'p_expression_fwsp', 'parser.py', 148),
]
