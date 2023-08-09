import panflute as pf

text = "\\begin{document}Hello World\\end{document}"

def test_pandoc():
    res = pf.convert_text(text, input_format='latex', output_format='html', standalone=False, extra_args=None, pandoc_path=None)
    ans = "<p>Hello World</p>"
    assert res == ans
