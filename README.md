# pandoc-math
A pandoc filter for converting LaTeX to html for mathematics documents. Provides support for various environments & commands in the amsthm/amsmath packages and equation labelling & referencing.

Installation
------------

Requires Python > 3.7 which can be installed here: [Python download page](https://www.python.org/downloads/) and Pandoc > 2.11 which can be installed here: [Pandoc installation page](https://pandoc.org/installing.html).

To download pandoc-math, use the pip tool with the command:

    pip install git+https://github.com/GavinMcWhinnie/pandoc-math

Documentation:
-------------
https://gavinmcwhinnie.github.io/pandoc-math

Usage
-----

The basic usage of pandoc-math is:

    pandoc-math [file] [options]

Where  `[file]` is a `.TeX` file to be converted to html.
