# Home

Pandoc-math is a tool for converting latex mathematics documents into html. It is a written as
a [Pandoc filter](https://pandoc.org/filters.html) but also has its own command line interface.

[Pandoc](https://pandoc.org/) is an amazing tool for converting from one markup format into another.
However, when using pandoc for converting latex to html for mathematics documents, there
are a number of issues as pandoc does not provide support for the commonly used
**amsmath** and **amsthm** packages. Pandoc-math seeks to fix these issues when converting latex to html
and provides support for:

 - *Amsthm* theorem environments, styles, qedhere, etc...
 - *Amsmath* commands such as: \\numberwithin, \\eqref

-----------------------

To get started, look at:

- [Installation](installation.md)
- [User Guide](Usage/index.md)
