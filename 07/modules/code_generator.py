from .code_error import CodeError
from . import config

class CodeGenerator():
    """Generator class class responsible for generating ASM code from VM code.

    Attributes:
    """
    def __init__(self):
        pass
        # initialize SP, set SP=256
        # self._asm.append("@256")
        # self._asm.append("D=A")
        # self._asm.append("@SP")
        # self._asm.append("M=D")
    
    # generates the arithmetic ASM commands
    # assumes stack is setup as follows:
    # |     x     |
    # |     y     |
    # |           | <- SP
    def generate_arithmetic(self, command):
        if command not in config.ARITHMETIC_COMMANDS:
            raise CodeError(command, "Is not a valid arithmetic command")

        asm_cmds = []
        switch = {
            "add": self.a_add,
            "sub": self.a_sub,
        }
        func = switch.get(command)
        return func()

    # generates push and pop asm commands
    def generate_push_pop(self, command, segment, index):
        if command is not config.C_PUSH:
            raise CodeError(command, "Is not a valid push or pop command")
        if segment not in config.SEGMENTS:
            raise CodeError(segment, "Cannot process segment")
        asm_cmds = []

        if command == config.C_PUSH:
            if segment == config.S_CONSTANT:
                return self.asm_push_constant(index)
    
    # generates asm for the add VM arithemteic command
    def a_add(self):
        asm_cmds = [
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",      # D = y
            "@SP",
            "M=M-1",
            "A=M",
            "D=D+M",    # D = y + x
        ]
        asm_cmds.extend(self.asm_push_d())
        return asm_cmds
    
    # generates asm for the sub VM arithmetic command
    def a_sub(self):
        asm_cmds = [
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",      # D = y
            "D=-D",     # D = -y
            "@SP",
            "M=M-1",
            "A=M",
            "D=D+M"     # D = -y + x  (aka x + -y aka x - y)
        ]
        asm_cmds.extend(self.asm_push_d())
        return asm_cmds

    # helper method to push a constant to the stack
    def asm_push_constant(self, index):
        asm_cmds = [
            "@{}".format(index),
            "D=A",
        ]
        asm_cmds.extend(self.asm_push_d())
        return asm_cmds
    
    # helper method to push the value of the D register to the stack
    def asm_push_d(self):
        asm_cmds = [
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ]
        return asm_cmds


