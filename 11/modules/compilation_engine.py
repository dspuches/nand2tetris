from modules.jack_tokenizer import JackTokenizer
from modules.symbol_table import SymbolTable
from modules.vm_writer import VmWriter
from errors.syntax_error import SyntaxError

class CompilationEngine:
    # Create a new tokenizer for the specified input stream
    # Make sure the tokenizer stream has at least one token
    # Advance to the first token
    # Call the recursive function to compile the class
    # After the recursion exits, there should be no more tokens to process
    #
    # Currently, the compilation engine assumes error free Jack code.
    # The compiler does syntax checking, but semantics are mostly ignored.
    # Semantic checking can be implemented as a future enhancement
    def __init__(self, in_f, out_f):
        self._fd = out_f                            # output file handle
        self._tkn = JackTokenizer(in_f)             # tokenizer that parses the input into tokens
        self._symbol_table = SymbolTable()
        self._vmw = VmWriter(out_f)
        self._while_index = 0                       # keep track of nested whiles
        self._if_index = 0                          # keep track of nested ifs
        self._indents = ""
        self._class_name = ""
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
    
    # Helper function to output an opening superstructrue xml tag and indent
    def _open_superstructure(self, name):
        self._println("<{}>".format(name))
        self._indent()
    
    # Helper function to dedent and output an closing superstructrue xml tag
    def _close_superstructure(self, name):
        self._dedent()
        self._println("</{}>".format(name))
    
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
    
    # Helper method to determine if current token is a stringConstant
    def _is_string_constant(self):
        return self._token_is_type(self._tkn.T_STRING_CONSTANT)

    # Helper method to determine if current token is an integerConstant
    def _is_int_constant(self):
        return self._token_is_type(self._tkn.T_INT_CONSTANT)
    
    # Helper method to determine if current token is a keywordConstant
    def _is_keyword_constant(self):
        valid_keywords = [
            self._tkn.K_TRUE,
            self._tkn.K_FALSE,
            self._tkn.K_NULL,
            self._tkn.K_THIS,
        ]
        if self._is_keyword() and (self._tkn.keyword() in valid_keywords):
            return True
        else:
            return False
        
    # Helper method to determine if current token is a unaryOp
    # '-' | '~'
    def _is_unary_op(self):
        is_op = False
        if self._is_symbol():
            if self._symbol_is("-") or self._symbol_is("~"):
                is_op = True
        return is_op

    # Helper method to determine if the current token can be considered the start of a term
    # Return true if:
    # integerConstant
    # stringConstant
    # keywordConstant - 'true' | 'false' | 'null' | 'this'
    # identifier - varName
    # unaryOp - '-' | '~'
    # '('
    def _is_term_start(self):
        is_term = False

        if self._is_identifier() or self._is_int_constant() or self._is_keyword_constant() or self._is_string_constant():
            is_term = True
        elif self._is_symbol() and self._symbol_is("("):
            is_term = True
        
        return is_term
    
    # Helper method to determine if token is an op
    # Valid ops: + - * / & | < > =
    def _is_op(self):
        is_op = False
        valid_ops = [
            '+',
            '-',
            '*',
            '/',
            '&',
            '|',
            '<',
            '>',
            '=',
        ]
        if self._is_symbol():
            if self._tkn.symbol() in valid_ops:
                is_op = True
        return is_op

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

    # Helper method to raise a syntax error for an invalid type
    def _type_syntax_error(self, valid_types):
        raise SyntaxError(self._tkn, "Expected type {}, found <{}> instead".format(valid_types, self._tkn.token()))

    # Helper method to raise a syntax error for an unexpected token in an expression
    def _expression_syntax_error(self):
        raise SyntaxError(self._tkn, "Unexpected token encountered in expression: <{}>".format(self._tkn.token()))

    # Helper method to raise syntax error for unexpected token when processing an integer constant
    def _integer_syntax_error(self):
        raise SyntaxError(self._tkn, "Expected integer constant, found <{}> instead".format(self._tkn.token()))

    # Helper method to raise syntax error for unexpected token when processing an integer constant
    def _string_syntax_error(self):
        raise SyntaxError(self._tkn, "Expected string constant, found <{}> instead".format(self._tkn.token()))

    # Helper method to compile an identifier
    # Checks to see if current token is an identifier, if not raises syntax error
    # Otherwise, it compiles the ident token
    def _compile_identifier(self):
        if (not self._is_identifier()):
            self._identifier_syntax_error()
        identifier = self._tkn.token()
        self._tkn.advance()
        return identifier
    
    # Compile a symbol
    # Checks to see if current token is a symbol that matches the provided symbol, if not raises syntax error
    # Otherwise, it compiles the symbol
    def _compile_symbol(self, symbol, advance=True):
        if ((not self._is_symbol()) or (not self._symbol_is(symbol))):
            self._symbol_syntax_error(symbol)
        
        token = self._tkn.token()
        if (token == "<"):
            token = "&lt;"
        elif (token == ">"):
            token = "&gt;"
        elif (token == "&"):
            token = "&amp;"
            
        if (advance):
            self._tkn.advance()
    
    # Compile a type token
    # Grammar:
    # 'int' | 'char' | 'boolean' | className
    def _compile_type(self, include_void=False):
        valid_keywords = [self._tkn.K_INT, self._tkn.K_CHAR, self._tkn.K_BOOLEAN]
        type = self._tkn.token()
        if include_void:
            valid_keywords.append(self._tkn.K_VOID)
        if self._is_keyword():
            # if its a keyword that isnt int, char, or boolean, its invalid
            if (not self._keyword_in(valid_keywords)):
                lower_keywords = [each_string.lower() for each_string in valid_keywords]
                lower_keywords.append("className")
                self._type_syntax_error(lower_keywords)
            
            self._tkn.advance()
        elif self._is_identifier():
            self._tkn.advance()
        else:
            lower_keywords = [each_string.lower() for each_string in valid_keywords]
            lower_keywords.append("className")
            self._type_syntax_error(lower_keywords)
        return type

    # Compile a class
    # Grammar:
    # 'class' className '{' classVarDec* subroutineDec * '}'
    def _compile_class(self):
        # make sure its a class symbol
        if ((not self._is_keyword()) or (not self._keyword_is(self._tkn.K_CLASS))):
            self._keyword_syntax_error("class")

        self._tkn.advance()                                     # class keyword
        self._class_name = self._compile_identifier()                 # class name (identifier)
        self._compile_symbol("{")                               # { symbol:
        self._compile_class_var_dec()                           # classVarDec*
        self._compile_subroutine()                              # subroutineDec*
        self._compile_symbol("}", False)                        # } symbol, dont advance to next token (shouldnt be any more)

    # Compile a class variable declaration
    # Grammar:
    # ('static' | 'field') type varName (',' varName)* ';'
    def _compile_class_var_dec(self):
        # return if no more variable declarations to process
        if not self._is_keyword():
            return
        if (not self._keyword_in([self._tkn.K_STATIC, self._tkn.K_FIELD])):
            return
        
        kind = self._tkn.token()
        self._tkn.advance()                                     # ('static' | 'field')
        type = self._compile_type()                             # type
        name = self._compile_identifier()                       # varName
        self._symbol_table.define(name, type, kind)
        self._compile_varname_list(type, kind)                  # (',' varname)*
        self._compile_symbol(";")                               # ; symbol

        # process more classVarDec's (if there are any)
        self._compile_class_var_dec()

        # Allocate
        return

    # Compile a list of variable names
    # Grammar:
    # (',' varName)*
    def _compile_varname_list(self, type, kind):
        # return if there are no more variables to process
        if not self._is_symbol():
            return
        if self._symbol_is(";"):
            return

        self._compile_symbol(",")                               # , symbol
        name = self._compile_identifier()                       # varName
        self._symbol_table.define(name, type, kind)
        self._compile_varname_list(type, kind)                  # process more
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

        self._symbol_table.start_method()                       # reset method scope

        # determine if this method is a constructor
        is_constructor = False
        is_method = False
        if self._tkn.keyword() == self._tkn.K_CONSTRUCTOR:
            is_constructor = True
        elif self._tkn.keyword() == self._tkn.K_METHOD:
            is_method = True
        
        self._tkn.advance()                                     # ('constructor' | 'function' | 'method')
        self._compile_type(True)                                # ('void' | type)
        method_name = self._compile_identifier()                # subroutineName
        method_name = "{}.{}".format(self._class_name, method_name)
        if is_method:
            self._symbol_table.define("this", self._class_name, SymbolTable.K_ARG)
        self._compile_symbol("(")                               # ( symbol
        self._compile_parameter_list()                          # parameterList
        self._compile_symbol(")")                               # ) symbol
        self._compile_subroutine_body(method_name, is_constructor, is_method)  # subroutineBody

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

        kind = SymbolTable.K_ARG
        type = self._compile_type()                             # type
        name = self._compile_identifier()                       # varName
        self._symbol_table.define(name, type, kind)
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
        
        kind = SymbolTable.K_ARG
        self._compile_symbol(",")                               # , symbol
        type = self._compile_type()                             # type
        name = self._compile_identifier()                       # varName
        self._symbol_table.define(name, type, kind)

        # process more params
        self._compile_parameter()
        return
    
    # Compile a subroutine body
    # Grammar:
    # '{' varDec* statements '}'
    def _compile_subroutine_body(self, method_name, is_constructor, is_method):
        self._compile_symbol("{")                               # { symbol
        self._compile_var_dec()                                 # varDec*
        self._vmw.write_function(method_name, self._symbol_table.var_count(SymbolTable.K_VAR))

        if is_constructor:
            # allocate memory for the object instance and set this to point to the new memory (pointer[0])
            num_fields = self._symbol_table.var_count(self._symbol_table.K_FIELD)
            self._vmw.write_push(VmWriter.S_CONSTANT, num_fields)
            self._vmw.write_call("Memory.alloc", 1)
            self._vmw.write_pop(VmWriter.S_POINTER, 0)
        elif is_method:
            # first "hidden" argument is this
            self._vmw.write_push(VmWriter.S_ARGUMENT, 0)
            self._vmw.write_pop(VmWriter.S_POINTER, 0)

        self._compile_statements()                              # statements
        self._compile_symbol("}")                               # } symbol
        self._if_index = 0
        self._while_index = 0
    
    # Compile variable declaration(s)
    # Grammar
    # 'var' type varName (',' varName)* ';'
    def _compile_var_dec(self):
        # return if no more variable declarations to process
        if not self._is_keyword():
            return
        if (not self._keyword_is(self._tkn.K_VAR)):
            return
        
        kind = self._tkn.token()
        self._tkn.advance()                                     # 'var'
        type = self._compile_type()                             # type
        name = self._compile_identifier()                       # varName
        self._symbol_table.define(name, type, kind)
        self._compile_varname_list(type, kind)                  # (',' varname)*
        self._compile_symbol(";")                               # ; symbol

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
        self._tkn.advance()                                     # let keyword
        var_name = self._compile_identifier()                   # varName
        is_array = self._compile_array_expression(var_name)     # ('[' expression ']')?
        self._compile_symbol("=")                               # = symbol
        self._compile_expression()                              # expression
        self._compile_symbol(";")                               # ; symbol

        if is_array:
            # pop temp 0 - return value of right side of = expression
            self._vmw.write_pop(VmWriter.S_TEMP, 0)
            # pop pointer 1 aka that = *(array[index])
            self._vmw.write_pop(VmWriter.S_POINTER, 1)
            # push temp 0
            self._vmw.write_push(VmWriter.S_TEMP, 0)
            # pop that 0 - array[index] = temp 0
            self._vmw.write_pop(VmWriter.S_THAT, 0)


        else:
            # pop the return value directly to the non-array variable
            self._vmw.write_pop(self._symbol_table.segment_of(var_name), self._symbol_table.index_of(var_name))

    # Compile a do statement. Assumes current token is a keyword = "do"
    # Grammar:
    # do subroutineCall ';'
    def _compile_do(self):
        self._tkn.advance()                                     # do keyword
        self._compile_subroutine_call()                         # subroutineCall
        self._compile_symbol(";")                               # ; symbol
        self._vmw.write_pop(VmWriter.S_TEMP, 0)                 # pop the return value (0) and ignore

    # Compile the subroutineCall portion of a do statement
    # Grammar:
    # subroutineName '(' expressionList ')' | (className | varName) '.' subroutineName '(' expressionList ')'
    def _compile_subroutine_call(self):
        id = self._compile_identifier()                # subroutineName | className | varName
        num_exp = 0

        if self._is_symbol() and self._symbol_is("."):
            # id is either className or varName
            # if it is varName (exists in symbol table), push to stack as "hidden argument"
            if self._symbol_table.kind_of(id) != self._symbol_table.K_NONE:
                self._vmw.write_push(self._symbol_table.segment_of(id), self._symbol_table.index_of(id))
                id = self._symbol_table.type_of(id)             # update ID to be className
                num_exp += 1

            self._compile_symbol(".")                           # . symbol
            temp = self._compile_identifier()                   # subroutineName
            id = "{}.{}".format(id, temp)
        else:
            # push hidden argument this, and set id to class_name.method_name
            self._vmw.write_push(VmWriter.S_POINTER, 0)
            id = "{}.{}".format(self._class_name, id)
            num_exp += 1

        self._compile_symbol("(")                               # ( symbol
        num_expressions = self._compile_expression_list(num_exp)    # expressionList
        self._vmw.write_call(id, num_expressions)
        self._compile_symbol(")")                               # ) symbol

    # Compile a let statment. Assumes current token is a keyword = 'while'
    # Grammar:
    # 'while' '(' expression ')' '{' statements '}'
    def _compile_while(self):
        self._tkn.advance()                                     # while keyword
        start_label = "WHILE_EXP{}".format(self._while_index)
        end_label = "WHILE_END{}".format(self._while_index)
        self._vmw.write_label(start_label)
        self._while_index += 1
        self._compile_symbol("(")                               # ( symbol
        self._compile_expression()                              # expression
        self._vmw.write_arithmetic("not")
        self._vmw.write_if(end_label)
        self._compile_symbol(")")                               # ) symbol
        self._compile_symbol("{")                               # { symbol
        self._compile_statements()                              # statements
        self._vmw.write_goto(start_label)
        self._compile_symbol("}")                               # } symbol
        self._vmw.write_label(end_label)

    # Compile a return statment. Assumes current token is a keyword = 'return'
    # Grammar:
    # 'return' expression? ';'
    def _compile_return(self):
        self._tkn.advance()                                     # return keyword
        return_exp = False

        # if the next token is not a ; symbol, try to compile expression and push the value onto the stack
        if not self._is_symbol():
            self._compile_expression()
            return_exp = True
        elif not self._symbol_is(";"):
            self._compile_expression()
            return_exp = True
        
        # no expression, so 0 must be pushed onto stack
        if not return_exp:
            self._vmw.write_push(VmWriter.S_CONSTANT, 0)


        self._compile_symbol(";")                               # ; symbol
        self._vmw.write_return()

    # Compile an if/else statement. Assumes the next token is keyword == 'if'
    # Grammar:
    # 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
    def _compile_if(self):
        true_label = "IF_TRUE{}".format(self._if_index)
        false_label = "IF_FALSE{}".format(self._if_index)
        end_label = "IF_END{}".format(self._if_index)
        self._if_index += 1
        self._tkn.advance()                                     # if keyword
        self._compile_symbol("(")                               # ( symbol
        self._compile_expression()                              # expression
        self._compile_symbol(")")                               # ) symbol
        self._vmw.write_if(true_label)
        self._vmw.write_goto(false_label)
        self._vmw.write_label(true_label)
        self._compile_symbol("{")                               # { symbol
        self._compile_statements()                              # statements
        self._compile_symbol("}")                               # } symbol
        self._compile_else(end_label, false_label)                                    # ('else' '{' statements '}')?
    
    # Compiles the else portion of an if/else block if there is one.
    # Grammar:
    # ('else' '{' statements '}')?
    def _compile_else(self, end_label, false_label):
        # Return if the first token isnt "else"
        if not self._is_keyword():
            self._vmw.write_label(false_label)
            return
        if not self._keyword_is(self._tkn.K_ELSE):
            self._vmw.write_label(false_label)
            return

        self._vmw.write_goto(end_label)     
        self._vmw.write_label(false_label)
        
        self._tkn.advance()                                     # else keyword
        self._compile_symbol("{")                               # { symbol
        self._compile_statements()                              # statements
        self._vmw.write_label(end_label)
        self._compile_symbol("}")                               # } symbol

    # Compile expression
    # Grammar:
    # term (op term)*
    def _compile_expression(self):
        self._compile_term()                                    # term
        self._compile_op_term()                                 # (op term)*

    # Compile zero or more op terms
    # Grammar:
    # (op term)*
    def _compile_op_term(self):
        if self._is_op():
            # if token is an op, process op token
            op = self._tkn.symbol()
            self._compile_symbol(self._tkn.symbol())
            self._compile_term()
            if op == "+":
                self._vmw.write_arithmetic("add")
            elif op == "*":
                self._vmw.write_call("Math.multiply", 2)
            elif op == "/":
                self._vmw.write_call("Math.divide", 2)
            elif op == "<":
                self._vmw.write_arithmetic("lt")
            elif op == ">":
                self._vmw.write_arithmetic("gt")
            elif op == "&":
                self._vmw.write_arithmetic("and")
            elif op == "=":
                self._vmw.write_arithmetic("eq")
            elif op == "-":
                self._vmw.write_arithmetic("sub")
        else:
            return
        
        # recursively process more op term pairs
        self._compile_op_term()

    # Compile term
    # Grammar:
    # integerConstant | stringConstant | keywordConstant | varName |
    # varName '[' expression ']' | subroutineCall | '(' expression ')'
    # unaryOp term
    def _compile_term(self):
        
        if self._is_int_constant():
            self._compile_int_constant()                        # integerConstant
        elif self._is_string_constant():
            self._compile_string_constant()                     # stringConstant
        elif self._is_keyword_constant():
            self._compile_keyword_constant()                    # keywordConstant
        elif self._is_unary_op():
            self._compile_unary_op()                            # unaryOp
        elif self._is_symbol() and self._symbol_is("("):
            self._compile_expression_block()                    # '(' expression ')'
        elif self._is_identifier():
            next_token = self._tkn.next_token()
            if next_token == "." or next_token == "(":
                self._compile_subroutine_call()
            else:
                var_name = self._compile_identifier()
                is_array = self._compile_array_expression(var_name)        # varName | varName '[' expression ']'

                if is_array:
                    # pop pointer 1 - this = *array[index]
                    self._vmw.write_pop(VmWriter.S_POINTER, 1)
                    # push that 0 - push array[index]
                    self._vmw.write_push(VmWriter.S_THAT, 0)
                else:
                    # push the value of the non-array variable onto the stack
                    self._vmw.write_push(self._symbol_table.segment_of(var_name), self._symbol_table.index_of(var_name))
        else:
            self._expression_syntax_error()                     # No valid term matches found


    # Compile an integerConstant
    # Grammar:
    # decimal number in range of 0..32767
    def _compile_int_constant(self):
        if (not self._is_int_constant()):
            self._integer_syntax_error()
        self._vmw.write_push(VmWriter.S_CONSTANT, self._tkn.token())
        self._tkn.advance()

    # Compile a stringConstant
    # Grammar:
    # '"' sequence of unicode chars not including double quote or newline '"'
    def _compile_string_constant(self):
        if (not self._is_string_constant()):
            self._string_syntax_error()

        str = self._tkn.string_val()
        str_len = len(str)
        self._vmw.write_push(VmWriter.S_CONSTANT, str_len)
        self._vmw.write_call("String.new", 1)
        for char in str:
            self._vmw.write_push(VmWriter.S_CONSTANT, ord(char))
            self._vmw.write_call("String.appendChar", 2)
        
        self._tkn.advance()

    # Compile a keywordConstant
    # Grammar:
    # 'true' | 'false' | 'null' | 'this'
    def _compile_keyword_constant(self):
        token = self._tkn.token()
        if token == "true":
            # true is 1111 1111 1111 1111
            self._vmw.write_push(VmWriter.S_CONSTANT, 0)
            self._vmw.write_arithmetic("not")
        elif token == "false" or token == "null":
            # false/null are 0000 0000 0000 0000
            self._vmw.write_push(VmWriter.S_CONSTANT, 0)
        elif token == "this":
            self._vmw.write_push(VmWriter.S_POINTER, 0)
        self._tkn.advance() # keywordConstant

    # Compile an optional array expression
    # Grammar:
    # '[' expression ']'
    def _compile_array_expression(self, var_name):
        if self._is_symbol() and self._symbol_is("["):          # ('[' expression ']')?
            self._compile_symbol("[")                           # [ symbol
            self._compile_expression()                          # expression
            self._compile_symbol("]")                           # ] symbol
            self._vmw.write_push(self._symbol_table.segment_of(var_name), self._symbol_table.index_of(var_name))
            self._vmw.write_arithmetic("add")
            return True
        return False

    # Compile an expression block
    # Grammar:
    # '(' expression ')'
    def _compile_expression_block(self):
        self._compile_symbol("(")
        self._compile_expression()
        self._compile_symbol(")")

    # Compile a unaryOp
    # Grammar:
    # unaryOp term
    def _compile_unary_op(self):
        if self._symbol_is("-"):
            self._compile_symbol("-")
            arith_cmd = "neg"
        else:
            self._compile_symbol("~")
            arith_cmd = "not"
        self._compile_term()
        self._vmw.write_arithmetic(arith_cmd)

    # Compile expression(s)
    # Grammar:
    # (expression (',' expression)*)?
    def _compile_expression_list(self, count):
        if self._is_term_start():
            # determine if the current token is the start of a term
            self._compile_expression()
            count += 1
        elif self._is_symbol() and self._symbol_is(","):
            # comma means additional expression
            self._compile_symbol(",")
            self._compile_expression()
            count += 1
        else:
            # no more to process
            return count
        
        # process more expressions
        count = self._compile_expression_list(count)
        return count
    