"""

This contains code from https://github.com/ickc/pandoc-amsthm.

BSD 3-Clause License

Copyright (c) 2016-2021, Kolen Cheung
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

It has been modified by Gavin McWhinnie as part of github.com/GavinMcWhinnie/pandoc-math.

MIT License

Copyright (c) 2023 Gavin McWhinnie

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""



from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from functools import cached_property, partial
from typing import TYPE_CHECKING

import panflute as pf
from panflute.tools import convert_text

if TYPE_CHECKING:
    from typing import Union

    from panflute.elements import Doc, Element

    THM_DEF = list[Union[str, dict[str, str], dict[str, list[str]]]]

__version__: str = "2.0.0"

MATHJAX_CONFIG = "<script> MathJax = {   loader: {     load: [\'[custom]/xypic.js\'],     paths: {custom: \'https://cdn.jsdelivr.net/gh/sonoisa/XyJax-v3@3.0.1/build/\'}   },   tex: {     packages: {\'[+]\': [\'xypic\']},     macros : { relax: '', qedhere: ''},     tags: \'ams\'   } }; </script>\n\n"


PARENT_COUNTERS: set[str] = {
    "part",
    "chapter",
    "section",
    "subsection",
    "subsubsection",
    "paragraph",
    "subparagraph",
}
STYLES: tuple[str, ...] = ("plain", "definition", "remark")
METADATA_KEY: str = "amsthm"
REF_REGEX = re.compile(r"^\\(ref|eqref)\{(.*)\}$")
LATEX_LIKE: set[str] = {"latex", "beamer"}
PLAIN_OR_DEF: set[str] = {"plain", "definition"}
COUNTER_DEPTH_DEFAULT: int = 0


def parse_info(info: str | None) -> list[Element]:
    """Convert theorem info to panflute AST inline elements."""
    return [pf.Str(r"(")] + parse_markdown_as_inline(info) + [pf.Str(r")")] if info else []


@dataclass
class NewTheorem:
    style: str
    env_name: str
    text: str = ""
    parent_counter: str | None = None
    shared_counter: str | None = None
    numbered: bool = True
    """A LaTeX amsthm new theorem.

    :param parent_counter: for LaTeX output, controlling the number of numbers in a theorem.
        Should be used with counter_depth to match LaTeX and non-LaTeX output.
    """

    def __post_init__(self) -> None:
        if self.env_name.endswith("*"):
            self.env_name = self.env_name[:-1]
            self.numbered = False
        if not self.text:
            #logger.debug("Defaulting text to %s", self.env_name.capitalize())
            self.text = self.env_name.capitalize()
        if (parent_counter := self.parent_counter) is not None and parent_counter not in PARENT_COUNTERS:
            #logger.warning("Unsupported parent_counter %s, ignoring.", parent_counter)
            pass
        if self.numbered and parent_counter is not None and self.shared_counter is not None:
            #logger.warning("Dropping shared_counter as parent_counter is defined.")
            self.shared_counter = None

    @property
    def class_name(self) -> str:
        """Name in pandoc div classes.

        It cannot have space.
        """
        return self.env_name.replace(" ", "_")

    @property
    def counter_name(self) -> str:
        return self.env_name if self.shared_counter is None else self.shared_counter

    def to_panflute_theorem_header(
        self,
        options: DocOptions,
        id: str | None,
        info: str | None,
    ) -> list[pf.Element]:
        """Return a theorem header as panflute AST.

        This mutates `options.theorem_counters`, `options.identifiers` in-place.
        """
        TextType: type[Element]
        text = self.text

        # text and number separated by Space

        NumberType: type[Element]
        theorem_number: str | None
        if self.numbered:
            counter_name = self.counter_name
            options.theorem_counters[counter_name] += 1
            theorem_counter = options.theorem_counters[counter_name]
            theorem_number = ".".join([str(i) for i in options.header_counters] + [str(theorem_counter)])
            if id:
                options.identifiers[id] = theorem_number
        else:
            theorem_number = None

        # no additional styling here
        info_list = parse_info(info)

        # append TextType of ".", Space

        # cases: PLAIN_OR_DEF, theorem_number, info_list
        if self.style in PLAIN_OR_DEF:
            TextType = pf.Strong
            NumberType = pf.Strong
        else:
            TextType = pf.Emph
            NumberType = pf.Str
        # We are normalizing the Emph/Strong boundary manually by having 6 cases
        if theorem_number is None:
            if info_list:
                res = [TextType(pf.Str(text)), pf.Space] + info_list #+ [TextType(pf.Str(".")), pf.Space]
            else:
                res = [TextType(pf.Str(f"{text}"))]# + [TextType(pf.Str(".")), pf.Space]
        else:
            if TextType is NumberType:
                if info_list:
                    res = (
                        [TextType(pf.Str(f"{text} {theorem_number}")), pf.Space]
                        + info_list
                        #+ [TextType(pf.Str(".")), pf.Space]
                    )
                else:
                    res = [TextType(pf.Str(f"{text} {theorem_number}"))] #+ [TextType(pf.Str(".")), pf.Space]
            else:
                if info_list:
                    res = (
                        [TextType(pf.Str(text)), pf.Space, pf.Str(theorem_number), pf.Space]
                        + info_list
                        #+ [TextType(pf.Str(".")), pf.Space]
                    )
                else:
                    res = [
                        TextType(pf.Str(text)),
                        pf.Space,
                        pf.Str(theorem_number),
                        #TextType(pf.Str(".")),
                        #pf.Space,
                    ]
        return res


@dataclass
class Proof(NewTheorem):
    style: str = "proof"
    env_name: str = "proof"
    text: str = "proof"
    parent_counter: str | None = None
    shared_counter: str | None = None
    numbered: bool = False

    def to_panflute_theorem_header(
        self,
        options: DocOptions,
        id: str | None,
        info: str | None,
    ) -> list[pf.Element]:
        """Return a theorem header as panflute AST."""
        if info is None:
            return [pf.Emph(pf.Str("Proof.")), pf.Space]
        else:
            # put it into a Para then walk
            ast = parse_markdown_as_inline(info)
            info_list = pf.Para(*ast)
            info_list.walk(to_emph)
            info_list.walk(cancel_emph)
            info_list.walk(merge_emph)
            return list(info_list.content) + [pf.Emph(pf.Str(".")), pf.Space]


@dataclass
class DocOptions:
    """Document options.

    :param: counter_depth: can be n=0-6 inclusive.
        n means n+1 numbers shown in non-LaTeX outputs.
        e.g. n=1 means x.y, where x is the heading 1 counter, y is the theorem counter.
        Should be used with parent_counter to match LaTeX and non-LaTeX output.
    """

    theorems: dict[str, NewTheorem] = field(default_factory=dict)
    counter_depth: int = COUNTER_DEPTH_DEFAULT
    counter_ignore_headings: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        try:
            self.counter_depth = int(self.counter_depth)
        except ValueError:
            #logger.warning("counter_depth must be int, default to 1.")
            self.counter_depth = COUNTER_DEPTH_DEFAULT

        # initial count is zero
        # should be += 1 before using
        self.header_counters: list[int] = [0] * self.counter_depth
        self.reset_theorem_counters()
        # from identifiers to numbers
        self.identifiers: dict[str, str] = {}

    def reset_theorem_counters(self) -> None:
        self.theorem_counters: dict[str, int] = defaultdict(int)

    @cached_property
    def theorems_set(self) -> set[str]:
        return set(self.theorems)

    @classmethod
    def from_doc(
        cls,
        doc: Doc,
    ) -> DocOptions:
        options: dict[
            str,
            dict[str, str | dict[str, str] | THM_DEF],
        ] = doc.get_metadata(METADATA_KEY, {})

        name_to_text: dict[str, str] = options.get("name_to_text", {})  # type: ignore[assignment, arg-type]
        parent_counter: str = options.get("parent_counter", None)  # type: ignore[assignment, arg-type]

        theorems: dict[str, NewTheorem] = {}
        for style in STYLES:
            option: THM_DEF = options.get(style, [])  # type: ignore[assignment]
            for opt in option:
                if isinstance(opt, dict):
                    for key, value in opt.items():
                        # key
                        theorem = NewTheorem(style, key, text=name_to_text.get(key, ""), parent_counter=parent_counter)
                        theorems[theorem.class_name] = theorem
                        # value(s)
                        if isinstance(value, list):
                            for v in value:
                                theorem = NewTheorem(style, v, text=name_to_text.get(v, ""), shared_counter=key)
                                theorems[theorem.class_name] = theorem
                        else:
                            v = value
                            theorem = NewTheorem(style, v, text=name_to_text.get(v, ""), shared_counter=key)
                            theorems[theorem.class_name] = theorem
                else:
                    key = opt
                    theorem = NewTheorem(style, key, text=name_to_text.get(key, ""), parent_counter=parent_counter)
                    theorems[theorem.class_name] = theorem
        # proof is predefined in amsthm
        theorems["proof"] = Proof()
        return cls(
            theorems,
            counter_depth=options.get("counter_depth", COUNTER_DEPTH_DEFAULT),  # type: ignore[arg-type] # will be verified at __post_init__
            counter_ignore_headings=set(options.get("counter_ignore_headings", set())),
        )

    @property
    def to_panflute(self) -> pf.RawBlock:
        return pf.RawBlock(self.latex, format="latex")


def prepare(doc: Doc) -> None:
    # add mathjax config to header
    raw_HEADER = pf.RawBlock(MATHJAX_CONFIG, format='html')
    doc.metadata.content['header-includes'] = pf.MetaBlocks(raw_HEADER)
    # generate amsthm data and store doc attribute
    doc._amsthm = options = DocOptions.from_doc(doc)


def amsthm(elem: Element, doc: Doc) -> None:
    """General amsthm transformation working for all document types.

    Essentially we replicate LaTeX amsthm behavior in this filter.
    """
    options: DocOptions = doc._amsthm
    if isinstance(elem, pf.Header):
        if elem.level <= options.counter_depth:
            header_string = None
            if (counter_ignore_headings := options.counter_ignore_headings) and (
                header_string := pf.stringify(elem)
            ) in counter_ignore_headings:
                pass
                #logger.debug("Ignoring header %s in header_counters as it is in counter_ignore_headings", header_string)
            else:
                # Header.level is 1-indexed, while list is 0-indexed
                options.header_counters[elem.level - 1] += 1
                # reset deeper levels
                for i in range(elem.level, options.counter_depth):
                    options.header_counters[i] = 0
                #logger.debug(
                #    "Header encounter: %s, current counter: %s", header_string or elem, options.header_counters
                #)
                options.reset_theorem_counters()
    elif isinstance(elem, pf.Math):

        if elem.format == 'DisplayMath':
            if re.search(r'\\label{.*}',elem.text):
                current_text = elem.text
                elem.text = "\\begin{equation}" + current_text + "\\end{equation}"
                return elem
    elif isinstance(elem, pf.Div):
        environments: set[str] = options.theorems_set.intersection(elem.classes)
        if environments:
            if len(environments) != 1:
                #logger.warning("Multiple environments found: %s", environments)
                return None
            environment = environments.pop()
            theorem = options.theorems[environment]

            info = elem.attributes.get("info", None)
            id = elem.identifier

            res = theorem.to_panflute_theorem_header(options, id, info)

            # theorem body
            if theorem.style == "plain":
                elem.walk(to_emph)
                elem.walk(cancel_emph)
                elem.walk(merge_emph)

            # if not numbered then pandoc already has it correcct
            if theorem.numbered == True:

                try:

                    if isinstance(elem.content[0].content[0], pf.Strong):
                        elem.content[0].content.pop(0)

                    for r in reversed(res):
                        elem.content[0].content.insert(0, r)

                except AttributeError:
                    #remove Strong

                    if isinstance(elem.content[0], pf.Strong):
                        elem.content.pop(0)

                    elem.content.insert(0, pf.Para(*res))

                return elem

def cite_to_id_mode(elem: pf.Cite) -> tuple[str, str] | None:
    if len(elem.citations) != 1:
        #logger.warning("Not only have 1 citations in Cite: %s. Ignoring...", elem)
        return None
    citation: pf.Citation = elem.citations[0]
    id = citation.id
    mode = citation.mode
    return id, mode

def link_to_ref_type(elem: pf.Link) -> tuple[str, str] | None:
    if not 'reference' in elem.attributes:
        #logger.warning("Link: %s has no reference. Ignoring...", elem)
        return None
    reference: pf.Str = elem.attributes.get('reference', None)
    type = elem.attributes.get('reference-type', None)
    return reference, type


def resolve_ref(elem: Element, doc: Doc) -> pf.Str | None:
    """Resolve references to theorem numbers.

    Consider this as post-process ref for general output formats.
    """
    options: DocOptions = doc._amsthm
    # from \ref{} to number
    if isinstance(elem, pf.Link):
        ref, type = link_to_ref_type(elem)
        if type == "eqref":
            elem.content = [pf.Math("\\eqref{"+ref+"}",format='InlineMath')]
            return elem
        if type is not None and ref in options.identifiers:
            if type == "ref":
                elem.content = [pf.Str(options.identifiers[ref])]
                return elem

    return None


def action1(elem: Element, doc: Doc) -> pf.RawBlock | None:
    amsthm(elem, doc)
    return None

def action2(elem: Element, doc: Doc) -> pf.Str | pf.RawInline | None:
    return resolve_ref(elem, doc)


def finalize(doc: Doc) -> None:
    del doc._amsthm


def main(doc: Doc | None = None) -> None:
    return pf.run_filters(
        (action1, action2),
        prepare=prepare,
        finalize=finalize,
        doc=doc,
    )
