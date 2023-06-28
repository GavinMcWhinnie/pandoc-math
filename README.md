# pandoc-math
A pandoc filter for converting LaTeX to html for mathematics teaching. Provides support for the amsthm package and equation labelling.

Installation
------------

    pip install git+https://github.com/GavinMcWhinnie/pandoc-math --user

Usage
-----
The basic usage is:

    pandoc input.tex -o output.html -s --mathjax --filter pandoc-math

Using custom metadata file to define custom amsthm shared/parent counters:

    pandoc input.tex -o output.html -s --mathjax --metadata-file meta.yaml --filter pandoc-math
