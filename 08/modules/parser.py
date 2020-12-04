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
        
        command = split[0]
        nargs = len(split) - 1
        
        if command in config.COMMANDS.keys():
            # valid command, check # of arguments
            if config.COMMANDS[command]["args"] == nargs:
                return config.COMMANDS[command]["type"]
            raise ParseError(self.current_line(), "Invalid number of arguments for this command.")
        raise ParseError(self.current_line(), "Invalid command")
        

    # return the first argument of the current command
    def arg1(self):
        # if an exeception is raised, its an invalid command or has wrong # of params
        cmd_type = self.command_type()

        # special case for arithmetic commands, the command itself is arg1.
        if cmd_type == config.C_ARITHMETIC:
            return self.current_line()
        
        split = self.current_line().split()
        return split[1]
        
    # return the second argument of the current command
    def arg2(self):
        # if an exeception is raised, its an invalid command or has wrong # of params
        cmd_type = self.command_type()
        split = self.current_line().split()

        try:
            return int(split[2])
        except ValueError:
            raise ParseError(self.current_line(), "arg2 must be an integer")