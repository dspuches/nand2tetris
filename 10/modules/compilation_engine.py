from modules.jack_tokenizer import JackTokenizer
from modules.syntax_error import SyntaxError

class CompilationEngine:
    """Tokenizer class responsible for parsing jack source files into tokens

    Attributes:
        _fd -- output file descriptor
        _tkn -- tokenizer
        _indents -- track the number of indents to prepend before xml output
    """

    # Create a new tokenizer for the specified input stream
    # Make sure the tokenizer stream has at least one token
    # Advance to the first token
    # Call the recursive function to compile the class
    # After the recursion exits, there should be no more tokens to process
    def __init__(self, in_f, out_f):
        self._fd = out_f                            # output file handle
        self._tkn = JackTokenizer(in_f)             # tokenizer that parses the input into tokens
        self._indents = ""
        if not self._tkn.has_more_tokens():
            raise SyntaxError(self._tkn, "No tokens found in input file!")
        
        self._tkn.advance()                         # advance tokenizer once (to first token)
        # call the compile_class method
        self._compile_class()
        # make sure tokenizer has no more tokens. Raise exception if more tokens exist
        if (self._tkn.has_more_tokens()):
            raise SyntaxError(self._tkn, "Unexpected token found <{}>".format(self._tkn.token()))

    # Increase the indentation of the output by two spaces
    def _indent(self):
        self._indents = "{}  ".format(self._indents)
    
    # Decrease the indenation of the output by two spaces
    def _dedent(self):
        self._indents = self._indents[:-2]
    
    # Helper function to output a line to the output file
    # Prepends output with the appropriate indentation
    def _println(self, str):
        self._fd.write("{}{}\n".format(self._indents, str))

    # Helper function to output an xml token of the following format:
    # <type> value </type>
    def _print_xml_token(self, type, value):
        self._println("<{}> {} </{}>".format(type, value, type))
    
    # Helper method to determine if the token matches a type
    def _is_type(self, type):
        if self._tkn.token_type() == type:
            return True
        else:
            return False

    # Helper method to determine if current token is a keyword
    def _is_keyword(self):
        return self._is_type(self._tkn.T_KEYWORD)
    
    # Helper method to determine if current token is a symbol
    def _is_symbol(self):
        return self._is_type(self._tkn.T_SYMBOL)

    # Helper method to determine if current token is an identifier
    def _is_identifier(self):
        return self._is_type(self._tkn.T_IDENTIFIER)
    
    # Helper method to determine if the current token is in the provided list
    # The method to get the token is func, if this shouldn't be called, a tokenizer error
    # will be raised
    def _token_in(self, func, list):
        if func() in list:
            return True
        else:
            return False
    
    # Helper method to determine if the current token is equal to the provided symbol
    def _symbol_is(self, symbol):
        func = self._tkn.symbol
        return self._token_in(func, [symbol])
    
    # Helper method to determine if the current token is equal to the provided keyword
    def _keyword_is(self, keyword):
        func = self._tkn.keyword
        return self._token_in(func, [keyword])
    
     # Helper method to determine if the current token is in the provided list of keywords
    def _keyword_in(self, keyword_list):
        func = self._tkn.keyword
        return self._token_in(func, keyword_list)

    # Compile a class
    # Grammar:
    # 'class' className '{' classVarDec* subroutineDec * '}'
    def _compile_class(self):
        # make sure its a class symbol
        if ((not self._is_keyword()) or (not self._keyword_is(self._tkn.K_CLASS))):
            raise SyntaxError(self._tkn, "Expected keyword <class>, found <{}> instead".format(self._tkn.token()))

        # class superstructure
        self._println("<class>")
        self._indent()

        # class keyword
        self._print_xml_token("keyword", self._tkn.token())
        self._tkn.advance()

        # class name (identifier)
        if (not self._is_identifier()):
            raise SyntaxError(self._tkn, "Expected identifier, found <{}> instead".format(self._tkn.token()))
        self._print_xml_token("identifier", self._tkn.token())
        self._tkn.advance()

        # { symbol:
        if ((not self._is_symbol()) or (not self._symbol_is("{"))):
            raise SyntaxError(self._tkn, "Expected symbol <{{>, found <{}> instead".format(self._tkn.token()))
        self._print_xml_token("symbol", self._tkn.token())
        self._tkn.advance()

        # classVarDec*
        self._compile_class_var_dec()
        
        # subroutineDec*
        self._compile_subroutine()

        # } symbol
        if ((not self._is_symbol()) or (not self._symbol_is("}"))):
            raise SyntaxError(self._tkn, "Expected symbol <}}>, found <{}> instead".format(self._tkn.token()))
        self._print_xml_token("symbol", self._tkn.token())

        # close superstructure
        self._dedent()
        self._println("</class>")

    # Compile a class variable declaration
    # Grammar:
    # ('static' | 'field') type varName (',' varName)* ';'
    def _compile_class_var_dec(self):
        # return if no more variable declarations to process
        if not self._is_keyword():
            return
        if (not self._keyword_in([self._tkn.K_STATIC, self._tkn.K_FIELD])):
            return
        
        # classVarDec superstructure
        self._println("<classVarDec>")
        self._indent()

        # ('static' | 'field')
        self._print_xml_token("keyword", self._tkn.token())
        self._tkn.advance()

        # type
        self._compile_type()

        # varName
        if (not self._is_identifier()):
            raise SyntaxError(self._tkn, "Expected identifier, found <{}> instead".format(self._tkn.token()))
        self._print_xml_token("identifier", self._tkn.token())
        self._tkn.advance()

        # (',' varname)*
        self._compile_varname_list()

        # ; symbol
        if ((not self._is_symbol()) or (not self._symbol_is(";"))):
            raise SyntaxError(self._tkn, "Expected symbol <;>, found <{}> instead".format(self._tkn.token()))
        self._print_xml_token("symbol", self._tkn.token())
        self._tkn.advance()

        # close superstructure
        self._dedent()
        self._println("</classVarDec>")

        # process more classVarDec's (if there are any)
        self._compile_class_var_dec()
        return

    # Compile a type token
    # Grammar:
    # 'int' | 'char' | 'boolean' | className
    def _compile_type(self, include_void=False):
        valid_keywords = [self._tkn.K_INT, self._tkn.K_CHAR, self._tkn.K_BOOLEAN]
        if include_void:
            valid_keywords.append(self._tkn.K_VOID)
        if self._is_keyword():
            # if its a keyword that isnt int, char, or boolean, its invalid
            if (not self._keyword_in(valid_keywords)):
                lower_keywords = [each_string.lower() for each_string in valid_keywords]
                raise SyntaxError(self._tkn, "Invalid type <{}>. Expected {}, or className".format(self._tkn.token(), lower_keywords))
            
            # output keyword
            self._print_xml_token("keyword", self._tkn.token())
            self._tkn.advance()
        elif self._is_identifier():
            # output identifier
            self._print_xml_token("identifier", self._tkn.token())
            self._tkn.advance()
        else:
            lower_keywords = [each_string.lower() for each_string in valid_keywords]
            raise SyntaxError(self._tkn, "Invalid type <{}>. Expected {}, or className".format(self._tkn.token(), valid_keywords))

    # Compile a list of variable names
    # Grammar:
    # (',' varName)*
    def _compile_varname_list(self):
        # return if there are no more variables to process
        if not self._is_symbol():
            return
        if self._symbol_is(";"):
            return
        if not self._symbol_is(","):
            raise SyntaxError(self._tkn, "Invalid symbol. Expected ',' but found <{}>".format(self._tkn.token()))

        # , symbol
        self._print_xml_token("symbol", self._tkn.token())
        self._tkn.advance()

        # fail if it isnt an identifier
        if not self._is_identifier():
            raise SyntaxError(self._tkn, "Expected identifier, found <{}> instead.".format(self._tkn.token()))
        
        # varName
        self._print_xml_token("identifier", self._tkn.token())
        self._tkn.advance()

        # process more
        self._compile_varname_list()
        return

    # Compile a subroutine
    # Grammar:
    # ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
    def _compile_subroutine(self):
        # return if there are no more subroutines to process (not a keyword or not a function keyword)
        if not self._is_keyword():
            return
        valid_keywords = [
            self._tkn.K_METHOD,
            self._tkn.K_FUNCTION,
            self._tkn.K_CONSTRUCTOR,
        ]
        if (not self._keyword_in(valid_keywords)):
            return
        
        # subroutineDec superstructure
        self._println("<subroutineDec>")
        self._indent()

        # ('constructor' | 'function' | 'method')
        self._print_xml_token("keyword", self._tkn.token())
        self._tkn.advance()

        # ('void' | type)
        self._compile_type(True)

        # subroutineName
        if (not self._is_identifier()):
            raise SyntaxError(self._tkn, "Expected identifier, found <{}> instead".format(self._tkn.token()))
        self._print_xml_token("identifier", self._tkn.token())
        self._tkn.advance()

        # ( symbol

        # parameterList

        # } symbol

        # subroutineBody

        # close superstructure
        self._dedent()
        self._println("</subroutineDec>")

        # process more subroutines
        self._compile_subroutine()
        return
        

    def _compile_parameter_list(self):
        pass

    def _compile_var_dec(self):
        pass

    def _compile_statements(self):
        pass

    def _compile_do(self):
        pass

    def _compile_let(self):
        pass

    def _compile_while(self):
        pass

    def _compile_return(self):
        pass

    def _compile_if(self):
        pass

    def _compile_expression(self):
        pass

    def _compile_term(self):
        pass

    def _compile_expression_list(self):
        pass
    