C_EMPTY_LINE = "C_EMPTY_LINE"
C_PUSH = "push"
C_POP = "pop"
C_ARITHMETIC = "C_ARITHMETIC"

S_CONSTANT = "constant"
S_LOCAL = "local"
S_ARGUMENT = "argument"
S_THIS = "this"
S_THAT = "that"
S_TEMP = "temp"
S_POINTER = "pointer"
S_STATIC = "static"
S_TEMP_BASE = 5
S_POINTER_BASE = 3

ASM_LOCAL = "LCL"
ASM_ARGUMENT = "ARG"
ASM_THIS = "THIS"
ASM_THAT = "THAT"

ARITHMETIC_COMMANDS = [
    "add",
    "sub",
    "neg",
    "eq",
    "gt",
    "lt",
    "and",
    "or",
    "not",
]

SEGMENTS = {
    S_LOCAL: ASM_LOCAL,
    S_ARGUMENT: ASM_ARGUMENT,
    S_THIS: ASM_THIS,
    S_THAT: ASM_THAT,
    S_CONSTANT: None,
    S_TEMP: None,
    S_POINTER: None,
    S_STATIC: None,
}

PUSH_POP_COMMANDS = [
    "push",
    "pop"
]

COMMANDS = {
    "add": {"args": 0, "type": C_ARITHMETIC},
    "sub": {"args": 0, "type": C_ARITHMETIC},
    "neg": {"args": 0, "type": C_ARITHMETIC},
    "eq": {"args": 0, "type": C_ARITHMETIC},
    "gt": {"args": 0, "type": C_ARITHMETIC},
    "lt": {"args": 0, "type": C_ARITHMETIC},
    "and": {"args": 0, "type": C_ARITHMETIC},
    "or": {"args": 0, "type": C_ARITHMETIC},
    "not": {"args": 0, "type": C_ARITHMETIC},
    "push": {"args": 2, "type": C_PUSH},
    "pop": {"args": 2, "type": C_POP},
}