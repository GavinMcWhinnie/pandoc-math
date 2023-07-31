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
from pathlib import Path

from pandocmath.ams import AmsthmSettings, AmsTheorem, amsthm_numbering, resolve_ref

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)

OUTPUT_FORMATS = pf.run_pandoc(args=['--list-output-formats']).split('\r\n')

MATHJAX_CONFIG = "<script> MathJax = {   loader: {     load: [\'[custom]/xypic.js\'],     paths: {custom: \'https://cdn.jsdelivr.net/gh/sonoisa/XyJax-v3@3.0.1/build/\'}   },   tex: {     packages: {\'[+]\': [\'xypic\']},     macros : { relax: ''},     tags: 'ams'   } }; </script>\n\n"

def action1(elem: pf.Element, doc: pf.Doc) -> None:

    amsthm_numbering(elem, doc)

def action2(elem: pf.Element, doc: pf.Doc) -> None:

    resolve_ref(elem, doc)

def prepare(doc: pf.Doc) -> None:

    doc._amsthm_settings = AmsthmSettings(doc)

def finalize(doc : pf.Doc) -> None:

    raw_HEADER : pf.RawBlock = pf.RawBlock(MATHJAX_CONFIG, format='html')
    doc.metadata.content['header-includes'] = pf.MetaBlocks(raw_HEADER)
    del doc._amsthm_settings

def main() -> None:
    parser = argparse.ArgumentParser( description='Hello world!')
    parser.add_argument('file', help='TeX file to be converted')
    #parser.add_argument('-o', default='output.html', help='output file')
    args = parser.parse_args()

    if args.file in OUTPUT_FORMATS:
        #### The filter is being called by Pandoc
        target_format : str = args.file
        if target_format == 'html':
            doc = pf.load()
            pf.run_filters(
                (action1, action2),
                prepare=prepare,
                finalize=finalize,
                doc=doc,
            )
            pf.dump(doc)
        else:
            logger.error('The filter pandoc-math is only intended for converting with output to html.')
    else:

        path = Path(args.file)
        if path.is_file():
            if (filetype := path.suffix.lower()) == '.tex':
                ####### TODO: finish here
                pass
            else:
                logger.error("Please input a .tex file only.")
        else:
            logger.error("No such file exists: "+str(args.file)+"\nPlease try again.")



if __name__ == "__main__":
    main()
