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
        self._start = 0                             # the index of the start of the token in current line
        self._curr = 0                              # the current index in the current line
        self._next_token = self._get_next_token()   # attempt to get the next token

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

    def _curr_char(self):
        return self._line[self._curr_char]

    # this helper method will return the next token in the stream
    def _get_next_token(self):
        token = None
        scanning = True

        if (self._line == None):
            self._read_next_line()

        if (self._line == ''):
            return token

        while (scanning):
            # print("start:{}".format(self._start))
            # print("curr:{}".format(self._curr))
            # print("line:*{}*".format(self._line))

            # EOF
            if (self._line == ''):
                break

            # import pdb;pdb.set_trace()
            if (self._curr == self._line_length or self._line[self._curr] == '\n'):
                # end of line
                # ignore blank lines
                if (self._curr != self._start):
                    token = self._line[self._start:self._curr] 
                    scanning = False
                self._read_next_line()
            elif (self._line[self._curr] in self.SYMBOLS):
                if (self._start == self._curr):
                    token = self._line[self._curr]
                    scanning = False
                    self._bump()
                else:
                    token = self._line[self._start:self._curr]
                    scanning = False
                    self._align()
            elif (self._line[self._curr] == ' '):
                # current is a space, we have a token if start and curr are not the same. Otherwise, bump
                if (self._start != self._curr):
                    token = self._line[self._start:self._curr] 
                    scanning = False
                self._bump()
            
            elif (scanning):
                # if we got this far, no tokens have been found yet and we havent reached end of line or EOF
                # if we are still scanning, keep increasing _curr
                self._curr += 1

        #self._read_next_line()
        return token
        
        # while (self._curr <= self._line_length):
            
        #     # start is at the end of the line or no lines have been read yet
        #     if (self._start == self._line_length or self._line == None):
        #         if (self._read_next_line() == False):
        #             return None

        #     # we are at the last character of this line
        #     if (self._curr == self._line_length):
        #         extracted = self._line[self._start:self._curr]      # extract start to end of line
        #         self._align()                                       # move start to EOL
        #         if (extracted != ""):                               # dont return empty tokens
        #             return extracted
                               
        #     # if current character is a space
        #     if (self._line[self._curr] == ' '):
        #         # continue on if start and curr point to the same space character
        #         if (self._curr == self._start):
        #             self._bump()
        #             continue
        #         extracted = self._line[self._start:self._curr]      # extract the token
        #         self._bump()
        #         if (extracted != ""):                               # dont return empty tokens
        #             return extracted
                
        #     # if current character is a symbol
        #     if (self._line[self._curr] in self.SYMBOLS):
        #         if self._start == self._curr:                       # if start and curr are the same, we want to extract the symbol itself
        #             self._curr += 1

        #         extracted = self._line[self._start:self._curr]      # extract the token
        #         self._align()

        #         if (extracted != ""):                               # dont return empty tokens
        #             return extracted

        #     self._curr += 1

    def has_more_tokens(self):
        if self._next_token is None:
            return False
        else:
            return True

    def advance(self):
        if self._next_token is None:
            raise TokenizerError("Cannot call advance if there are no more tokens to process")
        self._next_token = self._get_next_token()

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