

class SymbolTable:

    def __init__(self):
        self._class_table = {}
        self._class_index = 0
        self._method_table = {}
        self._method_index = 0

    def start_subroutine(self):
        self._class_table = {}

    def define(self, name, type, kind):
        pass

    def var_count(self):
        pass

    def kind_of(self):
        pass

    def type_of(self):
        pass

    def index_of(self):
        pass