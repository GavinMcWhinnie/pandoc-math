from pylatexenc.latexwalker import *
from pylatexenc.macrospec import *

# Setup logging
import logging
logger : logging.Logger = logging.getLogger(__name__)

THEOREM_SETTINGS : list[str] = ['numbered','env_name','shared_counter','text','parent_counter']

newtheorem : MacroSpec = MacroSpec("newtheorem", args_parser='*{[{[')
theoremstyle : MacroSpec = MacroSpec("theoremstyle", args_parser='{')
numberwithin : MacroSpec = MacroSpec("numberwithin", args_parser='{{')

db : LatexContextDb = get_default_latex_context_db()
db.add_context_category("amsthm", [newtheorem, theoremstyle, numberwithin])

def extract_text_from_argument(node : LatexNode) -> str:
    text : str = ''
    if node.isNodeType(LatexGroupNode):
        child_node : LatexNode
        for child_node in node.nodelist:
            text += extract_text_from_argument(child_node)
    elif node.isNodeType(LatexCharsNode):
        text += node.chars
    else:
        logger.error("Incorrect Node Type found in argument")

    return text

def get_metadata_from_latex(latex_source : str) -> dict:

    w : latexwalker.LatexWalker = LatexWalker(latex_source, latex_context=db)
    nodelist : list[LatexNode]
    (nodelist, pos, len_) = w.get_latex_nodes(pos=0)

    amsthm_settings : dict = {}
    current_style : str = ''

    node : LatexNode
    for node in nodelist:
        if node.isNodeType(LatexMacroNode):

            if node.macroname == 'theoremstyle':
                if len(node.nodeargs) == 1:
                    current_style = extract_text_from_argument(node.nodeargs[0])
                else:
                    logger.error("Could not extract style from \theoremstyle command.")

            if node.macroname == 'newtheorem':

                theorem_dict : dict = {}
                args : ParsedMacroArgs = node.nodeargd
                for i, arg in enumerate(args.argnlist):
                    if arg:
                        if extract_text_from_argument(arg) == '*':
                            # If theorem environment is not numbered, set 'numbered' to False in `theorem_dict`
                            theorem_dict[THEOREM_SETTINGS[i]] = False
                        else:
                            # Otherwise set the theorem setting to the argument value
                            theorem_dict[THEOREM_SETTINGS[i]] = extract_text_from_argument(arg)

                if current_style in amsthm_settings:
                    amsthm_settings[current_style].append(theorem_dict)
                else:
                    amsthm_settings[current_style] = [theorem_dict]

            if node.macroname == 'numberwithin':

                # Only support numbering equations within section currently,
                # this could be extended to many more counters
                args : list[LatexNode] = node.nodeargd.argnlist
                if len(args) == 2:
                    if extract_text_from_argument(args[0]) == 'equation' and \
                        extract_text_from_argument(args[1]) == 'section':
                            amsthm_settings['number_within'] = True
                    else:
                        logger.warning("pandoc-math only supports \\numberwithin{equation}{section}.")
                else:
                    logger.error("Cannot read latex macro \\numberwithin")

    metadata_dictionary : dict = {'amsthm_settings':amsthm_settings}
    return metadata_dictionary

def read_metadata_from_file(filename : str) -> dict:

    with open(filename, "r") as file:
        return get_metadata_from_latex(file.read())
