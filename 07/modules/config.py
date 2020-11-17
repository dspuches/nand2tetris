C_EMPTY_LINE = "C_EMPTY_LINE"
C_PUSH = "C_PUSH"
C_ARITHMETIC = "C_ARITHMETIC"

S_CONSTANT = "constant"

ARITHMETIC_COMMANDS = {
    "add",
    "sub",
    "neg",
    "eq",
    "gt",
    "lt",
    "and",
    "or",
    "not",
}

POP_SEGMENTS = []

PUSH_SEGMENTS = POP_SEGMENTS.copy()
PUSH_SEGMENTS.append("constant")

PUSH_POP_COMMANDS = {
    "push"
}

