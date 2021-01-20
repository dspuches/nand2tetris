from errors.vm_writer_error import VmWriterError

class VmWriter:
    S_CONSTANT = "constant"
    S_LOCAL = "local"
    S_ARGUMENT = "argument"
    S_THIS = "this"
    S_THAT = "that"
    S_TEMP = "temp"
    S_POINTER = "pointer"
    S_STATIC = "static"

    SEGMENTS = [
        S_CONSTANT,
        S_LOCAL,
        S_ARGUMENT,
        S_THIS,
        S_THAT,
        S_TEMP,
        S_POINTER,
        S_STATIC,
    ]

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

    # Assumes out_f is already an open file descriptor
    def __init__(self, out_f):
        self._fd = out_f
    
    def _validate_segment_index(self, segment, index):
        if segment not in self.SEGMENTS:
            raise VmWriterError("Invalid segment: <{}>".format(segment))
        try:
            int(index)
        except ValueError:
            raise VmWriterError("Invalid index: <{}>".format(index))
    
    def _println(self, line):
        self._fd.write("{}\n".format(line))

    def write_push(self, segment, index):
        self._validate_segment_index(segment, index)
        self._println("push {} {}".format(segment, index))

    def write_pop(self, segment, index):
        self._validate_segment_index(segment, index)
        self._println("pop {} {}".format(segment, index))

    def write_arithmetic(self, command):
        if command not in self.ARITHMETIC_COMMANDS:
            raise VmWriterError("Invalid arithmetic command: <{}>".format(command))
        self._println(command)

    def write_label(self, label):
        self._println("label {}".format(label))

    def write_goto(self, label):
        self._println("goto {}".format(label))

    def write_if(self, label):
        self._println("if-goto {}".format(label))

    def write_call(self, name, num_args):
        self._println("call {} {}".format(name, num_args))

    def write_function(self, name, num_locals):
        self._println("function {} {}".format(name, num_locals))

    def write_return(self):
        self._println("return")