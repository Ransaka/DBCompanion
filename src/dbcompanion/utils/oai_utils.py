import random
import os
import openai

DUMMY_RESPONSE_TEXT = '''def most_productive_year(connection):
    import pandas as pd
    import matplotlib.pyplot as plt

    # Query to get the total score for each year
    query = """
    SELECT YEAR(date) AS year, SUM(score) AS total_score
    FROM eprods
    GROUP BY year
    ORDER BY total_score DESC
    LIMIT 1;
    """

    # Execute the query and fetch the result into a DataFrame
    result_df = pd.read_sql(query, connection)

    # Check if there are results
    if not result_df.empty:
        most_productive_year = result_df.iloc[0]['year']
        total_score = result_df.iloc[0]['total_score']

        # Return the result as text
        return f"The most productive year so far is {most_productive_year} with a total score of {total_score}."
    else:
        return "No data available."

# Example usage:
# connection = pymysql.connect(host='your_host', user='your_user', password='your_password', database='your_database')
# result_text = most_productive_year(connection)
# print(result_text)
'''

DUMMY_RESPONSE_PLOT = '''
def most_productive_months_2023(connection):
    import pandas as pd
    import matplotlib.pyplot as plt
    import pymysql

    # SQL query to get the sum of scores for each month in 2023
    query = """
    SELECT DATE_FORMAT(date, '%Y-%m') AS month_year, SUM(score) AS total_score
    FROM eprods
    WHERE YEAR(date) = 2023
    GROUP BY month_year
    ORDER BY total_score DESC
    LIMIT 5;
    """

    # Execute the query and fetch the results into a pandas DataFrame
    result_df = pd.read_sql(query, connection)

    # Plot the bar chart for the top 5 most productive months
    plt.bar(result_df['month_year'], result_df['total_score'])
    plt.xlabel('Month-Year')
    plt.ylabel('Total Score')
    plt.title('Top 5 Most Productive Months in 2023')
    plt.xticks(rotation=45)
    plt.tight_layout()

# Example usage:
# connection = pymysql.connect(host='your_host', user='your_user', password='your_password', database='your_database')
# most_productive_months_2023(connection)
'''
DUMMY_RESPONSE_PLOT_2 = '''
def productivity_score_trend(connection):
    import matplotlib.pyplot as plt
    import pandas as pd

    query = """
    SELECT `date`, `score`
    FROM eprods
    WHERE YEAR(`date`) = 2023
    """

    df = pd.read_sql(query, connection)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['score'])
    plt.xlabel('Date')
    plt.ylabel('Productivity Score')
    plt.title('Productivity Score Trend in Year 2023')

    return plt'''


def detect_openai_api_key():
    API_KEY = os.environ.get("OPEN_AI_API_KEY", None)
    if API_KEY:
        return API_KEY
    else:
        raise ValueError(
            "Coundn't find open ai API key in environment, try setting it manually when intializing report")


def get_llm_response(system_prompt, quer, type='plot'):
    type = random.choice(['plot', 'text'])
    if type == 'plot':
        return random.choice([DUMMY_RESPONSE_PLOT_2, DUMMY_RESPONSE_PLOT])
    else:
        return DUMMY_RESPONSE_TEXT


# from openai import OpenAI
# client = OpenAI()

# response =

def get_gpt_response(
        client: openai.Client,
        system_prompt: str,
        user_prompt: str
):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=1,
        max_tokens=448,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content
