# pandoc-math
A pandoc filter for converting LaTeX to html for mathematics teaching

Installation
------------

    pip install git+https://github.com/GavinMcWhinnie/pandoc-math --user

Usage
-----

    pandoc input.tex -o output.tex -s --mathjax --filter pandoc-math

Using custom metadata file:
    pandoc input.tex -o output.tex -s --mathjax --metadata-file meta.yaml --filter pandoc-math
