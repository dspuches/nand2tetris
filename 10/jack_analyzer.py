import argparse
import re
import os

from modules.jack_tokenizer import JackTokenizer

def main(input):
    infiles = []
    outdir = ""
    # determine if the inputs is a directory or vmfile
    if re.search("\.jack$", input):
        # input is a single .jack file
        infiles.append(input)
        # determine output directory
        (head, tail) = os.path.split(os.path.abspath(input))
        outdir = head
    else:
        # input is a directory
        outdir = os.path.abspath(input)
        try:
            files = os.listdir(input)
            for f in files:
                if re.search("\.jack$", f):
                    infiles.append(f)
        except Exception as e:
            print("Error attempting to read directory: {}".format(e))
            exit(1)

    # if empty, output error and exit
    if not infiles:
        print("No files found with .jack suffix in {} directory. Exiting".format(input))
        exit(1)

    # loop through all .jack files
    for infile in infiles:
        if args.tokenize:
            # only output tokenized xml output file
            # token_outfile_name = re.sub("\.jack$", "T.xml", infile)
            # token_outfile = os.path.join(outdir, token_outfile_name)
            # with open(infile) as f:
            #     jack_input = f.readlines()
            t = JackTokenizer(infile)
            while (t.has_more_tokens()):
                print("*{}*".format(t._next_lexeme))
                t.advance()

            
            # print("input = {}".format(infile))
            # print("outdir = {}".format(outdir))
            # print("token_outfile = {}".format(token_outfile))
        else:
            # default is to generate output from the compilation engine
            pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input .jack file or directory containing .jack files")
    parser.add_argument("--tokenize", help="generate tokenized output", action="store_true")
    args = parser.parse_args()
    main(args.input)