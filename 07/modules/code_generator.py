from .code_error import CodeError
from . import config

class CodeGenerator():
    """Generator class class responsible for generating ASM code from VM code.

    Attributes:
    """
    def __init__(self):
        self._a_eq_ctr = 1
        self._a_gt_ctr = 1
        self._a_lt_ctr = 1

    # generate preamble asm code
    # right now, all it does is initialize SP to 256
    def generate_preamble(self):
        asm_cmds = [
            "@256",
            "D=A",
            "@SP",
            "M=D",
        ]
        return asm_cmds


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
            "neg": self.a_neg,
            "eq": self.a_eq,
            "gt": self.a_gt,
            "lt": self.a_lt,
            "and": self.a_and,
            "or": self.a_or,
            "not": self.a_not,
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
    
    def a_neg(self):
        asm_cmds = [
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",      # D = y
            "D=-D",     # D = -y
        ]
        asm_cmds.extend(self.asm_push_d())
        return asm_cmds
    
    # if x - y == 0, they are equal.
    def a_eq(self):
        asm_cmds = []
        asm_cmds.extend(self.a_sub())
        asm_check_eq = [
            "@A_EQ_TRUE{}".format(self._a_eq_ctr),
            "D;JEQ",
            "@SP",        # value is not == 0, store false (0)
            "M=M-1",
            "A=M",
            "M=0",
            "@SP",
            "M=M+1",
            "@A_EQ_DONE{}".format(self._a_eq_ctr),
            "0;JMP",
            "(A_EQ_TRUE{})".format(self._a_eq_ctr),
            "@SP",         # value is == 0, store true (-1)
            "M=M-1",
            "A=M",
            "M=-1",
            "@SP",
            "M=M+1",
            "(A_EQ_DONE{})".format(self._a_eq_ctr),
        ]
        self._a_eq_ctr += 1
        asm_cmds.extend(asm_check_eq)
        return asm_cmds

    # if x - y > 0, true.
    def a_gt(self):
        asm_cmds = []
        asm_cmds.extend(self.a_sub())
        asm_check_gt = [
            "@A_GT_TRUE{}".format(self._a_gt_ctr),
            "D;JGT",
            "@SP",        # value is not == 0, store false (0)
            "M=M-1",
            "A=M",
            "M=0",
            "@SP",
            "M=M+1",
            "@A_GT_DONE{}".format(self._a_gt_ctr),
            "0;JMP",
            "(A_GT_TRUE{})".format(self._a_gt_ctr),
            "@SP",         # value is == 0, store true (-1)
            "M=M-1",
            "A=M",
            "M=-1",
            "@SP",
            "M=M+1",
            "(A_GT_DONE{})".format(self._a_gt_ctr),
        ]
        self._a_gt_ctr += 1
        asm_cmds.extend(asm_check_gt)
        return asm_cmds

    # if x - y < 0, true.
    def a_lt(self):
        asm_cmds = []
        asm_cmds.extend(self.a_sub())
        asm_check_lt = [
            "@A_LT_TRUE{}".format(self._a_lt_ctr),
            "D;JLT",
            "@SP",        # value is not == 0, store false (0)
            "M=M-1",
            "A=M",
            "M=0",
            "@SP",
            "M=M+1",
            "@A_LT_DONE{}".format(self._a_lt_ctr),
            "0;JMP",
            "(A_LT_TRUE{})".format(self._a_lt_ctr),
            "@SP",         # value is == 0, store true (-1)
            "M=M-1",
            "A=M",
            "M=-1",
            "@SP",
            "M=M+1",
            "(A_LT_DONE{})".format(self._a_lt_ctr),
        ]
        self._a_lt_ctr += 1
        asm_cmds.extend(asm_check_lt)
        return asm_cmds
    
    # generates asm for the and VM arithmetic command
    def a_and(self):
        asm_cmds = [
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",      # D = y
            "@SP",
            "M=M-1",
            "A=M",
            "D=D&M"     # D = x & y
        ]
        asm_cmds.extend(self.asm_push_d())
        return asm_cmds

    # generates asm for the or VM arithmetic command
    def a_or(self):
        asm_cmds = [
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",      # D = y
            "@SP",
            "M=M-1",
            "A=M",
            "D=D|M"     # D = x & y
        ]
        asm_cmds.extend(self.asm_push_d())
        return asm_cmds

    def a_not(self):
        asm_cmds = [
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",      # D = y
            "D=!D",     # D = -y
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


