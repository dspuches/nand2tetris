from .tokenizer_error import TokenizerError


class JackTokenizer():
    """Tokenizer class responsible for parsing jack source files into tokens

    Attributes:
        _infile -- jack input as python list
    """
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
    
    def __init__(self, infile):
        self._fd = open(infile)                     # file descriptor
        self._line = None                           # read a line
        self._line_count = 0                        # start off the counter at 1
        self._line_length = 0                       # store length of current line
        self._start = 0                             # the index of the start of the lexeme in current line
        self._curr = 0                              # the current index in the current line
        self._next_lexeme = self._get_next_lexeme() # attempt to get the next lexeme

    def _read_next_line(self):
        self._line = self._fd.readline()
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
    def _peek(self):
        if (self._curr + 1 < self._line_length):
            return self._line[self._curr + 1]
        else:
            return ""
    
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
                if (self._line == ''):
                    #EOF without finding closure. Raise exception
                    raise TokenizerError("Reached EOF before finding closing */ to multiline comment")
                # end of current line, move to next
                self._read_next_line()
                
            elif (self._line[self._curr] == "*"):
                # if we find a *, check if its the end of comment
                if (self._peek() == "/"):
                    # end of comment
                    scanning = False
                    self._bump()
                    self._bump()
                else:
                    self._curr += 1
            else:
                self._curr += 1

    # this method will return the next lexeme in the stream
    def _get_next_lexeme(self):
        lexeme = None
        scanning = True

        if (self._line == None):
            self._read_next_line()

        # EOF
        if (self._line == ''):
            return lexeme

        while (scanning):
            # EOF encountered while processing lexemes
            if (self._line == ''):
                break

            if (self._curr == self._line_length or self._line[self._curr] == '\n'):
                # end of line. we have a lexeme if start != curr
                if (self._curr != self._start):
                    lexeme = self._line[self._start:self._curr] 
                    scanning = False
                self._read_next_line()
            elif (self._line[self._curr] == '"'):
                # string constant
                scanning_string = True
                self._curr += 1
                while (scanning_string):
                    if (self._curr == self._line_length):
                        # end of line
                        raise TokenizerError("Unterminated string constant {}".format(self._line[self._start:self._curr]))
                    elif (self._line[self._curr] == '"'):
                        # found closing quote
                        lexeme = self._line[self._start:self._curr+1] 
                        scanning_string = False
                        scanning = False
                        self._bump()
                    else:
                        # keep scanning
                        self._curr += 1

            elif (self._line[self._curr] in self.SYMBOLS):
                # found a symbol
                if (self._start == self._curr):
                    # if start == curr, the symbol is the lexeme...unless its a comment
                    if (self._line[self._curr] == "/"):
                        # check if it is a comment and skip them if it is
                        if (self._peek() == "/"):
                            self._handle_singleline_comment()
                            continue
                        elif (self._peek() == "*"):
                            self._handle_multiline_comment()
                            continue
                    
                    # not a comment, so its a lexeme
                    lexeme = self._line[self._curr]
                    scanning = False
                    self._bump()
                else:
                    # otherwise, the previous text from start up to curr is the lexeme
                    lexeme = self._line[self._start:self._curr]
                    scanning = False
                    self._align()
            elif (self._line[self._curr] == ' '):
                # curr is a space, we have a lexeme if start and curr are not the same. Otherwise, bump
                if (self._start != self._curr):
                    lexeme = self._line[self._start:self._curr] 
                    scanning = False
                self._bump()
            
            elif (scanning):
                # if we got this far, no lexemes have been found yet and we havent reached end of line or EOF
                self._curr += 1

        return lexeme

    def has_more_tokens(self):
        if self._next_lexeme is None:
            return False
        else:
            return True

    def advance(self):
        if self._next_lexeme is None:
            raise TokenizerError("Cannot call advance if there are no more lexemes to process")
        self._next_lexeme = self._get_next_lexeme()

    def token_type(self):
        pass

    def keyword(self):
        pass

    def symbol(self):
        pass
    
    def identifier(self):
        pass

    def int_val(self):
        pass

    def string_val(self):
        pass