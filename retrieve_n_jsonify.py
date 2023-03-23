import psycopg2
import requests
import json

# Connect to the database
conn = psycopg2.connect(
    host="localhost",
    database="analysis",
    user="postgres",
    password="postgres"
)

# Retrieve tweets from the table
cur = conn.cursor()
cur.execute("SELECT tweet_id, strings FROM sentiment_strings")
rows = cur.fetchall()

# Convert the rows to a dictionary
json_dict = {row[0]: row[1] for row in rows}

# Close the database connection
conn.close()

url = "http://127.0.0.1:5000/sentiment"

payload = json.dumps(json_dict)
headers = {"Content-Type": "application/json"}
response = requests.request("POST", url, data=payload.encode('utf-8'), headers=headers)

# Parse the JSON response and insert the data into the sentiment_results table
if response.status_code == 200:
    sentiment_data = response.json()
    conn = psycopg2.connect(
        host="localhost",
        database="analysis",
        user="postgres",
        password="postgres"
    )

    # Parse the JSON response and insert the data into the sentiment_results table
    for item in sentiment_data:
        tweet_id = item['tweet_id']
        sentiment = item
        cur.execute("INSERT INTO sentiment_results (tweet_id, sentiment_string_id, sentiment_result, sentiment_score, model_name_id, created_date) VALUES (%s, %s, %s, %s, %s, NOW())", (tweet_id, sentiment.get('id'), sentiment.get('result'), sentiment.get('score'), sentiment.get('model_name_id')))
    conn.commit()
    conn.close()
else:
    print(f"Error occurred: {response.status_code}")


# import psycopg2
# import requests

# # Connect to the database
# conn = psycopg2.connect(
#     host="localhost",
#     database="analysis",
#     user="postgres",
#     password="postgres"
# )

# # Retrieve tweets from the table
# cur = conn.cursor()
# cur.execute("SELECT tweet_id, strings FROM sentiment_strings")
# rows = cur.fetchall()

# # Convert the rows to a list of dictionaries
# json_dict = {row[0]: row[1] for row in rows}

# # Close the database connection
# conn.close()

# url = "http://127.0.0.1:5000/po"

# payload = str(json_dict).encode('utf-8')
# headers = {"Content-Type": "application/json"}
# response = requests.request("POST", url, data=payload, headers=headers)
# print(response.text)

# # Commit the changes and close the database connection
# conn.close()
