from modules.jack_tokenizer import JackTokenizer
from modules.compilation_error import CompilationError

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
    # Make sure the first token is a "class" keyword
    # Call the recursive function to compile the class
    # After the recursion exits, there should be no more tokens to process
    def __init__(self, in_f, out_f):
        self._fd = out_f                            # output file handle
        self._tkn = JackTokenizer(in_f)             # tokenizer that parses the input into tokens
        self._indents = ""
        if not self._tkn.has_more_tokens():
            raise CompilationError("No tokens found in input file!")
        
        self._tkn.advance()                         # advance tokenizer once (to first token)
        # call the compile_class method
        self._compile_class()
        # make sure tokenizer has no more tokens. Raise exception if more tokens exist
        if (self._tkn.has_more_tokens()):
            raise CompilationError("Unexpected token found <{}>".format(self._tkn.token()))

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

    # Compile a class
    # Grammar:
    # 'class' className '{' classVarDec* subroutineDec * '}'
    def _compile_class(self):
        # make sure its a class symbol
        if ((self._tkn.token_type() != self._tkn.T_KEYWORD) or (self._tkn.keyword() != self._tkn.K_CLASS)):
            raise CompilationError("Expected keyword <class>, found <{}> instead".format(self._tkn.token()))

        # class superstructure
        self._println("<class>")
        self._indent()

        # class keyword
        self._print_xml_token("keyword", self._tkn.token())
        self._tkn.advance()

        # class name (identifier)
        if (self._tkn.token_type() != self._tkn.T_IDENTIFIER):
            raise CompilationError("Expected identifier, found <{}> instead".format(self._tkn.token()))
        self._print_xml_token("identifier", self._tkn.token())
        self._tkn.advance()

        # { symbol
        if ((self._tkn.token_type() != self._tkn.T_SYMBOL) or (self._tkn.token() != "{")):
            raise CompilationError("Expected symbol <{{>, found <{}> instead".format(self._tkn.token()))
        self._print_xml_token("symbol", self._tkn.token())
        self._tkn.advance()

        # if next token is static or field keyword, process classVarDec*
        # if self._tkn.token_type() == self._tkn.T_KEYWORD:
        #     if (self._tkn.keyword() == self._tkn.K_STATIC) or (self._tkn.keyword() == self._tkn.K_FIELD):
        self._compile_class_var_dec()
        
        # if next token is constructor, function, or method keyword, process subroutineDec*
        

        # } symbol
        if ((self._tkn.token_type() != self._tkn.T_SYMBOL) or (self._tkn.token() != "}")):
            raise CompilationError("Expected symbol <}}>, found <{}> instead".format(self._tkn.token()))
        self._print_xml_token("symbol", self._tkn.token())

        # close superstructure
        self._dedent()
        self._println("</class>")

    # Compile a class variable declaration
    # Grammar:
    # ('static' | 'field') type varName (',' varName)* ';'
    def _compile_class_var_dec(self):
        # return if no more variable declarations to process
        if self._tkn.token_type() != self._tkn.T_KEYWORD:
            return
        if (self._tkn.keyword() != self._tkn.K_STATIC) and (self._tkn.keyword() != self._tkn.K_FIELD):
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
        if (self._tkn.token_type() != self._tkn.T_IDENTIFIER):
            raise CompilationError("Expected identifier, found <{}> instead".format(self._tkn.token()))
        self._print_xml_token("identifier", self._tkn.token())
        self._tkn.advance()

        # ; symbol
        if ((self._tkn.token_type() != self._tkn.T_SYMBOL) or (self._tkn.token() != ";")):
            raise CompilationError("Expected symbol <;>, found <{}> instead".format(self._tkn.token()))
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
    def _compile_type(self):
        if self._tkn.token_type() == self._tkn.T_KEYWORD:
            # if its a keyword that isnt int, char, or boolean, its invalid
            if (self._tkn.keyword() != self._tkn.K_INT) and (self._tkn.keyword() != self._tkn.K_CHAR) and (self._tkn.keyword() != self._tkn.K_BOOLEAN):
                raise CompilationError("Invalid type <{}>. Expected char, int, boolean, or className".format(self._tkn.token()))
            # output keyword
            self._print_xml_token("keyword", self._tkn.token())
            self._tkn.advance()
        elif self._tkn.token_type() == self._tkn.T_IDENTIFIER:
            # output identifier
            self._print_xml_token("identifier", self._tkn.token())
            self._tkn.advance()
        else:
            raise CompilationError("Invalid type <{}>. Expected char, int, boolean, or className".format(self._tkn.token()))

    def _compile_subroutine(self):
        pass

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
    