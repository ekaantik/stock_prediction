import psycopg2
import requests
import json
from datetime import datetime

# Connect to the database
conn = psycopg2.connect(
    host="localhost",
    database="analysis",
    user="postgres",
    password="postgres"
)

# Retrieve the models from the model_details table
cur = conn.cursor()
cur.execute("SELECT id, model_name FROM model_details")
models = cur.fetchall()

# Loop through the models
for model in models:
    model_id = model[0]
    model_name = model[1]
    
    # Retrieve tweets from the sentiment_strings table
    cur.execute("SELECT symbol_config_id, tweet_id, strings FROM sentiment_strings")
    tweets = cur.fetchall()

    # Convert the rows to a list of dictionaries
    temp_dict = {row[1]: row[0] for row in tweets}
    tweet_dict = {row[1]:row[2] for row in tweets}


    # Make a POST request to the sentiment analysis API
    url = "http://127.0.0.1:5000/po"
    payload = json.dumps(tweet_dict)
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, data=payload, headers=headers)

    # Parse the JSON response and insert/update the data into the sentiment_results table
    if response.status_code == 200:
        sentiment_data = json.loads(response.content.decode('utf-8'))
        
        # Loop through the sentiment data for each tweet
        for tweet_id, result in sentiment_data.items():
            sentiment = result[0]
            sentiment_score = result[1]
            created_date = datetime.now()
            symbol_config_id = temp_dict[int(tweet_id)]

            # Check if a record already exists in the sentiment_results table for this model and tweet
            cur.execute("SELECT id FROM sentiment_results WHERE tweet_id = %s AND model_name_id = %s", (tweet_id, model_id))
            existing_record = cur.fetchone()
            
            if existing_record:
                # Update the existing record
                cur.execute("UPDATE sentiment_results SET sentiment_result = %s, sentiment_score = %s, created_date = %s, symbol_config_id = %s WHERE id = %s", (sentiment, sentiment_score, created_date, symbol_config_id))
            else:
                # Insert a new record
                cur.execute("INSERT INTO sentiment_results (tweet_id, model_name_id, sentiment_result, sentiment_score, created_date, symbol_config_id) VALUES (%s, %s, %s, %s, %s, %s)", (tweet_id, model_id, sentiment, sentiment_score, created_date, symbol_config_id))

        # Commit the changes for this model
        conn.commit()
    else:
        print(f"Error occurred: {response.status_code}")

# Close the database connection
cur.close()
conn.close()
