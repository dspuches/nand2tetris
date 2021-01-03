import re
from errors.tokenizer_error import TokenizerError
from errors.token_error import TokenError


class JackTokenizer():
    SYMBOLS = [
        "{",
        "}",
        "(",
        ")",
        "[",
        "]",
        ".",
        ",",
        ";",
        "+",
        "-",
        "*",
        "/",
        "&",
        "|",
        "<",
        ">",
        "=",
        "~",
    ]
    
    KEYWORDS = [
        "class",
        "constructor",
        "function",
        "method",
        "field",
        "static",
        "var",
        "int",
        "char",
        "boolean",
        "void",
        "true",
        "false",
        "null",
        "this",
        "let",
        "do",
        "if",
        "else",
        "while",
        "return",
    ]

    T_KEYWORD = "KEYWORD"
    T_SYMBOL = "SYMBOL"
    T_IDENTIFIER = "IDENTIFIER"
    T_INT_CONSTANT = "INT_CONSTANT"
    T_STRING_CONSTANT = "STRING_CONST"

    TYPE_XML = {
        T_KEYWORD: "keyword",
        T_SYMBOL: "symbol",
        T_IDENTIFIER: "identifier",
        T_INT_CONSTANT: "integerConstant",
        T_STRING_CONSTANT: "stringConstant",
    }

    K_CLASS = "CLASS"
    K_METHOD = "METHOD"
    K_FUNCTION = "FUNCTION"
    K_CONSTRUCTOR = "CONSTRUCTOR"
    K_INT = "INT"
    K_BOOLEAN = "BOOLEAN"
    K_CHAR = "CHAR"
    K_VOID = "VOID"
    K_VAR = "VAR"
    K_STATIC = "STATIC"
    K_FIELD = "FIELD"
    K_LET = "LET"
    K_DO = "DO"
    K_IF = "IF"
    K_ELSE = "ELSE"
    K_WHILE = "WHILE"
    K_RETURN = "RETURN"
    K_TRUE = "TRUE"
    K_FALSE = "FALSE"
    K_NULL = "NULL"
    K_THIS = "THIS"

    def __init__(self, in_f):
        self._fd = in_f                             # file descriptor
        self._line = None                           # read a line
        self._line_count = 0                        # start off the counter at 1
        self._line_length = 0                       # store length of current line
        self._start = 0                             # the index of the start of the token in current line
        self._curr = 0                              # the current index in the current line
        self._eof = False
        self._next_token = self._get_next_token()   # attempt to get the next token
        self._curr_token = None

    # read a line from the stream, increase line count, reset indices
    def _read_next_line(self):
        next = self._fd.readline()
        if next == '':
            self._eof = True
        else:
            self._line = next
            self._line_count += 1
            self._line_length = len(self._line)
            self._start = 0
            self._curr = 0
    
    # move both curr and start to the next position
    def _bump(self):
        self._curr += 1
        self._align()
    
    # move start to curr
    def _align(self):
        self._start = self._curr

    # peek at next char (curr + 1)
    def peek(self):
        if (self._curr + 1 < self._line_length):
            return self._line[self._curr + 1]
        else:
            return ""
    
    # handler called when EOL is encountered scanning a line
    def _handle_end_of_line(self):
        # we have a token if start != curr
        scanning = True
        token = None
        if (self._curr != self._start):
            token = self._line[self._start:self._curr] 
            scanning = False
        self._read_next_line()
        return scanning, token
    
    # handler called when " is encountered scanning a line
    def _handle_string(self):
        token = None
        scanning = True
        scanning_string = True
        self._curr += 1
        while (scanning_string):
            if (self._curr == self._line_length):
                # end of line
                raise TokenError(self._line[self._start:self._curr], "Unterminated string constant")
            elif (self._line[self._curr] == '"'):
                # found closing quote
                token = self._line[self._start:self._curr+1] 
                scanning_string = False
                scanning = False
                self._bump()
            else:
                # keep scanning
                self._curr += 1
        return scanning, token
    
    # handler called when a symbol is encountered scanning a line
    # note that comments start with / which is also a division symbol
    # handler must peek ahead if the symbol is /
    def _handle_symbol(self):
        scanning = True
        token = None
        if (self._start == self._curr):
            # if start == curr, the symbol is the token...unless its a comment
            if (self._line[self._curr] == "/"):
                # check if it is a comment and skip them if it is
                if (self.peek() == "/"):
                    self._handle_singleline_comment()
                    return scanning, token
                elif (self.peek() == "*"):
                    self._handle_multiline_comment()
                    return scanning, token
            
            # not a comment, so its a token
            token = self._line[self._curr]
            scanning = False
            self._bump()
        else:
            # otherwise, the previous text from start up to curr is the token
            token = self._line[self._start:self._curr]
            scanning = False
            self._align()
        return scanning, token

    # process a // type comment
    def _handle_singleline_comment(self):
        self._read_next_line()
    
    # process a /* */ type comment
    def _handle_multiline_comment(self):
        scanning = True
        self._bump()            # start/curr point to * of /*
        self._bump()            # start/curr point to first char after /*

        while (scanning):
            if (self._curr == self._line_length):
                if (self._eof):
                    #EOF without finding closure. Raise exception
                    raise TokenizerError("Reached EOF before finding closing */ to multiline comment")
                # end of current line, move to next
                self._read_next_line()
                
            elif (self._line[self._curr] == "*"):
                # if we find a *, check if its the end of comment
                if (self.peek() == "/"):
                    # end of comment
                    scanning = False
                    self._bump()
                    self._bump()
                else:
                    self._curr += 1
            else:
                self._curr += 1

    # handler called when a space is encountered scanning a line
    def _handle_space(self):
        # we have a token if start and curr are not the same. Otherwise, bump
        scanning = True
        token = None
        if (self._start != self._curr):
            token = self._line[self._start:self._curr] 
            scanning = False
        self._bump()
        return scanning, token

    # this method will return the next token in the stream
    def _get_next_token(self):
        token = None
        scanning = True

        if (self._line == None):
            self._read_next_line()

        # EOF
        if (self._eof):
            return token

        while (scanning):
            # EOF encountered while processing tokens
            if (self._eof):
                break

            if (self._curr == self._line_length or self._line[self._curr] == '\n'):
                scanning, token = self._handle_end_of_line()
            elif (self._line[self._curr] == '"'):
                scanning, token  = self._handle_string()
            elif (self._line[self._curr] in self.SYMBOLS):
                scanning, token = self._handle_symbol()
            elif (self._line[self._curr] == ' ' or self._line[self._curr] == '\t'):
                scanning, token = self._handle_space()
            elif (scanning):
                # if we got this far, no tokens have been found yet and we havent reached end of line or EOF
                self._curr += 1

        return token

    # return the raw token
    def token(self):
        return self._curr_token

    # return true if there are more tokens to process (_next_token is not None)
    def has_more_tokens(self):
        if self._next_token is None:
            return False
        else:
            return True

    # move to the next token
    def advance(self):
        if self._next_token is None:
            raise TokenizerError("Unexpected EOF, no more tokens to process")
        self._curr_token = self._next_token
        self._next_token = self._get_next_token()

    # determine the type of the token
    def token_type(self):
        t_type = None
        int_regex = "^[0-9]+$"
        string_regex = '^"([^"\n])*"$'
        id_regex = "^[a-zA-Z_][a-zA-Z0-9_]*$"
        
        if (self._curr_token == None):
            raise TokenizerError("Cannot call token_type() before advance() has been called()")
        
        # see if we have any matches
        if (self._curr_token in self.KEYWORDS):
            t_type = self.T_KEYWORD
        elif (self._curr_token in self.SYMBOLS):
            t_type = self.T_SYMBOL
        elif (re.search(int_regex, self._curr_token)):
            value = int(self._curr_token)
            if (value >= 0 and value <= 32767):
                t_type = self.T_INT_CONSTANT
            else:
                raise TokenError(self._curr_token, "Integers must be in the range 0..32767")
        elif (re.search(string_regex, self._curr_token)):
            t_type = self.T_STRING_CONSTANT
        elif (re.search(id_regex, self._curr_token)):
            t_type = self.T_IDENTIFIER
        else:
            raise TokenError(self._curr_token, "Unable to determine token type")

        return t_type

    # Return the keyword to upper case
    # This should only get called if the token is a keyword (token_type == T_KEYWORD)
    def keyword(self):
        if (self.token_type() is not self.T_KEYWORD):
            raise TokenizerError("Token type must be {} to call the keyword() method".format(self.T_KEYWORD))
        return self._curr_token.upper()

    # Return the symbol
    # This should only get called if the token is a symbol (token_type == T_SYMBOL)
    def symbol(self):
        if (self.token_type() is not self.T_SYMBOL):
            raise TokenizerError("Token type must be {} to call the symbol() method".format(self.T_SYMBOL))
        return self._curr_token
    
    # Return the identifier
    # This should only get called if the token is a identifier (token_type == T_IDENTIFIER)
    def identifier(self):
        if (self.token_type() is not self.T_IDENTIFIER):
            raise TokenizerError("Token type must be {} to call the identifier() method".format(self.T_IDENTIFIER))
        return self._curr_token

    # Return the integer value
    # This should only get called if the token is a integer (token_type == T_INT_CONSTANT)
    def int_val(self):
        if (self.token_type() is not self.T_INT_CONSTANT):
            raise TokenizerError("Token type must be {} to call the int_val() method".format(self.T_INT_CONSTANT))
        return self._curr_token

    
    # Return the string value without double quotes
    # This should only get called if the token is a stribg (token_type == T_STRING_CONSTANT)
    def string_val(self):
        if (self.token_type() is not self.T_STRING_CONSTANT):
            raise TokenizerError("Token type must be {} to call the string_val() method".format(self.T_STRING_CONSTANT))
        return self._curr_token.strip('"')
    
    # generate token xml top level tag
    def token_xml_header(self):
        return "<tokens>\n"

    # close token top level tag
    def token_xml_trailer(self):
        return "</tokens>\n"

    # helper to generate an xml token
    def token_xml(self):
        token = self._curr_token.strip('"')
        if (self.token_type() == self.T_SYMBOL):
            if (self._curr_token == "<"):
                token = "&lt;"
            elif (self._curr_token == ">"):
                token = "&gt;"
            elif (self._curr_token == "&"):
                token = "&amp;"
        return "  <{}> {} </{}>\n".format(self.TYPE_XML[self.token_type()], token, self.TYPE_XML[self.token_type()])