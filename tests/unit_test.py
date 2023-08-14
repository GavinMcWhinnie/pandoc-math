import panflute as pf
from pathlib import Path

############ UNIT TESTING ##########################
## Units to be tested:

# __init__.py - not sure how to call with arguments etc...
# latex_reader.py - should be renamed to latex-reader
# filter.py - load full Doc object from latex test file and check it converts correct
# ams.py ? not sure how


SAMPLE_METADATA = {
'amsthm_settings': {
    'definition':
        [{'env_name': 'definition', 'text': 'Definition', 'parent_counter': 'section'},
        {'env_name': 'theorem', 'shared_counter': 'definition', 'text': 'Theorem'},
        {'env_name': 'example', 'shared_counter': 'definition', 'text': 'Example'}],
    'plain':
        [{'env_name': 'remarks', 'text': 'Remarks', 'parent_counter': 'section'},
        {'env_name': 'ackn', 'shared_counter': 'remarks', 'text': 'Acknowledgements'}],
    'number_within': True
}}

from pandocmath.latex_reader import read_metadata_from_file

def test_pandoc():
    text = "\\begin{document}Hello World\\end{document}"
    res = pf.convert_text(text, input_format='latex', output_format='html', standalone=False, extra_args=None, pandoc_path=None)
    ans = "<p>Hello World</p>"
    assert res == ans

def test_latex_reader_from_file():

    expected = SAMPLE_METADATA

    relative_path = Path("files/latex_reader_test.tex")
    path : Path= Path(__file__).parent / relative_path
    path = path.resolve(strict=True)
    actual = read_metadata_from_file(str(path.resolve()))

    assert expected == actual

from pandocmath.ams import AmsthmSettings, AmsTheorem

def test_read_metadata():


    doc : pf.Doc = pf.Doc()
    doc.metadata = SAMPLE_METADATA

    amsthm_settings = AmsthmSettings(doc)
    theorems = amsthm_settings.theorems

    for name, theorem in amsthm_settings.theorems.items():
        assert isinstance(theorem, AmsTheorem)

    env_names = ['definition','theorem','example','remarks','ackn']
    for env_name in env_names:
        assert theorems[env_name].env_name == env_name

    assert theorems['definition'].parent_counter == 'section'
    assert theorems['ackn'].shared_counter == 'remarks'

    assert amsthm_settings.number_within == True
