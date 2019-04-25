import ast
import sys
from collections import defaultdict

def not_found():
    print('WARNING: missing in language dictionary')
    return '<?????>'

Dict = defaultdict(not_found)

def load_dict(lang):
    Dict.clear()
    file = lang + '.i18n'
    try:
        with open(file) as f:
            Dict.update(ast.literal_eval(f.read()))
    except BaseException:
        print('Error loading language file')
        sys.exit(1)

