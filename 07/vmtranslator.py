import argparse
import re
import os

from modules.parser import Parser
from modules.parse_error import ParseError
from modules.code_error import CodeError
from modules.code_generator import CodeGenerator
from modules import config



def main(input):
    infiles = []
    # determine if the inputs is a directory or vmfile
    if re.search("\.vm$", input):
        # input is a single .vm file
        infiles.append(input)
        output = input.strip(".vm")
        output = "{}.asm".format(output)
    else:
        try:
            files = os.listdir(input)
            for f in files:
                if re.search("\.vm$", f):
                    infiles.append(os.path.join(input, f))
            # generate output filename
            input = re.sub("/$", "", input)
            output = os.path.join(os.path.abspath(input), "{}.asm".format(os.path.split(input)[1]))
        except Exception as e:
            print("Error attempting to read directory: {}".format(e))
            exit(1)


    # if empty, output error and exit
    if not infiles:
        print("No files found with .vm suffix in {} directory. Exiting".format(input))
        exit(1)
    
    # single code generator for all vm files, single ASM output
    code_gen = CodeGenerator()
    asm_output = code_gen.generate_preamble()

    # loop through all .vm files
    for file in infiles:
        # open and load the file into a list
        vm_input = []
        with open(file) as f:
            vm_input = f.readlines()
        
        # each vm file gets its own parser
        parser = Parser(vm_input)
        while parser.has_more_commands():
            parser.advance()
            try:
                if parser.command_type() is config.C_EMPTY_LINE:
                    # skip whitespace/blank lines
                    continue
                if parser.command_type() == config.C_PUSH:
                    asm_output.extend(code_gen.generate_push_pop(parser.command_type(), parser.arg1(), parser.arg2()))
                if parser.command_type() == config.C_ARITHMETIC:
                    asm_output.extend(code_gen.generate_arithmetic(parser.arg1()))
                    
            except ParseError as err:
                print("Parser error. Expression: <{}>. Error detail: {}".format(err.expression, err.message))
                exit(1)
            except CodeError as err:
                print("Code generator error. Expression: <{}>. Error detail: {}".format(err.expression, err.message))
                exit(1)

    # write out asm file
    with open(output, "w") as f:
        for line in asm_output:
            f.write(line)
            f.write("\n")
        

    



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input .vm file or directory containing .vm files")
    args = parser.parse_args()
    main(args.input)