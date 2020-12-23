from modules.jack_tokenizer import JackTokenizer
from modules.compilation_error import CompilationError

class CompilationEngine:
    def __init__(self, in_f, out_f):
        self._fd = out_f                            # output file handle
        self._tkn = JackTokenizer(in_f)             # tokenizer that parses the input into tokens
        self._indents = ""
        if not self._tkn.has_more_tokens():
            raise CompilationError("No tokens found in input file!")
        
        self._tkn.advance()                         # advance tokenizer once (to first token)
        if (self._tkn.token_type() == self._tkn.T_KEYWORD and self._tkn.keyword() == self._tkn.K_CLASS):
            # call the compile_class method
            self._compile_class()
        else:
            raise CompilationError("Expected keyword <class>, found <{}> instead".format(self._tkn.token()))
        # make sure tokenizer has no more tokens. Raise exception if more tokens exist
        if (self._tkn.has_more_tokens()):
            raise CompilationError("Unexpected token found <{}>".format(self._tkn.token()))

    def _indent(self):
        self._indents = "{}  ".format(self._indents)
    
    def _dedent(self):
        self._indents = self._indents[:-2]
    
    def _println(self, str):
        self._fd.write("{}{}\n".format(self._indents, str))

    def _compile_class(self):
        self._println("<class>")
        self._indent()
        self._println("<keyword> {} </keyword>".format(self._tkn.token()))
        self._tkn.advance()

        if (self._tkn.token_type() != self._tkn.T_IDENTIFIER):
            raise CompilationError("Expected identifier, found <{}> instead".format(self._tkn.token()))
        self._println("<identifier> {} </identifier>".format(self._tkn.token()))
        self._tkn.advance()

        if ((self._tkn.token_type() != self._tkn.T_SYMBOL) or (self._tkn.token() != "{")):
            raise CompilationError("Expected symbol <{{>, found <{}> instead".format(self._tkn.token()))
        self._println("<symbol> {} </symbol>".format(self._tkn.token()))
        self._tkn.advance()

        if ((self._tkn.token_type() != self._tkn.T_SYMBOL) or (self._tkn.token() != "}")):
            raise CompilationError("Expected symbol <}}>, found <{}> instead".format(self._tkn.token()))
        self._println("<symbol> {} </symbol>".format(self._tkn.token()))

        self._dedent()

        self._println("</class>")

    def _compile_class_var_dec(self):
        pass

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
    