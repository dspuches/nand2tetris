import argparse
import re
import os

from modules.jack_tokenizer import JackTokenizer
from modules.compilation_engine import CompilationEngine

def main(input):
    infiles = []
    outdir = ""
    isdir = False
    # determine if the inputs is a directory or jack file
    if re.search("\.jack$", input):
        # input is a single .jack file
        infiles.append(os.path.abspath(input))
        # determine output directory
        (head, tail) = os.path.split(os.path.abspath(input))
        outdir = head
    else:
        # input is a directory
        outdir = os.path.abspath(input)
        isdir = True
        try:
            files = os.listdir(input)
            for f in files:
                if re.search("\.jack$", f):
                    infiles.append(os.path.join(outdir, f))
        except Exception as e:
            print("Error attempting to read directory: {}".format(e))
            exit(1)

    # if empty, output error and exit
    if not infiles:
        print("No files found with .jack suffix in {} directory. Exiting".format(input))
        exit(1)

    # loop through all .jack files
    if args.tokenize:
        for infile in infiles:
            # only output tokenized xml output file
            token_outfile_name = re.sub("\.jack$", "T.xml", infile)
            token_outfile = os.path.join(outdir, token_outfile_name)
            with open(token_outfile, "w") as out_f:
                with open(infile) as in_f:
                    t = JackTokenizer(in_f)
                    out_f.write(t.token_xml_header())
                    while (t.has_more_tokens()):
                        t.advance()
                        out_f.write(t.token_xml())
                    out_f.write(t.token_xml_trailer())
            
    else:
        # default is to generate output from the compilation engine
        # each input file should have one and only one class
        # so the only compilation engine function that should be called from
        # here for each file is compileClass(). All other functions should be invoked recursively
        # The output generated should be a single XML file


        for infile in infiles:
            outfile_name = re.sub("\.jack$", ".xml", infiles[0])
            outfile = os.path.join(outdir, outfile_name)

            with open(outfile, "w") as out_f:
                with open(infile) as in_f:
                    engine = CompilationEngine(in_f, out_f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input .jack file or directory containing .jack files")
    parser.add_argument("--tokenize", help="generate tokenized output", action="store_true")
    args = parser.parse_args()
    main(args.input)