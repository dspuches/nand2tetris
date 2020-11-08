import argparse
import re

from modules.code import Code
from modules.parser import Parser
from modules.parse_error import ParseError
from modules.symbol_table import SymbolTable

# helper function to translate an a instruction to a binary string
# assumes that symbol is an integer
def translate_a_instruction(symbol):
    return format(int(symbol), '016b')

# helper function to translate a c instruction to a binary string
def translate_c_instruction(comp, dest, jump):
    code = Code(comp, dest, jump)
    return "111{}{}{}".format(code.comp(), code.dest(), code.jump())

# removes whitespace from the list of input lines as well as comments
def remove_whitespace(input):
    processed = []
    for line in input:
        # remove any whitespace 
        stripped = "".join(line.split())
        # remove any comments
        no_comment = stripped.split("//")[0]
        # skip empty lines
        if no_comment != "":
            processed.append(no_comment)
    return processed

def main(infile):
    # read the input file into a list, remove whitespace
    asm_lines = []
    binary_lines = []
    with open(infile) as f:
        asm_lines = f.readlines()
    input = remove_whitespace(asm_lines)

    # first pass, build symbol table
    parser = Parser(input)
    symbol_table = SymbolTable()
    rom_addr = 0
    while parser.has_more_commands():
        parser.advance()
        try:
            if parser.command_type() == parser.C_COMMAND or parser.command_type() == parser.A_COMMAND:
                rom_addr += 1
            else:
                # must be L_COMMAND
                symbol = parser.symbol()
                symbol_table.add_entry(symbol, rom_addr)
        except ParseError as err:
            print("Parser error. Expression: {}. Error detail: {}".format(err.expression, err.message))
            exit(1)
    
    # second pass
    parser = Parser(input)
    ram_addr = 16
    while parser.has_more_commands():
        parser.advance()
        try:
            if parser.command_type() == parser.A_COMMAND:
                symbol = parser.symbol()
                
                try:
                    # if the symbol is a constant (int), translate it
                    int_symbol = int(symbol)
                    binary_lines.append(translate_a_instruction(int_symbol))
                except ValueError:
                    # symbol is not an integer, so either look it up, or its a new variable
                    if symbol_table.contains(symbol):
                        binary_lines.append(translate_a_instruction(symbol_table.get_address(symbol)))
                    else:
                        symbol_table.add_entry(symbol, ram_addr)
                        binary_lines.append(translate_a_instruction(ram_addr))
                        ram_addr += 1
            elif parser.command_type() == parser.C_COMMAND:
                # Translate C command
                binary_lines.append(translate_c_instruction(parser.comp(), parser.dest(), parser.jump()))
        except ParseError as err:
            print("Parser error. Expression: {}. Error detail: {}".format(err.expression, err.message))
            exit(1)
    
    # translation is done. output to new .hack file
    outfile = infile.replace(".asm", "")
    outfile = "{}.hack".format(outfile)
    with open(outfile, "w") as f:
        for line in binary_lines:
            f.write(line)
            f.write("\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help="input assembly file")
    args = parser.parse_args()
    main(args.infile)