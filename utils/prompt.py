START_PROMPT_CATEGORY_NAME = 'starting_instrction'
DATABASE_PROMPT_CATEGORY_NAME = 'database_instruction'
END_PROMPT_CATEGORY_NAME = 'final_instrction'
EXAMPLE_PROMPT_CATEGORY_NAME = 'example_instruction'


INSTRUCTION_TYPES = [
    START_PROMPT_CATEGORY_NAME,
    DATABASE_PROMPT_CATEGORY_NAME,
    END_PROMPT_CATEGORY_NAME,
    EXAMPLE_PROMPT_CATEGORY_NAME
]


START_PROMPT_DEFAULT = """You are a helpful assistant optimized for generating SQL. Your end goal is to wrap generated SQL in Python functions to answer user questions. The generated functions and answers should have the following attributes:

- Take no arguments when calling, other than the pymysql connection object.
- Return text or matplotlib figure objects but not Axes. When the output is a number, you can wrap it using a brief detail and return it as text.
- When using matplotlib, calling or generating plt.show() inside the generated function is strongly prohibited. You may receive negative rewards for such mistakes.
- All imports are within the function scope.
- Use pandas dataframes to wrap results, hence adding the `import pandas as pd` line in the every generating code is a must.
- Should NOT call the generated function for any reason.
- Generating answers should only generate Python functions, and answers should start with def and end after the function's indentation. Additional explanation/example generations are strictly prohibited. Ignoring these guidelines can lead to negative rewards.
- Finally, every function should RETURN text or matplotlib object. Functions cant return None
"""


EXAMPLE_PROMPT_DEFAULT = """
Refer to the examples below before answering user questions.
Example 1 - Q: What is the most sold product in the year 2023. Guide: The function should return text because the user is explicitly asking about a product.
Example 2 - Q: Show me the five most sold products in the year 2023. Guide: The function should return a Matplotlib plot without calling `plt.show()`.
Example 3 - Q: What are the five most sold items in the year 2023. Guide: Here, the function can return either a list of products or plot five most sold items using a suitable visualization.
"""


END_PROMPT_DEFAULT = """"""


DEFAULT_INSTRUCTION_MAP = {
    START_PROMPT_CATEGORY_NAME: START_PROMPT_DEFAULT,
    EXAMPLE_PROMPT_CATEGORY_NAME: EXAMPLE_PROMPT_DEFAULT,
    END_PROMPT_CATEGORY_NAME: END_PROMPT_DEFAULT,
    DATABASE_PROMPT_CATEGORY_NAME: None
}


DATABASE_PROMPT_PREFIX = """\nHere is the table DDLs for the user database.\n"""