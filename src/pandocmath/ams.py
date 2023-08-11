"""

This file is based on and contains code from https://github.com/ickc/pandoc-amsthm.

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

from dataclasses import dataclass
import logging
import panflute as pf
import re

logger = logging.getLogger(__name__)

# Constants
AMSTHM_STYLES = ["plain", "definition", "remark"]
MAX_SECTION_DEPTH = 3
LEVEL_TO_SECTION = {1: "section", 2: "subsection", 3: "subsubsection"}

# Type Aliases
THEOREM_DATA = dict[str,str]

@dataclass
class AmsTheorem:
    style: str
    env_name: str
    text: str
    parent_counter: str | None = None
    shared_counter: str | None = None
    numbered: bool = True

class AmsthmSettings:

    theorems: dict[str, AmsTheorem]
    section_counters : list[int]
    theorem_counters : dict[str, int]
    identifiers : dict[str, str]
    number_within: bool = False
    equation_counter : int

    def __init__(self, doc: pf.Doc) -> None:
        self.theorems = {}
        self.section_counters = [0]*3
        self.theorem_counters = {}
        self.identifiers = {}
        self.equation_counter = 1
        self.read_metadata(doc)

        # Add the pre-defined proof environment to theorems
        proof : AmsTheorem = AmsTheorem("proof", "proof", "Proof", numbered=False)
        self.theorems['proof'] = proof

    def read_metadata(self, doc: pf.Doc) -> None:
        """
            Read amsthm_settings metadata to setup options on theorem styles and counters.
        """

        metadata: dict[str, dict] = doc.get_metadata("amsthm_settings")

        if (numberwithin := metadata.get('number_within')):
            self.number_within = numberwithin
            logger.info('Numbering within sections set to: '+str(numberwithin).upper())

        for style in AMSTHM_STYLES:
            theorems_list: list[THEOREM_DATA] = metadata.get(style)
            if theorems_list:
                for theorem in theorems_list:
                    # Get individual theorem data from metadata
                    env_name : str = theorem.get('env_name')
                    text : str = theorem.get('text')
                    parent_counter : str = theorem.get('parent_counter')
                    shared_counter : str = theorem.get('shared_counter')
                    numbered : bool = theorem.get('numbered', True)

                    # NewTheorem environment has shared counter
                    if shared_counter is not None:
                        self.theorem_counters[shared_counter] = 0
                        if parent_counter is not None:
                            logger.warning("AmsTheorem %s has both a parent and shared counter.", env_name)

                    # Create AmsTheorem dataclass and add to list of theorems
                    new_theorem : AmsTheorem = AmsTheorem(style, env_name, text, parent_counter, shared_counter, numbered)
                    self.theorems[env_name] = new_theorem
                    logger.info('Added new AmsTheorem: %s.', new_theorem.text)



def replace_qed_here(elem: pf.Element, doc: pf.Doc) -> None:
    """
        Helper function that replaces \qedhere in proof environment.
    """

    qed_symbol : str = chr(9723)

    if isinstance(elem, pf.Math):
        # Replace qedhere with equation tag containing '◻'
        if "\\qedhere" in elem.text:
            elem.text = elem.text.replace("\\qedhere","\\tag*{"+qed_symbol+"}")

    if isinstance(elem, pf.Str):
        # Remove the original '◻' at the end of the proof
        if qed_symbol in elem.text:
            return []


def amsthm_numbering(elem: pf.Element, doc: pf.Doc) -> None:
    """
        Action that re-numbers amsthm environments and numbers labelled equations.
    """

    amsthm_settings: AmsthmSettings = doc._amsthm_settings

    if isinstance(elem, pf.Header):
        level : int = elem.level
        section : str = LEVEL_TO_SECTION.get(level)
        if level <= MAX_SECTION_DEPTH:


            # Add one to counter and reset deeper counters
            amsthm_settings.section_counters[level - 1] += 1
            for i in range(elem.level, MAX_SECTION_DEPTH):
                amsthm_settings.section_counters[i] = 0

            #### If any theorem counters have section:level as parent, reset
            for theorem_counter in amsthm_settings.theorem_counters:
                if amsthm_settings.theorems[theorem_counter].parent_counter == section:
                    amsthm_settings.theorem_counters[theorem_counter] = 0

            # Reset equation counter on new section
            if section == 'section':
                amsthm_settings.equation_counter = 1


    elif isinstance(elem, pf.Math):

        if re.findall(r'\\label{.*}', elem.text):

            if re.search(r'\\begin{aligned}', elem.text):
                # MathJax doesn't number 'aligned' environments, so change to 'align'
                elem.text = re.sub(r'\\begin{aligned}', r'\\begin{align}', elem.text)
                elem.text = re.sub(r'\\end{aligned}', r'\\end{align}', elem.text)


                matches = re.finditer(r'\\label{.*}', elem.text)
                offset_from_previously_added = 0
                for match in matches:
                    if amsthm_settings.number_within:
                        equation_number : str = str(amsthm_settings.section_counters[0]) + '.' + str(amsthm_settings.equation_counter)
                        # Calculate index of end of match, accounting for adding characters to elem.text previously
                        index = match.end() + offset_from_previously_added
                        elem.text = elem.text[:index] + '\\tag{'+equation_number+'}' + elem.text[index:]
                        offset_from_previously_added += len('\\tag{'+equation_number+'}')
                    amsthm_settings.equation_counter += 1
            else:
                # Put Math inside \begin{equation} tags so that MathJax automatically numbers the equation
                current_text : str = elem.text
                if amsthm_settings.number_within:
                    equation_number : str = str(amsthm_settings.section_counters[0]) + '.' + str(amsthm_settings.equation_counter)
                    elem.text = '\\begin{equation}' + current_text + '\\tag{'+equation_number+'}' + '\\end{equation}'
                else:
                    elem.text = '\\begin{equation}' + current_text +  '\\end{equation}'

                amsthm_settings.equation_counter += 1

        return elem

    elif isinstance(elem, pf.Div):
        environments: set[str] = set(amsthm_settings.theorems).intersection(elem.classes)
        if environments:
            if len(environments) != 1:
                logger.warning("Multiple environments found: %s", environments)
                return None
            env_name : str = environments.pop()

            if env_name == 'proof':
                # Move the qed symbol in the case the user writes \qedhere
                if re.search(r'\\qedhere', str(elem.content)):
                        elem.walk(replace_qed_here)
            else:
                theorem_type : AmsTheorem = amsthm_settings.theorems[env_name]
                id : str = elem.identifier

                ## Update counters
                if (thm_counter := theorem_type.shared_counter) is not None:
                    amsthm_settings.theorem_counters[thm_counter] += 1
                elif env_name in amsthm_settings.theorem_counters:
                    thm_counter = env_name
                    amsthm_settings.theorem_counters[env_name] += 1

                #################################################################
                ## NEED: improve this section to make it more robust and readable.

                theorem_number : str = str(amsthm_settings.section_counters[0]) + '.' + str(amsthm_settings.theorem_counters[thm_counter])
                theorem_text : list[pf.Element] = [pf.Str(theorem_type.text), pf.Space, pf.Str(theorem_number)]

                amsthm_settings.identifiers[id] = theorem_number

                if not isinstance(elem.content[0], pf.Para):
                    logger.warning("Theorem environment not wrapped in Para!")
                elif not isinstance(elem.content[0].content[0], pf.Strong):
                    logger.warning('Theorem environment does not have a Strong elem at the start!')
                else:
                    strong : pf.Strong = elem.content[0].content[0]
                    strong.content = theorem_text

def link_to_ref_type(elem: pf.Link) -> tuple[str, str] | None:
    """
        Takes a panflute Link element and returns its reference and reference-type.
    """

    if not 'reference' in elem.attributes:
        logger.warning("Link: %s has no reference. Ignoring...", elem)
        return None

    reference : pf.Str = elem.attributes.get('reference', None)
    type = elem.attributes.get('reference-type', None)

    return reference, type


def resolve_ref(elem: pf.Element, doc: pf.Doc) -> None:
    """
        Action that corrects Link text for theorem and equation references.
    """

    amsthm_settings: AmsthmSettings = doc._amsthm_settings
    if isinstance(elem, pf.Link):
        ref, type = link_to_ref_type(elem)

        if type == "eqref":
            # Put \eqref inside Math tags, so that MathJax can see it
            elem.content = [pf.Math("\\eqref{"+ref+"}",format='InlineMath')]
            return elem

        elif type is not None and ref in amsthm_settings.identifiers:
            if type == "ref":
                # if reference is in identifiers, replace it with correct text
                elem.content = [pf.Str(amsthm_settings.identifiers[ref])]
                return elem

### TODO:
#  - if it is a plain style, make it italic.
#  - are styles exactly right? -- currently all the same.
#  - if it is display math and has \label, put it in \begin{equation} tags?
#  - add mathjax config with support for ams, and \numberwithin command

## EXTRAS?
# - number swapping in theorems?
