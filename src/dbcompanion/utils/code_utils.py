import re
import io
import sys
import os
import pandas as pd #dont remove

CODE_PREFIX = """
from types import ModuleType
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')\n
"""

CODE_SUFFIX = """
def is_numeric(obj):
    attrs = ['__add__', '__sub__', '__mul__', '__truediv__', '__pow__']
    return all(hasattr(obj, attr) for attr in attrs)
connection = pymysql.connect(host='{host}', user='{username}', password='{password}', database='{database}', port={port})
result = {function_name}(connection)
if is_numeric(result) and not isinstance(result,(pd.DataFrame,pd.Series)):
    print(result)
elif result is None or isinstance(result,plt.Figure) or isinstance(result, ModuleType):
    plt.savefig("{save_location}/{function_name}.png")
    plt.close()
    print("./{function_name}.png") # saving inside the save_location but printing only function name
elif isinstance(result,(pd.DataFrame,pd.Series)):
    print(result.to_html())
else:
    print(result)
"""

def extract_function_names(text):
    pattern = re.compile(r'\bdef\s+([a-zA-Z_]\w*)\s*\(')
    matches = pattern.findall(text)
    return matches

def get_executable_code(llm_response:str,connection_param_dict:str,save_location:str):
    connection_param_dict['function_name'] = extract_function_names(llm_response)[0]
    connection_param_dict['save_location'] = save_location
    executable_code = CODE_PREFIX + llm_response + CODE_SUFFIX.format_map(connection_param_dict)
    return executable_code

def get_execution_output(code):
    output_buffer = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = output_buffer
    try:
        exec(code)
    finally:
        sys.stdout = original_stdout
    captured_output = output_buffer.getvalue()
    return captured_output

class HidePrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

def in_notebook():
    """
    Returns ``True`` if the module is running in IPython kernel,
    ``False`` if in IPython shell or other Python shell.
    """
    return 'ipykernel' in sys.modules