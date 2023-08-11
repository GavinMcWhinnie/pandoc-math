
import logging
import sys
import panflute as pf

from pandocmath.ams import AmsthmSettings, AmsTheorem, amsthm_numbering, resolve_ref

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)

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
