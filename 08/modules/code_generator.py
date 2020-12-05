from .code_error import CodeError
from . import config

class CodeGenerator():
    """Generator class class responsible for generating ASM code from VM code.

    Attributes:
    """
    def __init__(self, vmfile=None):
        # counters for labels generated during comparisons
        self._a_eq_ctr = 1
        self._a_gt_ctr = 1
        self._a_lt_ctr = 1
        self._vmfile = vmfile
        self._current_function = None
        self._function_id = 1
    
    # return value of the vmfile property
    @property
    def vmfile(self):
        return self._vmfile
    
    # set the value of the vmfile property
    @vmfile.setter
    def vmfile(self, newfile):
        self._vmfile = newfile

    # generate preamble asm code
    # Init SP, LCL, ARG, THIS, and THAT
    def generate_init(self):
        asm_cmds = [
            "@256",             # SP=256
            "D=A",
            "@SP",
            "M=D",
        ]
        asm_cmds.extend(self.generate_call("Sys.init", 0))
        return asm_cmds

    # generates the arithmetic ASM commands
    # assumes stack is setup as follows:
    # |     x     |
    # |     y     |
    # |           | <- SP
    # unary operators will only process y
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
        if command not in config.PUSH_POP_COMMANDS:
            raise CodeError(command, "Is not a valid push or pop command")

        asm_cmds = []

        if command == config.C_PUSH:
            if segment not in config.SEGMENTS.keys():
                raise CodeError(segment, "Cannot process segment for push command")
            
            # push the value of segment[index] to the stack
            return self._asm_push_segment(segment, index)
        if command == config.C_POP:
            if segment not in config.SEGMENTS.keys() or segment == config.S_CONSTANT:
                raise CodeError(segment, "Cannot process segment for pop command")
            return self._asm_pop_segment(segment, index)
    
    # generates asm for label
    def generate_label(self, label):
        if len(self._current_function) is None:
            raise CodeError(label, "Labels must be defined within a function")
        asm_cmds = ["({}${})".format(self._current_function, label)]
        return asm_cmds
    
    # generates asm for goto
    def generate_goto(self, label):
        asm_cmds = [
            "@{}${}".format(self._current_function, label),
            "0;JMP",
        ]
        return asm_cmds

    # generate asm for if-goto
    # pop the topmost value from the stack
    # if the value != 0, then jump to label
    # else, continue as normal
    def generate_if(self, label):
        asm_cmds = self._asm_pop_d()
        asm_cmds.extend([
            "@{}${}".format(self._current_function, label),
            "D;JNE"
        ])
        return asm_cmds

    # generate asm for function definition
    def generate_function(self, name, num_locals):
        # store function name so we can appropriately name function labels
        self._current_function = name
        asm_cmds = [
            "({})".format(name)
        ]
        # initialize the local vars (on stack) to zero
        for i in range(num_locals):
            asm_cmds.extend(self._asm_push_constant(0))
        return asm_cmds
    
    # generates asm for the call command
    def generate_call(self, name, num_args):
        return_label = "{}.{}.return".format(name, self._function_id)
        self._function_id += 1

        asm_cmds = []
        # push return address onto the stack
        asm_cmds.extend(self._asm_push_a(return_label))
        # push LCL
        asm_cmds.extend(self._asm_push_m("LCL"))
        # push ARG
        asm_cmds.extend(self._asm_push_m("ARG"))
        # push THIS
        asm_cmds.extend(self._asm_push_m("THIS"))
        # push THAT
        asm_cmds.extend(self._asm_push_m("THAT"))
        # ARG = SP-num_args-5
        asm_cmds.extend([
            "@SP",
            "D=M",
            "@{}".format(num_args),
            "D=D-A",
            "@5",
            "D=D-A",
            "@ARG",
            "M=D",
        ])

        # LCL = SP
        asm_cmds.extend([
            "@SP",
            "D=M",
            "@LCL",
            "M=D",
        ])

        # goto function
        asm_cmds.extend([
            "@{}".format(name),
            "0;JMP",
        ])

        # (return_label)
        asm_cmds.append("({})".format(return_label))
        
        return asm_cmds
    
    # generates asm for return
    def generate_return(self):
        asm_cmds = []
        # FRAME = LCL (R13 will be FRAME)
        asm_cmds.extend([
            "@LCL",
            "D=M",
            "@R13",
            "M=D",
        ])
        # RET = *(FRAME - 5) (R14 will be RET)
        asm_cmds.extend([
            "@5",
            "D=D-A",
            "A=D",
            "D=M",
            "@R14",
            "M=D",
        ])
        # *ARG = pop() - pop from working stack and store the value at 
        # the memory location pointed to by ARG
        asm_cmds.extend(self._asm_pop_d())
        asm_cmds.extend([
            "@ARG",
            "A=M",
            "M=D",
        ])
        # SP = ARG + 1
        asm_cmds.extend([
            "@ARG",
            "D=M",
            "D=D+1",
            "@SP",
            "M=D",
        ])
        # THAT = *(FRAME-1)
        asm_cmds.extend([
            "@R13",
            "D=M",
            "@1",
            "D=D-A",
            "A=D",
            "D=M",
            "@THAT",
            "M=D",
        ])
        # THIS = *(FRAME-2)
        asm_cmds.extend([
            "@R13",
            "D=M",
            "@2",
            "D=D-A",
            "A=D",
            "D=M",
            "@THIS",
            "M=D",
        ])
        # ARG = *(FRAME-3)
        asm_cmds.extend([
            "@R13",
            "D=M",
            "@3",
            "D=D-A",
            "A=D",
            "D=M",
            "@ARG",
            "M=D",
        ])
        # LCL = *(FRAME-4)
        asm_cmds.extend([
            "@R13",
            "D=M",
            "@4",
            "D=D-A",
            "A=D",
            "D=M",
            "@LCL",
            "M=D",
        ])
        # goto RET
        asm_cmds.extend([
            "@R14",
            "A=M",
            "0;JMP"
        ])
        return asm_cmds

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

    # helper method to push a constant (index) to the stack
    def _asm_push_constant(self, index):
        asm_cmds = [
            "@{}".format(index),
            "D=A",
        ]
        asm_cmds.extend(self._asm_push_d())
        return asm_cmds
    
    # helper method to push from the temp segment
    # index must be between 0 and 7 inclusive
    def _asm_push_temp(self, index):
        if index < 0 or index > 7:
            raise CodeError(index, "index must be between 0 and 7 (inclusive)")

        asm_cmds = [
            "@{}".format(config.S_TEMP_BASE),# A=5
            "D=A",                           # D=5
            "@{}".format(index),             # A=index
            "D=D+A",                         # D=5+index
            "A=D",                           # A=5+index
            "D=M",                           # D=M[5+index]
        ]
        asm_cmds.extend(self._asm_push_d())
        return asm_cmds

    # helper method to pop into the temp segment
    # index must be between 0 and 7 inclusive
    def _asm_pop_temp(self, index):
        if index < 0 or index > 7:
            raise CodeError(index, "index must be between 0 and 7 (inclusive)")

        asm_cmds = [
            "@{}".format(config.S_TEMP_BASE),
            "D=A",
            "@{}".format(index),
            "D=D+A",
            "@R13",
            "M=D",
        ]
        asm_cmds.extend(self._asm_pop_d())
        asm_cmds.extend([
            "@R13",
            "A=M",
            "M=D",
        ])
        return asm_cmds
    
    # helper method to push from the pointer segment
    # index must be between 0 and 1 inclusive
    def _asm_push_pointer(self, index):
        if index < 0 or index > 1:
            raise CodeError(index, "index must be between 0 and 1 (inclusive)")
        
        asm_cmds = [
            "@{}".format(config.S_POINTER_BASE),# A=3
            "D=A",                              # D=3
            "@{}".format(index),                # A=index
            "D=D+A",                            # D=3+index
            "A=D",                              # A=3+index
            "D=M",                              # D=M[3+index]
        ]
        asm_cmds.extend(self._asm_push_d())
        return asm_cmds
    
    # helper method to pop into the pointer segment
    def _asm_pop_pointer(self, index):
        if index < 0 or index > 1:
            raise CodeError(index, "index must be between 0 and 1 (inclusive)")

        asm_cmds = [
            "@{}".format(config.S_POINTER_BASE),
            "D=A",
            "@{}".format(index),
            "D=D+A",
            "@R13",
            "M=D",
        ]
        asm_cmds.extend(self._asm_pop_d())
        asm_cmds.extend([
            "@R13",
            "A=M",
            "M=D",
        ])
        return asm_cmds
    
    def _asm_push_static(self, index):
        if self.vmfile == None:
            raise CodeError("vmfile", "vmfile must be defined for push static")
        asm_cmds = [
            "@{}.{}".format(self.vmfile, index),
            "D=M",
        ]
        asm_cmds.extend(self._asm_push_d())
        return asm_cmds
    
    def _asm_pop_static(self, index):
        if self.vmfile == None:
            raise CodeError("vmfile", "vmfile must be defined for pop static")

        asm_cmds = [
            "@{}.{}".format(self.vmfile, index),
            "D=A",
            "@R13",
            "M=D",
        ]
        asm_cmds.extend(self._asm_pop_d())
        asm_cmds.extend([
            "@R13",
            "A=M",
            "M=D",
        ])
        return asm_cmds

    # pushes the value mapped at segment[index] onto the stack.
    def _asm_push_segment(self, segment, index):
        if segment not in config.SEGMENTS.keys():
            raise CodeError(segment, "No predefined symbol is defined for this segment")
        if segment == config.S_CONSTANT:
            return self._asm_push_constant(index)

        if segment == config.S_TEMP:
            return self._asm_push_temp(index)

        if segment == config.S_POINTER:
            return self._asm_push_pointer(index)

        if segment == config.S_STATIC:
            return self._asm_push_static(index)

        # if we got this far, process the push command as 
        # pushing the value at segment[index] onto the stack
        asm_segment = config.SEGMENTS[segment]
        asm_cmds = [
            "@{}".format(asm_segment),       # A=SEG
            "D=M",                           # D=*SEG
            "@{}".format(index),             # A=index
            "D=D+A",                         # D=SEG+index
            "A=D",                           # A=SEG+index
            "D=M",                           # D=M[SEG+index]
        ]
        asm_cmds.extend(self._asm_push_d())
        return asm_cmds
    
    # pop the value pointed to by SP into segment[index] 
    def _asm_pop_segment(self, segment, index):
        if segment not in config.SEGMENTS.keys() or segment == config.S_CONSTANT:
            raise CodeError(segment, "No predefined symbol is defined for this segment")

        if segment == config.S_TEMP:
            return self._asm_pop_temp(index)
        
        if segment == config.S_POINTER:
            return self._asm_pop_pointer(index)
        
        if segment == config.S_STATIC:
            return self._asm_pop_static(index)

        # if we got this far, process the push command as 
        # popping from stack and storing at value at segment[index]
        asm_segment = config.SEGMENTS[segment]
        asm_cmds = [
            "@{}".format(asm_segment),
            "D=M",
            "@{}".format(index),
            "D=D+A",
            "@R13",
            "M=D",
        ]
        asm_cmds.extend(self._asm_pop_d())
        asm_cmds.extend([
            "@R13",
            "A=M",
            "M=D",
        ])
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

    # helper method to call A instruction for value and push the contents
    # of that to the stack
    def _asm_push_a(self, value):
        asm_cmds = [
            "@{}".format(value),
            "D=A",
        ]
        asm_cmds.extend(self._asm_push_d())
        return asm_cmds
    
    # helper method to call A instruction for value and push the contents
    # of M to the stack
    def _asm_push_m(self, value):
        asm_cmds = [
            "@{}".format(value),
            "D=M",
        ]
        asm_cmds.extend(self._asm_push_d())
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
