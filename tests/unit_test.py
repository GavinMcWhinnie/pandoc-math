import panflute as pf
from pathlib import Path

############ UNIT TESTING ##########################
## Units to be tested:

# __init__.py - not sure how to call with arguments etc...
# latex_reader.py - should be renamed to latex-reader
# filter.py - load full Doc object from latex test file and check it converts correct
# ams.py ? not sure how


from pandocmath.latex_reader import read_metadata_from_file

def test_pandoc():
    text = "\\begin{document}Hello World\\end{document}"
    res = pf.convert_text(text, input_format='latex', output_format='html', standalone=False, extra_args=None, pandoc_path=None)
    ans = "<p>Hello World</p>"
    assert res == ans

def test_latex_reader_from_file():

    expected = {
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

    relative_path = Path("files/latex_reader_test.tex")
    path : Path= Path(__file__).parent / relative_path
    path = path.resolve(strict=True)
    actual = read_metadata_from_file(str(path.resolve()))

    assert expected == actual
