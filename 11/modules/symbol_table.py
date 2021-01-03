from errors.symbol_table_error import SymbolTableError

class SymbolTable:
    K_STATIC = "static"
    K_FIELD = "field"
    K_ARG = "arg"
    K_VAR = "var"
    K_NONE = "none"

    CLASS_SCOPES = [K_STATIC, K_FIELD]
    METHOD_SCOPES = [K_ARG, K_VAR]

    def __init__(self):
        self._class_table = {}                              # class scoped symbol table
        self._class_index = 0                               # class scoped index
        self._method_table = {}                             # method scoped symbol table
        self._method_index = 0                              # method scoped index

    # clear the method symbol table and reset the index
    def start_subroutine(self):
        self._method_table = {}
        self._method_index = 0

    # define a new entry in the symbol tables
    def define(self, name, type, kind):
        if kind in self.CLASS_SCOPES:
            if name not in self._class_table:
                self._class_table[name] = {"kind": kind, "type": type, "index": self._class_index}
                self._class_index += 1
        elif kind in self.METHOD_SCOPES:
            if name not in self._method_table:
                self._method_table[name] = {"kind": kind, "type": type, "index": self._method_index}
                self._method_index += 1
        else:
            raise SymbolTableError("Unknown kind: <{}>".format(kind))

    def var_count(self):
        pass

    def kind_of(self):
        pass

    def type_of(self):
        pass

    def index_of(self):
        pass