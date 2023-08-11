"""
MIT License

Copyright (c) 2023 Gavin McWhinnie

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging
import sys
import panflute as pf
import argparse
import os
import tempfile
import subprocess
import yaml
from pathlib import Path

from pandocmath._version import __version__
from pandocmath.filter import action1, action2, prepare, finalize
from pandocmath.latex_reader import read_metadata_from_file

# Setup logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger : logging.Logger = logging.getLogger(__name__)

# CONSTANTS
PANDOC_OUTPUT_FORMATS : list[str] = pf.run_pandoc(args=['--list-output-formats']).split('\r\n')

def main() -> None:

    parser : argparse.ArgumentParser = argparse.ArgumentParser(
        prog='pandoc-math',
        description='A pandoc filter for converting LaTeX to html for mathematics documents.',
        epilog='For more help, see the documentation at https://gavinmcwhinnie.github.io/pandoc-math/'
    )
    parser.add_argument('file', help='TeX file to be converted')
    parser.add_argument('--version', action='version', version=__version__)
    #parser.add_argument('-o', default='output.html', help='output file')
    args : argparse.Namespace = parser.parse_args()

    if args.file in PANDOC_OUTPUT_FORMATS:

        #### pandoc-math is being called by Pandoc, run as a json filter

        target_format : str = args.file
        if target_format == 'html':

            # Read JSON-encoded document from stdin
            doc : pf.Doc = pf.load()

            # Run panflute filters
            pf.run_filters(
                (action1, action2),
                prepare=prepare,
                finalize=finalize,
                doc=doc,
            )

            # Dump JSON-encoded text string to stdout
            pf.dump(doc)

        else:
            logger.error('The filter pandoc-math is only intended for converting with output to html.')
    else:

        #### pandoc-math is being called by user

        path : Path = Path(args.file)

        if path.is_file():
            filetype : str = path.suffix.lower()
            if filetype == '.tex':

                ####### TODO: finish here
                metadata_file : tempfile.NamedTemporaryFile = tempfile.NamedTemporaryFile(delete=False)

                # Read metadata in from
                metadata : dict = read_metadata_from_file(str(path))
                yaml.dump(metadata, metadata_file, encoding = 'utf-8')

                command : list[str] = ["pandoc", str(path), "-o", path.stem+'.html', "-s", "--mathjax", "--filter", "pandoc-math",
                    "--metadata-file", metadata_file.name, "--number-sections"]
                res : subprocess.CompletedProcess = subprocess.run(command, shell=True, capture_output=True)

                # pandoc-math logging goes to stderr
                stdout : str = res.stdout.decode('utf-8').replace(r"\r\n", r"\n")
                stderr : str = res.stderr.decode('utf-8').replace(r"\r\n", r"\n")
                # Print logging and errors to stdout
                if stdout:
                    print(stdout)
                print(stderr)

                # Close the temporary metadata file
                metadata_file.close()
                os.remove(metadata_file.name)

            else:
                logger.error("Please input a .tex file only.")
        else:
            logger.error("No such file exists: "+str(args.file)+"\nPlease try again.")


if __name__ == "__main__":
    main()
