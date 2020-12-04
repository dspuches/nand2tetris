from .parse_error import ParseError
from . import config

class Parser():
    """Parser class responsible for parsing vm commands into assembly.

    Attributes:
        _input -- list of vm commands, one line per list element
        _numlines -- number of vm commands
        _index -- current index of instruction in _input
    """

    def __init__(self, input):
        self._input = input
        self._numlines = len(self._input)
        self._index = -1
    
    # return the current line with no leading/trailing whitespace and no comments
    def current_line(self):
        no_comment = self._input[self._index].split("//")[0]
        return no_comment.strip()

    # return true if there are more commands to process
    def has_more_commands(self):
        if self._index < (self._numlines - 1):
            return True
        else:
            return False
    
    # advance the current command
    def advance(self):
        if self.has_more_commands():
            self._index += 1
    
    # return the current command type of the existing instruction
    def command_type(self):
        line = self.current_line()
        split = line.split()

        if len(split) == 0:
            return config.C_EMPTY_LINE
        
        if len(split) == 1 and split[0] in config.ARITHMETIC_COMMANDS:
            return config.C_ARITHMETIC

        if len(split) == 3 and split[0] in config.PUSH_POP_COMMANDS:
            if split[0] == "push":
                return config.C_PUSH
            else:
                return config.C_POP
        
        raise ParseError(self.current_line(), "Cannot determine command type")
        

    # return the first argument of the current command
    def arg1(self):
        if self.command_type() == config.C_ARITHMETIC:
            return self.current_line()
        
        if self.command_type() in config.PUSH_POP_COMMANDS:
            arg1 = self.current_line().split()[1]
            if arg1 in config.SEGMENTS.keys():
                return arg1
            else:
                raise ParseError(self.current_line(), "Invalid segment")
        
        raise ParseError(self.current_line(), "Cannot determine arg1 for this command type")
    
    # return the second argument of the current command
    def arg2(self):
        type = self.command_type()

        if type in config.PUSH_POP_COMMANDS:
            try:
                return int(self.current_line().split()[2])
            except ValueError:
                raise ParseError(self.current_line(), "arg2 must be an integer")
        
        raise ParseError(self.current_line(), "Cannot determine arg2 for this command type")