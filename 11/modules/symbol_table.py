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
        self._static_count = 0                              # count of static variables in current scope
        self._field_count = 0                               # count of field variables in current scope

        self.start_method()

    # clear the method symbol table and reset the index
    def start_method(self):
        self._method_table = {}                             # method scoped symbol table
        self._method_index = 0                              # method scoped index
        self._arg_count = 0                                 # count of arg variables in current scope
        self._var_count = 0                                 # count of var variables in current scope

    # define a new entry in the symbol tables
    def define(self, name, type, kind):
        if kind in self.CLASS_SCOPES:
            self._class_define(name, type, kind)
        elif kind in self.METHOD_SCOPES:
            self._method_define(name, type, kind)
        else:
            raise SymbolTableError("Unknown kind: <{}>".format(kind))

    # helper to define a method scoped symbol
    def _method_define(self, name, type, kind):
        if name not in self._method_table:
            self._method_table[name] = {"kind": kind, "type": type, "index": self._method_index}
            self._method_index += 1
            if kind == self.K_ARG:
                self._arg_count += 1
            else:
                self._var_count += 1
        else:
            raise SymbolTableError("Attemting to define a symbol that is already defined: <{}>".format(name))

    # helper to define a class scoped symbol
    def _class_define(self, name, type, kind):
        if name not in self._class_table:
            self._class_table[name] = {"kind": kind, "type": type, "index": self._class_index}
            self._class_index += 1
            if kind == self.K_STATIC:
                self._static_count += 1
            else:
                self._field_count += 1
        else:
            raise SymbolTableError("Attemting to define a symbol that is already defined: <{}>".format(name))

    # return the number of variable definitons of the given kind
    def var_count(self, kind):
        if kind == self.K_STATIC:
            return self._static_count
        if kind == self.K_FIELD:
            return self._field_count
        if kind == self.K_ARG:
            return self._arg_count
        if kind == self.K_VAR:
            return self._var_count

        raise SymbolTableError("Unknown kind: <{}>".format(kind))

    # return the kind of the named identifier in the current scope
    # returns K_NONE if the symbol is not defined
    def kind_of(self, name):
        if name in self._method_table.keys():
            return self._method_table[name]["kind"]
        elif name in self._class_table.keys():
            return self._class_table[name]["kind"]
        else:
            return self.K_NONE

    # returns the type of the named identifier in the current scope
    def type_of(self, name):
        if name in self._method_table.keys():
            return self._method_table[name]["type"]
        elif name in self._class_table.keys():
            return self._class_table[name]["type"]

        raise SymbolTableError("Undefined name encountered when calling type_of: <{}>".format(name))

    # returns the index of the named identifier in the current scope
    def index_of(self, name):
        if name in self._method_table.keys():
            return self._method_table[name]["index"]
        elif name in self._class_table.keys():
            return self._class_table[name]["index"]

        raise SymbolTableError("Undefined name encountered when calling type_of: <{}>".format(name))