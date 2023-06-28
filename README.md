# pandoc-math
A pandoc filter for converting LaTeX to html for mathematics teaching. Provides support for the amsthm package and equation labelling.

Installation
------------

Requires Python > 3.7 which can be installed here: [Python download page](https://www.python.org/downloads/) and Pandoc which can be installed here: [Pandoc installation page](https://pandoc.org/installing.html)

    pip install git+https://github.com/GavinMcWhinnie/pandoc-math

Usage
-----
The basic usage is:

    pandoc input.tex -o output.html -s --mathjax --filter pandoc-math

Using custom metadata file to define custom amsthm shared/parent counters:

    pandoc input.tex -o output.html -s --mathjax --metadata-file metadata.yaml --filter pandoc-math
