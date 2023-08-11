import logging
logger = logging.getLogger(__name__)

from pylatexenc.latexwalker import *
from pylatexenc.macrospec import *
import yaml
import tempfile, os

THEOREM_SETTINGS = ['numbered','env_name','shared_counter','text','parent_counter']

newtheorem = macrospec.MacroSpec("newtheorem", args_parser='*{[{[')
theoremstyle = macrospec.MacroSpec("theoremstyle", args_parser='{')
numberwithin = macrospec.MacroSpec("numberwithin", args_parser='{{')

db = get_default_latex_context_db()
db.add_context_category("amsthm", [newtheorem, theoremstyle, numberwithin])

def extract_text_from_argument(node):
    text = ''
    if node.isNodeType(LatexGroupNode):
        for child_node in node.nodelist:
            text += extract_text_from_argument(child_node)
    elif node.isNodeType(LatexCharsNode):
        text += node.chars
    else:
        logger.error("Incorrect Node Type found in argument")

    return text

def read_metadata_from_file(filename):

    with open(filename, "r") as file:

        w = LatexWalker(file.read(), latex_context=db)
        (nodelist, pos, len_) = w.get_latex_nodes(pos=0)

        amsthm_settings = {}
        current_style = ''

        for node in nodelist:
            if node.isNodeType(LatexMacroNode):

                if node.macroname == 'theoremstyle':
                    if len(node.nodeargs) == 1:
                        current_style = extract_text_from_argument(node.nodeargs[0])
                    else:
                        logger.error("Could not extract style from \theoremstyle command.")

                if node.macroname == 'newtheorem':

                    theorem_dict = {}
                    args = node.nodeargs
                    for i, arg in enumerate(args):
                        if arg:
                            if extract_text_from_argument(arg) == '*':
                                theorem_dict[THEOREM_SETTINGS[i]] = False
                            else:
                                theorem_dict[THEOREM_SETTINGS[i]] = extract_text_from_argument(arg)

                    if current_style in amsthm_settings:
                        amsthm_settings[current_style].append(theorem_dict)
                    else:
                        amsthm_settings[current_style] = [theorem_dict]

                if node.macroname == 'numberwithin':
                    #### TODO make this more robust/general

                    amsthm_settings['number_within'] = True

    dictionary = {'amsthm_settings':amsthm_settings}
    return dictionary
"""

def print_group_node(node):
    string = ""
    if node.nodelist:
        for sub_node in node.nodelist:
            if sub_node.isNodeType(LatexCharsNode):
                string += sub_node.chars
    return node.delimiters[0] + string + node.delimiters[1]

def extract_text(node):
    if node.nodelist:
        if node.nodelist[0].isNodeType(LatexCharsNode):
            return node.nodelist[0].chars
    logger.error("uh oh")

file = "C:\\Users\\gmcwhinn\\Documents\\GitHub\\pandoc-math\\pandocmath\\input.tex"

f = open(file, "r")

newtheorem = macrospec.MacroSpec("newtheorem", args_parser='*{[{[')
theoremstyle = macrospec.MacroSpec("theoremstyle", args_parser='{')
numberwithin = macrospec.MacroSpec("numberwithin", args_parser='{{')

db = get_default_latex_context_db()
db.add_context_category("amsthm", [newtheorem, theoremstyle, numberwithin])

w = LatexWalker(f.read(), latex_context=db)
(nodelist, pos, len_) = w.get_latex_nodes(pos=0)

#{'amsthm_settings': {'number_within': True, 'definition':
#[{'env_name': 'lemma', 'text': 'Lemma', 'parent_counter': 'section'}]}}
amsthm_settings = {'definition':[],'plain':[],'remark':[]}

settings = ['env_name','shared_counter','text','parent_counter']


style = ''
for i, node in enumerate(nodelist):

    if node.isNodeType(LatexMacroNode):

        if node.macroname == 'theoremstyle':
            for arg in node.nodeargs:
                style = extract_text(arg)

        if node.macroname == 'newtheorem':
            print(i)
            theorem_dict = {}
            for i, arg in enumerate(node.nodeargs):
                if arg:
                    if arg.isNodeType(LatexGroupNode):
                        if i != 0:
                            theorem_dict[settings[i-1]] = extract_text(arg)

            amsthm_settings[style].append(theorem_dict)


        if node.macroname == 'numberwithin':
            amsthm_settings['numberwithin'] = True
            #print(i)
            #print("\\numberwithin")
            #for arg in node.nodeargs:
            #    if arg:
            #        print(print_group_node(arg))


f.close()

dictionary = {'amsthm_settings':amsthm_settings}

tmp = tempfile.NamedTemporaryFile(delete=False)
print(tmp.name)
yaml.dump(dictionary, tmp, encoding = 'utf-8')

#### DO PANDOC COMMAND HERE

tmp.close()
os.remove(tmp.name)
"""
