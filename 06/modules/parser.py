import re
from .parse_error import ParseError

class Parser():
    """Parser class responsible for parsing assembly commands.

    Attributes:
        _input -- list of assembly commands, one line per list element
        _numlines -- number of assembly commands after whitespace is removed
        _index -- current index of instruction in _input
    """
    A_COMMAND = "A_COMMAND"
    C_COMMAND = "C_COMMAND"
    L_COMMAND = "L_COMMAND"

    DESTINATIONS = [
        "null",
        "M",
        "D",
        "MD",
        "A",
        "AM",
        "AD",
        "AMD",
    ]

    JUMPS = [
        "null",
        "JGT",
        "JEQ",
        "JGE",
        "JLT",
        "JNE",
        "JLE",
        "JMP",
    ]

    COMPUTATIONS = [
        "0",
        "1",
        "-1",
        "D",
        "A",
        "!D",
        "!A",
        "-D",
        "-A",
        "D+1",
        "A+1",
        "D-1",
        "A-1",
        "D+A",
        "D-A",
        "A-D",
        "D&A",
        "D|A",
        "M",
        "!M",
        "-M",
        "M+1",
        "M-1",
        "D+M",
        "D-M",
        "M-D",
        "D&M",
        "D|M",
    ]

    def __init__(self, input):
        self._input = input
        self._numlines = len(self._input)
        self._index = -1
    
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
    
    # return the current instruction
    def current_instruction(self):
        if self._index >= 0 and self._index < self._numlines:
            return self._input[self._index]
        else:
            raise ParseError(self._index, "Index out of range, no current instruction")

    # return the command type of the existing instruction
    def command_type(self):
        line = self._input[self._index]
        if re.search("^@[0-9]+$", line) or re.search("^@[a-zA-Z][a-zA-Z0-9_\.\$\:]*$", line):
            return self.A_COMMAND
        elif re.search("^\([a-zA-Z_\.\$\:][a-zA-Z0-9_\.\$\:]*\)$", line):
            return self.L_COMMAND
        else:
            return self.C_COMMAND

    def symbol(self):
        if self.command_type() == self.A_COMMAND:
            instruction = self._input[self._index]
            stripped = instruction.replace('@', '')
            try:
                stripped_int = int(stripped)
                if stripped_int < 32768 and stripped_int >= 0:
                    return stripped
                else:
                    raise ParseError(instruction, "Invalid value in A-instruction: {}. Value must be between 0 and 32767 (inclusive)".format(stripped_int))
            except ValueError:
                return stripped
        elif self.command_type() == self.L_COMMAND:
            return self._input[self._index].replace('(', '').replace(')', '')
        else:
            raise ParseError(self.current_instruction(), "Cannot determine symbol for a c-instruction")

    def dest(self):
        if self.command_type() == self.C_COMMAND:
            if re.search('=', self.current_instruction()):
                # destination is specified. make sure there is only one =
                if self.current_instruction().count("=") == 1:
                    split = self.current_instruction().split("=")
                    if split[0] in self.DESTINATIONS:
                        return split[0]
                    else:
                        raise ParseError(self.current_instruction(), "Invalid destination specified")
                else:
                    raise ParseError(self.current_instruction(), "Multiple destinations specified")
            else:
                # no destination is specified
                return "null"
        else:
            raise ParseError(self.current_instruction(), "Can only determine dest for C-instructions")
    
    def comp(self):
        if self.command_type() == self.C_COMMAND:
            line = self.current_instruction()
            comp = ""
            if re.search('=', line) and re.search(';', line):
                # if = and ; are present, it is the part between the two
                splitline = line.split('=')[1]
                comp = splitline.split(';')[0]
            elif re.search('=', line):
                # if only = is present, it is the part to the right of =
                comp = line.split('=')[1]
            elif re.search(';', line):
                # if only ; is present it is the part to the left of ;
                comp = line.split(';')[0]
            else:
                # if neither = or ; are present, it is the entire string (really useless but whatever)
                comp = line
            if comp in self.COMPUTATIONS:
                return comp
            else:
                raise ParseError(self.current_instruction(), "Invalid computation specified")

        else:
            raise ParseError(self.current_instruction(), "Can only determine comp for C-instructions")

    def jump(self):
        if self.command_type() == self.C_COMMAND:
            if re.search(';', self.current_instruction()):
                # jump is specified. make sure there is only 1 ;
                if self.current_instruction().count(";") == 1:
                    split = self.current_instruction().split(";")
                    if split[1] in self.JUMPS:
                        return split[1]
                    else:
                        raise ParseError(self.current_instruction(), "Invalid jump specified")
                else:
                    raise ParseError(self.current_instruction(), "Multiple jumps specified")
            else:
                # no destination is specified
                return "null"
        else:
            raise ParseError(self.current_instruction(), "Can only determine dest for C-instructions")