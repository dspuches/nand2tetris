from .code_error import CodeError
from . import config

class CodeGenerator():
    """Generator class class responsible for generating ASM code from VM code.

    Attributes:
    """
    def __init__(self):
        # counters for labels generated during comparisons
        self._a_eq_ctr = 1
        self._a_gt_ctr = 1
        self._a_lt_ctr = 1

    # generate preamble asm code
    # right now, all it does is initialize SP to 256
    def generate_preamble(self):
        asm_cmds = [
            "@256",             # A=256
            "D=A",              # D=256
            "@SP",              # A=SP
            "M=D",              # M[SP]=256
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
            "add": self._a_add,
            "sub": self._a_sub,
            "neg": self._a_neg,
            "eq": self._a_eq,
            "gt": self._a_gt,
            "lt": self._a_lt,
            "and": self._a_and,
            "or": self._a_or,
            "not": self._a_not,
        }
        func = switch.get(command)
        return func()

    # generates push and pop asm commands
    def generate_push_pop(self, command, segment, index):
        if command is not config.C_PUSH:
            raise CodeError(command, "Is not a valid push or pop command")
        asm_cmds = []

        if command == config.C_PUSH:
            if segment not in config.PUSH_SEGMENTS:
                raise CodeError(segment, "Cannot process segment")
            if segment == config.S_CONSTANT:
                return self._asm_push_constant(index)
    
    # generates asm for the add VM arithemteic command
    def _a_add(self):
        asm_cmds = self._asm_pop_d()            # SP--;D=*M[SP]
        asm_cmds.extend([
            "@SP",                              # A=SP
            "M=M-1",                            # SP--
            "A=M",                              # A=M[SP]
            "D=D+M",                            # D=D+*M[SP]
        ])
        asm_cmds.extend(self._asm_push_d())
        return asm_cmds
    
    # generates asm for the sub VM arithmetic command
    def _a_sub(self):
        asm_cmds = self._asm_pop_d()            # SP--;D=*M[SP]
        asm_cmds.extend([
            "D=-D",                             # D=-D
            "@SP",                              # A=SP
            "M=M-1",                            # SP--
            "A=M",                              # A=M[SP]
            "D=D+M"                             # D=D+*M[SP]  (aka x + -y aka x - y)
        ])
        asm_cmds.extend(self._asm_push_d())
        return asm_cmds
    
    # generates asm for the neg VM arithmetic command
    def _a_neg(self):
        asm_cmds = self._asm_pop_d()            # SP--;D=*M[SP]
        asm_cmds.extend([
            "D=-D",                             # D=-D
        ])
        asm_cmds.extend(self._asm_push_d())
        return asm_cmds
    
    # generates asm for the eq VM arithmetic command
    # if x - y == 0, they are equal.
    def _a_eq(self):
        asm_cmds = self._a_sub()
        asm_cmds.extend([
            "@A_EQ_TRUE{}".format(self._a_eq_ctr),
            "D;JEQ",
        ])
        asm_cmds.extend(self._asm_push_false())
        asm_cmds.extend([
            "@A_EQ_DONE{}".format(self._a_eq_ctr),
            "0;JMP",
            "(A_EQ_TRUE{})".format(self._a_eq_ctr),
        ])
        asm_cmds.extend(self._asm_push_true())
        asm_cmds.extend([
            "(A_EQ_DONE{})".format(self._a_eq_ctr),
        ])
        self._a_eq_ctr += 1
        return asm_cmds

    # generates asm for the gt VM arithmetic command
    # if x - y > 0, true.
    def _a_gt(self):
        asm_cmds = self._a_sub()
        asm_cmds.extend([
            "@A_GT_TRUE{}".format(self._a_gt_ctr),
            "D;JGT",
        ])
        asm_cmds.extend(self._asm_push_false())
        asm_cmds.extend([
            "@A_GT_DONE{}".format(self._a_gt_ctr),
            "0;JMP",
            "(A_GT_TRUE{})".format(self._a_gt_ctr),
        ])
        asm_cmds.extend(self._asm_push_true())
        asm_cmds.extend([
            "(A_GT_DONE{})".format(self._a_gt_ctr),
        ])
        self._a_gt_ctr += 1
        return asm_cmds

    # generates asm for the lt VM arithmetic command
    # if x - y < 0, true.
    def _a_lt(self):
        asm_cmds = self._a_sub()
        asm_cmds.extend([
            "@A_LT_TRUE{}".format(self._a_lt_ctr),
            "D;JLT",
        ])
        asm_cmds.extend(self._asm_push_false())
        asm_cmds.extend([
            "@A_LT_DONE{}".format(self._a_lt_ctr),
            "0;JMP",
            "(A_LT_TRUE{})".format(self._a_lt_ctr),
        ])
        asm_cmds.extend(self._asm_push_true())
        asm_cmds.extend([
            "(A_LT_DONE{})".format(self._a_lt_ctr),
        ])
        self._a_lt_ctr += 1
        return asm_cmds
    
    # generates asm for the and VM arithmetic command
    def _a_and(self):
        asm_cmds = self._asm_pop_d()
        asm_cmds.extend([
            "@SP",                      # A=SP
            "M=M-1",                    # SP--
            "A=M",                      # A=*M[SP]
            "D=D&M"                     # D=D&*M[SP]
        ])
        asm_cmds.extend(self._asm_push_d())
        return asm_cmds

    # generates asm for the or VM arithmetic command
    def _a_or(self):
        asm_cmds = self._asm_pop_d()
        asm_cmds.extend([
            "@SP",                      # A=SP
            "M=M-1",                    # SP--
            "A=M",                      # A=*M[SP]
            "D=D|M"                     # D=D|*M[SP]
        ])
        asm_cmds.extend(self._asm_push_d())
        return asm_cmds

    # generates asm for the not VM arithmetic command
    def _a_not(self):
        asm_cmds = self._asm_pop_d()
        asm_cmds.extend([
            "D=!D",     # D = -y
        ])
        asm_cmds.extend(self._asm_push_d())
        return asm_cmds

    # helper method to push a constant to the stack
    def _asm_push_constant(self, index):
        asm_cmds = [
            "@{}".format(index),
            "D=A",
        ]
        asm_cmds.extend(self._asm_push_d())
        return asm_cmds
    
    # helper method to push the value of the D register to the stack
    def _asm_push_d(self):
        asm_cmds = [
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ]
        return asm_cmds
    
    # helper method to pop from the stack and store in the D register
    def _asm_pop_d(self):
        asm_cmds = [
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
        ]
        return asm_cmds

    # helper method to push true (-1) onto the stack
    def _asm_push_true(self):
        asm_cmds = [
            "@SP",
            "M=M-1",
            "A=M",
            "M=-1",
            "@SP",
            "M=M+1",
        ]
        return asm_cmds

    # helper method to push false (0) onto the stack
    def _asm_push_false(self):
        asm_cmds = [
            "@SP",        
            "M=M-1",
            "A=M",
            "M=0",
            "@SP",
            "M=M+1",
        ]
        return asm_cmds

