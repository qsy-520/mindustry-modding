""" Parser for Mindustry JSON. 

This parser may be more forgiving then 
the actual Mindustry parser itself, so
to make parsing other mods possible.

The specific implimentation changes goes as follows:
- `//` maybe used for single line comments,
  and also cannot technically be used in strings;
- `"` quotes aren't required for strings;
- `,` commas aren't required for arrays or objects.
"""


'''
Use parsec.py to parse JSON text.
'''

from parsec import *

@generate
def comment():
    yield optional(many(string(" ") | string("\n") | string("\t")))
    yield string("//")
    comment = yield regex(".*")
    yield string("\n")
    return comment

whitespace = regex(r'\s*') << optional(many(comment))

lexeme = lambda p: p << whitespace

lbrace = lexeme(string('{'))
rbrace = lexeme(string('}'))
lbrack = lexeme(string('['))
rbrack = lexeme(string(']'))
colon = lexeme(string(':'))
comma = lexeme(string(',')) | whitespace
true = lexeme(string('true')).result(True)
false = lexeme(string('false')).result(False)
null = lexeme(string('null')).result(None)


def number():
    '''Parse number.'''
    return lexeme(
        regex(r'-?(0|[1-9][0-9]*)([.][0-9]+)?([eE][+-]?[0-9]+)?')
    ).parsecmap(float)

def charseq():
    '''Parse string. (normal string and escaped string)'''
    def string_part():
        '''Parse normal string.'''
        return regex(r'[^"\\]+')

    def string_esc():
        '''Parse escaped string.'''
        return string('\\') >> (
            string('\\')
            | string('/')
            | string('"')
            | string('b').result('\b')
            | string('f').result('\f')
            | string('n').result('\n')
            | string('r').result('\r')
            | string('t').result('\t')
            | regex(r'u[0-9a-fA-F]{4}').parsecmap(lambda s: chr(int(s[1:], 16)))
        )
    return string_part() | string_esc()

@lexeme
@generate
def quoted():
    '''Parse quoted string.'''
    yield string('"')
    body = yield many(charseq())
    yield string('"')
    return ''.join(body)

@generate
def unquoted():
    '''Parse unquoted string.'''
    body = yield many(regex(r"[a-zA-Z ]"))
    return ''.join(body).strip()

@generate
def array():
    '''Parse array element in JSON text.'''
    yield lbrack
    elements = yield sepBy(value, comma)
    yield rbrack
    return elements

@generate
def object_pair():
    '''Parse object pair in JSON.'''
    key = yield quoted | unquoted
    yield colon
    val = yield value
    return (key, val)

@generate
def json_object():
    '''Parse JSON object.'''
    yield lbrace
    pairs = yield sepBy(object_pair, comma)
    yield rbrace
    return dict(pairs)

value = quoted | number() | json_object | array | true | false | null | unquoted
jsonc = whitespace >> json_object

if __name__ == '__main__':
    print(jsonc.parse(""" 
// comment 1
// comment 2
{}
// comment 3
"""))
    print(jsonc.parse('{"test" : "json"  }'))
    print(jsonc.parse('{"test" :  json  }'))
    print(jsonc.parse('{ test  : "json" }'))
    print(jsonc.parse('{ test  :  json  }'))
    print(jsonc.parse('''{ test : json,
                           tist : jons }'''))
    print(jsonc.parse('''{ test : json 
                           tist : jons }'''))
    print(jsonc.parse('{} //comment'))
    print(jsonc.parse('''{ test : json 
                           tist : jons } //comment'''))
    print(jsonc.parse('''{ test : jsona //
                           tist : jons }'''))
    print(jsonc.parse('''{ test : jsonb // comment
                           tist : jons }'''))
    print(jsonc.parse('''{ test : jsonc 
// comment
                           tist : jons }'''))

    print(jsonc.parse('''{ test : json 
// comment 
      // comment
                           tist : jons }'''))
