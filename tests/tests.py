import panflute as pf

############ UNIT TESTING ##########################
## Units to be tested:

# __init__.py - not sure how to call with arguments etc...
# helper.py - should be renamed to latex-reader
# filter.py - load full Doc object from latex test file and check it converts correct
# ams.py ? not sure how




text = "\\begin{document}Hello World\\end{document}"

def test_pandoc():
    res = pf.convert_text(text, input_format='latex', output_format='html', standalone=False, extra_args=None, pandoc_path=None)
    ans = "<p>Hello World</p>"
    assert res == ans
