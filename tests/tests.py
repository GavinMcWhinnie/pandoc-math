import panflute as pf

text = "\\begin{document}Hello World\\end{document}"

res = pf.convert_text(text, input_format='latex', output_format='html', standalone=False, extra_args=None, pandoc_path=None)
