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
    def _token_is_type(self, type):
        if self._tkn.token_type() == type:
            return True
        else:
            return False

    # Helper method to determine if current token is a keyword
    def _is_keyword(self):
        return self._token_is_type(self._tkn.T_KEYWORD)
    
    # Helper method to determine if current token is a symbol
    def _is_symbol(self):
        return self._token_is_type(self._tkn.T_SYMBOL)

    # Helper method to determine if current token is an identifier
    def _is_identifier(self):
        return self._token_is_type(self._tkn.T_IDENTIFIER)

    # Helper method to determine if current token is a variable type:
    # char, int, boolean, or identifier
    def _is_var_type(self):
        is_var_type = False
        valid_keywords = [self._tkn.K_BOOLEAN, self._tkn.K_INT, self._tkn.K_CHAR]
        # if keyword and char/int/boolean/identifier, true
        if (self._is_keyword()):
            if (self._tkn.keyword() in valid_keywords):
                is_var_type = True
        elif (self._is_identifier()):
            is_var_type = True
        return is_var_type
    
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

    # Helper method to raise a syntax error for an unexpected symbol
    def _symbol_syntax_error(self, symbol):
        raise SyntaxError(self._tkn, "Expected symbol <{}>, found <{}> instead".format(symbol, self._tkn.token()))

    # Helper method to raise a syntax error for an unexpected keyword
    def _keyword_syntax_error(self, keyword):
        raise SyntaxError(self._tkn, "Expected keyword <{}>, found <{}> instead".format(keyword, self._tkn.token()))

    # Helper method to raise a syntax error for a missing identifier
    def _identifier_syntax_error(self):
        raise SyntaxError(self._tkn, "Expected identifier, found <{}> instead".format(self._tkn.token()))

    def _type_syntax_error(self, valid_types):
        raise SyntaxError(self._tkn, "Expected type {}, found <{}> instead".format(valid_types, self._tkn.token()))

    # Helper method to compile an identifier
    # Checks to see if current token is an identifier, if not raises syntax error
    # Otherwise, it compiles the ident token
    def _compile_identifier(self):
        if (not self._is_identifier()):
            self._identifier_syntax_error()
        self._print_xml_token("identifier", self._tkn.token())
        self._tkn.advance()
    
    # Helper method to compile a symbol
    # Checks to see if current token is a symbol that matches the provided symbol, if not raises syntax error
    # Otherwise, it compiles the symbol
    def _compile_symbol(self, symbol, advance=True):
        if ((not self._is_symbol()) or (not self._symbol_is(symbol))):
            self._symbol_syntax_error(symbol)
        self._print_xml_token("symbol", self._tkn.token())
        if (advance):
            self._tkn.advance()
    
    # Helper method to compile a type token
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
                lower_keywords.append("className")
                self._type_syntax_error(lower_keywords)
            
            # output keyword
            self._print_xml_token("keyword", self._tkn.token())
            self._tkn.advance()
        elif self._is_identifier():
            # output identifier
            self._print_xml_token("identifier", self._tkn.token())
            self._tkn.advance()
        else:
            lower_keywords = [each_string.lower() for each_string in valid_keywords]
            lower_keywords.append("className")
            self._type_syntax_error(lower_keywords)

    # Compile a class
    # Grammar:
    # 'class' className '{' classVarDec* subroutineDec * '}'
    def _compile_class(self):
        # make sure its a class symbol
        if ((not self._is_keyword()) or (not self._keyword_is(self._tkn.K_CLASS))):
            self._keyword_syntax_error("class")

        self._println("<class>")                                # class superstructure
        self._indent()

        self._print_xml_token("keyword", self._tkn.token())     # class keyword
        self._tkn.advance()
        self._compile_identifier()                              # class name (identifier)
        self._compile_symbol("{")                               # { symbol:
        self._compile_class_var_dec()                           # classVarDec*
        self._compile_subroutine()                              # subroutineDec*
        self._compile_symbol("}", False)                        # } symbol, dont advance to next token (shouldnt be any more)

        self._dedent()                                          # close superstructure
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
        
        self._println("<classVarDec>")                          # classVarDec superstructure
        self._indent()

        self._print_xml_token("keyword", self._tkn.token())     # ('static' | 'field')
        self._tkn.advance()
        self._compile_type()                                    # type
        self._compile_identifier()                              # varName
        self._compile_varname_list()                            # (',' varname)*
        self._compile_symbol(";")                               # ; symbol

        self._dedent()                                          # close superstructure
        self._println("</classVarDec>")

        # process more classVarDec's (if there are any)
        self._compile_class_var_dec()
        return

    # Compile a list of variable names
    # Grammar:
    # (',' varName)*
    def _compile_varname_list(self):
        # return if there are no more variables to process
        if not self._is_symbol():
            return
        if self._symbol_is(";"):
            return

        self._compile_symbol(",")                               # , symbol
        self._compile_identifier()                              # varName
        self._compile_varname_list()                            # process more
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
        
        self._println("<subroutineDec>")                        # subroutineDec superstructure
        self._indent()

        self._print_xml_token("keyword", self._tkn.token())     # ('constructor' | 'function' | 'method')
        self._tkn.advance()
        self._compile_type(True)                                # ('void' | type)
        self._compile_identifier()                              # subroutineName
        self._compile_symbol("(")                               # ( symbol
        self._println("<parameterList>")                        # parameterList superstructure
        self._indent()
        self._compile_parameter_list()                          # parameterList
        self._dedent()                                          # close superstructure
        self._println("</parameterList>")
        self._compile_symbol(")")                               # ) symbol
        self._compile_subroutine_body()                         # subroutineBody

        self._dedent()                                          # close superstructure
        self._println("</subroutineDec>")

        # process more subroutines
        self._compile_subroutine()
        return
        
    # Compile a (possibly empty) parameter list
    # Grammar:
    # ((type varName) (',' type varName)*)?
    def _compile_parameter_list(self):
        # on entry, it should be a type
        if (not self._is_var_type()):
            return

        self._compile_type()                                    # type
        self._compile_identifier()                              # varName
        self._compile_parameter()                               # (',' type varName)*
    
    # Compile zero or more parameters
    # Grammar:
    # (',' type varName)*
    def _compile_parameter(self):
        # return if there are no more params to process
        if not self._is_symbol():
            return
        if self._symbol_is(")"):
            return
        
        self._compile_symbol(",")                               # , symbol
        self._compile_type()                                    # type
        self._compile_identifier()                              # varName

        # process more params
        self._compile_parameter()
        return
    
    # Compile a subroutine body
    # Grammar:
    # '{' varDec* statements '}'
    def _compile_subroutine_body(self):
        self._println("<subroutineBody>")                       # superstructure
        self._indent()

        self._compile_symbol("{")                               # { symbol
        self._compile_var_dec()                                 # varDec*
        self._compile_statements()                              # statements
        self._compile_symbol("}")                               # } symbol

        self._dedent()                                          # close superstructure
        self._println("</subroutineBody>")
    
    # Compile variable declaration(s)
    # Grammar
    # 'var' type varName (',' varName)* ';'
    def _compile_var_dec(self):
        # return if no more variable declarations to process
        if not self._is_keyword():
            return
        if (not self._keyword_is(self._tkn.K_VAR)):
            return
        
        self._println("<varDec>")                               # classVarDec superstructure
        self._indent()

        self._print_xml_token("keyword", self._tkn.token())     # 'var'
        self._tkn.advance()
        self._compile_type()                                    # type
        self._compile_identifier()                              # varName
        self._compile_varname_list()                            # (',' varname)*
        self._compile_symbol(";")                               # ; symbol
        
        self._dedent()                                          # close superstructure
        self._println("</varDec>")

        # process more varDec's (if there are any)
        self._compile_var_dec()
        return

    # Compile statements. Basically dispatches the handlers for each of the various statement types
    # until there are no more to process
    # Grammar:
    # statement*
    # statement grammar:
    # letStatement | ifStatement | whileStatement | doStatement | returnStatement
    def _compile_statements(self):
        valid_keywords = [
            self._tkn.K_LET,
            self._tkn.K_WHILE,
            self._tkn.K_RETURN,
            self._tkn.K_IF,
            self._tkn.K_DO,
        ]
        if (not self._is_keyword()):
            return
        if (not self._keyword_in(valid_keywords)):
            return
        
        keyword = self._tkn.keyword()

        if (keyword == self._tkn.K_LET):
            self._compile_let()
        elif (keyword == self._tkn.K_WHILE):
            self._compile_while()
        elif (keyword == self._tkn.K_RETURN):
            self._compile_return()
        elif (keyword == self._tkn.K_IF):
            self._compile_if()
        elif (keyword == self._tkn.K_DO):
            self._compile_do()
        
        self._compile_statements()

    # Compile a let statment. Assumes current token is a keyword = 'let'
    # Grammar:
    # 'let' varName ('[' expression ']')? '=' expression ';'
    def _compile_let(self):
        self._println("<letStatement>")                         # let superstructure
        self._indent()

        self._print_xml_token("keyword", self._tkn.token())     # let keyword
        self._tkn.advance()
        self._compile_identifier()                              # varName
        self._compile_symbol("=")                               # = symbol
        self._compile_expression()                              # expression
        self._compile_symbol(";")                               # ; symbol

        self._dedent()                                          # close superstructure
        self._println("</letStatement>")

    # Compile a do statement. Assumes current token is a keyword = "do"
    # Grammar:
    # do subroutineCall ';'
    def _compile_do(self):
        self._println("<doStatement>")                          # superstructure
        self._indent()

        self._print_xml_token("keyword", self._tkn.token())     # do keyword
        self._tkn.advance()
        self._compile_subroutine_call()                         # subroutineCall
        self._compile_symbol(";")                               # ; symbol

        self._dedent()                                          # close superstructure
        self._println("</doStatement>")

    # Compile the subroutineCall portion of a do statement
    # Grammar:
    # subroutineName '(' expressionList ')' | (className | varName) '.' subroutineName '(' expressionList ')'
    def _compile_subroutine_call(self):
        self._compile_identifier()                              # subroutineName
        self._compile_symbol("(")                               # ( symbol
        self._compile_expression_list()                         # expressionList
        self._compile_symbol(")")                               # ) symbol

    # Compile a let statment. Assumes current token is a keyword = 'while'
    # Grammar:
    # 'while' '(' expression ')' '{' statements '}'
    def _compile_while(self):
        self._println("<whileStatement>")                       # superstructure
        self._indent()
        
        self._print_xml_token("keyword", self._tkn.token())     # while keyword
        self._tkn.advance()
        self._compile_symbol("(")                               # ( symbol
        self._compile_expression()                              # expression
        self._compile_symbol(")")                               # ) symbol
        self._compile_symbol("{")                               # { symbol
        self._compile_statements()                              # statements
        self._compile_symbol("}")                               # } symbol

        self._dedent()                                          # close superstructure
        self._println("</whileStatement>")

    # Compile a return statment. Assumes current token is a keyword = 'return'
    # Grammar:
    # 'return' expression? ';'
    def _compile_return(self):
        
        self._println("<returnStatement>")                      # superstructure
        self._indent()

        self._print_xml_token("keyword", self._tkn.token())     # return keyword
        self._tkn.advance()

        # if the next token is not a ; symbol, try to compile expression
        if not self._is_symbol():
            self._compile_expression()
        elif not self._symbol_is(";"):
            self._compile_expression()

        self._compile_symbol(";")                               # ; symbol

        self._dedent()                                          # close superstructure
        self._println("</returnStatement>")

    # Compile an if/else statement. Assumes the next token is keyword == 'if'
    # Grammar:
    # 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
    def _compile_if(self):
        self._println("<ifStatement>")                          # superstructure
        self._indent()

        self._print_xml_token("keyword", self._tkn.token())     # if keyword
        self._tkn.advance()
        self._compile_symbol("(")                               # ( symbol
        self._compile_expression()                              # expression
        self._compile_symbol(")")                               # ) symbol
        self._compile_symbol("{")                               # { symbol
        self._compile_statements()                              # statements
        self._compile_symbol("}")                               # } symbol
        self._compile_else()                                    # ('else' '{' statements '}')?

        self._dedent()                                          # close superstructure
        self._println("</ifStatement>")
    
    # Compiles the else portion of an if/else block if there is one.
    # Grammar:
    # ('else' '{' statements '}')?
    def _compile_else(self):
        # Return if the first token isnt "else"
        if not self._is_keyword():
            return
        if not self._keyword_is(self._tkn.K_ELSE):
            return
        
        self._print_xml_token("keyword", self._tkn.token())     # else keyword
        self._tkn.advance()
        self._compile_symbol("{")                               # { symbol
        self._compile_statements()                              # statements
        self._compile_symbol("}")                               # } symbol

    # First pass of expression is to only allow an identifier as expression
    # Grammar:
    # identifier
    def _compile_expression(self):
        
        self._println("<expression>")                           # let superstructure
        self._indent()

        self._compile_identifier()                              # identifier

        self._dedent()                                          # close superstructure
        self._println("</expression>")

    def _compile_term(self):
        pass

    # First pass of expressionList is to only allow an identifier as expressionList
    # Grammar:
    # identifier
    def _compile_expression_list(self):
        self._compile_identifier()                              # identifier
    