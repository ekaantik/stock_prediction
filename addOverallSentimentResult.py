from datetime import datetime
import re
from tables import SymbolConfig, ModelDetails, SentimentResult, StockSentimentResults, SentimentString
from sqlalchemy import create_engine, and_ 
from sqlalchemy.orm import sessionmaker

# Set up database connection
engine = create_engine('postgresql://postgres:postgres@localhost:5432/analysis')
Session = sessionmaker(bind=engine)
session = Session()

# Get distinct stock IDs
stock_ids = [id for (id,) in session.query(SymbolConfig.id).distinct()]

# Get distinct model IDs
model_ids = [id for (id,) in session.query(ModelDetails.id).distinct()]

# Define threshold value
threshold = 0.7

# Define a regular expression pattern to match the "YYYY-MM-DD" format
date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')       

# Prompt the user to enter the start date and validate the input
while True:
    time_from_str = input("Enter the start date in YYYY-MM-DD format: ")
    if not date_pattern.match(time_from_str):
        print("Invalid date format. Please enter the date in the YYYY-MM-DD format.")
    else:
        try:
            time_from = datetime.strptime(time_from_str, '%Y-%m-%d')
            break
        except ValueError:
            print("Invalid date. Please enter a valid date in the YYYY-MM-DD format.")

# Prompt the user to enter the end date and validate the input
while True:
    time_to_str = input("Enter the end date in YYYY-MM-DD format: ")
    if not date_pattern.match(time_to_str):
        print("Invalid date format. Please enter the date in the YYYY-MM-DD format.")
    else:
        try:
            time_to = datetime.strptime(time_to_str, '%Y-%m-%d')
            if time_to <= time_from:
                print("End date must be after start date. Please enter a valid end date.")
            else:
                break
        except ValueError:
            print("Invalid date. Please enter a valid date in the YYYY-MM-DD format.")

# Check if the specified start and end dates already exist in the database
existing_start_date = session.query(SentimentString).filter(SentimentString.data_date == time_from).first()
existing_end_date = session.query(SentimentString).filter(SentimentString.data_date == time_to).first()

if existing_start_date is not None and existing_end_date is not None:
    print("Sentiment analysis for the specified start and end dates already exists in the database.")
else:
    # Perform sentiment analysis and store the results in the database
    for stock_id in stock_ids:
        for model_id in model_ids:
                # Check if there is already a record for this stock, model, time_from, and time_to
                existing_record = session.query(StockSentimentResults)\
                    .filter(and_(StockSentimentResults.stock_id == stock_id,
                                StockSentimentResults.model_id == model_id,
                                StockSentimentResults.time_from == time_from,
                                StockSentimentResults.time_to == time_to))\
                    .first()

                if existing_record:
                    # Update the existing record
                    overall_sentiment = existing_record.overall_sentiment
                    overall_score = existing_record.overall_score
                else:
                    # Get all sentiment results for the stock and model in the specified date range
                    sentiment_results = session.query(SentimentResult.sentiment_result, SentimentResult.sentiment_score)\
                        .join(SentimentString, SentimentString.tweet_id == SentimentResult.tweet_id)\
                        .join(SymbolConfig, SymbolConfig.id == SentimentString.symbol_config_id)\
                        .filter(and_(SymbolConfig.id == stock_id,
                                    SentimentResult.model_name_id == model_id,
                                    SentimentString.data_date >= time_from,
                                    SentimentString.data_date < time_to))\
                        .all()


                    # Calculate the counts for each sentiment result 
                    positive_count = 0
                    negative_count = 0
                    neutral_count = 0
                    for sentiment_result, sentiment_score in sentiment_results:
                        if sentiment_result == 'positive'  and sentiment_score >= threshold:
                            positive_count += 1
                        elif sentiment_result == 'negative' and sentiment_score >= threshold:
                            negative_count += 1
                        else:
                            neutral_count += 1

                    total_count = positive_count + negative_count + neutral_count
                    print(total_count, positive_count, negative_count, neutral_count)

                    # Determine the overall sentiment based on the counts
                    if total_count == 0:
                        overall_sentiment = 'neutral'
                        overall_score = 0.0
                    else:
                        if positive_count == max(positive_count, neutral_count, negative_count):
                            overall_sentiment = 'positive'
                            overall_score = positive_count / total_count
                        elif negative_count == max(positive_count, neutral_count, negative_count):
                            overall_sentiment = 'negative'
                            overall_score = negative_count / total_count
                        else:
                            overall_sentiment = 'neutral'
                            overall_score = neutral_count / total_count

                    # Check if there is an existing record for the same time range, stock and model
                    existing_record = session.query(StockSentimentResults)\
                        .filter(and_(StockSentimentResults.stock_id == stock_id,
                                    StockSentimentResults.model_id == model_id,
                                    StockSentimentResults.time_from == time_from,
                                    StockSentimentResults.time_to == time_to))\
                        .first()

                    if existing_record:
                        # Update existing record with new sentiment values
                        existing_record.overall_sentiment = overall_sentiment
                        existing_record.overall_score = overall_score
                    else:
                        # Create a new record in the stock_sentiment_results table
                        stock_sentiment_result = StockSentimentResults(
                            stock_id=stock_id,
                            model_id=model_id,
                            overall_sentiment=overall_sentiment,
                            overall_score=overall_score,
                            time_from=time_from,
                            time_to=time_to,
                        )
                        session.add(stock_sentiment_result)
session.commit()





# # Check if there is sentiment data for the specified date range
# if not session.query(SentimentString).filter(
#         and_(SentimentString.data_date >= time_from , SentimentString.data_date <= time_to)
#         ).count():
#     print("No sentiment data found for the specified date range.")
# else:
#     # Loop over each stock and model to calculate the sentiment
#     for stock_id in stock_ids:

#         for model_id in model_ids:
#             # Check if there is already a record for this stock, model, time_from, and time_to
#             existing_record = session.query(StockSentimentResults)\
#                 .filter(and_(StockSentimentResults.stock_id == stock_id,
#                             StockSentimentResults.model_id == model_id,
#                             StockSentimentResults.time_from == time_from,
#                             StockSentimentResults.time_to == time_to))\
#                 .first()

#             if existing_record:
#                 # Update the existing record
#                 overall_sentiment = existing_record.overall_sentiment
#                 overall_score = existing_record.overall_score
#             else:
#                 # Get all sentiment results for the stock and model in the specified date range
#                 sentiment_results = session.query(SentimentResult.sentiment_result, SentimentResult.sentiment_score)\
#                     .join(SentimentString, SentimentString.tweet_id == SentimentResult.tweet_id)\
#                     .join(SymbolConfig, SymbolConfig.id == SentimentResult.symbol_config_id)\
#                     .filter(and_(SymbolConfig.id == stock_id,
#                                 SentimentResult.model_name_id == model_id,
#                                 SentimentString.data_date >= time_from,
#                                 SentimentString.data_date < time_to))\
#                     .all()

#                 # Calculate the counts for each sentiment result
#                 positive_count = 0
#                 negative_count = 0
#                 neutral_count = 0
#                 for sentiment_result, sentiment_score in sentiment_results:
#                     if sentiment_result == 'positive'  and sentiment_score >= threshold:
#                         positive_count += 1
#                     elif sentiment_result == 'negative' and sentiment_score >= threshold:
#                         negative_count += 1
#                     else:
#                         neutral_count += 1

#                 total_count = positive_count + negative_count + neutral_count
#                 print(total_count, positive_count, negative_count, neutral_count)

#                 # Determine the overall sentiment based on the counts
#                 if total_count == 0:
#                     overall_sentiment = 'neutral'
#                     overall_score = 0.0
#                 else:
#                     if positive_count == max(positive_count, neutral_count, negative_count):
#                         overall_sentiment = 'positive'
#                         overall_score = positive_count / total_count
#                     elif negative_count == max(positive_count, neutral_count, negative_count):
#                         overall_sentiment = 'negative'
#                         overall_score = negative_count / total_count
#                     else:
#                         overall_sentiment = 'neutral'
#                         overall_score = neutral_count / total_count

#                 # Check if there is an existing record for the same time range, stock and model
#                 existing_record = session.query(StockSentimentResults)\
#                     .filter(and_(StockSentimentResults.stock_id == stock_id,
#                                 StockSentimentResults.model_id == model_id,
#                                 StockSentimentResults.time_from == time_from,
#                                 StockSentimentResults.time_to == time_to))\
#                     .first()

#                 if existing_record:
#                     # Update existing record with new sentiment values
#                     existing_record.overall_sentiment = overall_sentiment
#                     existing_record.overall_score = overall_score
#                 else:
#                     # Create a new record in the stock_sentiment_results table
#                     stock_sentiment_result = StockSentimentResults(
#                         stock_id=stock_id,
#                         model_id=model_id,
#                         overall_sentiment=overall_sentiment,
#                         overall_score=overall_score,
#                         time_from=time_from,
#                         time_to=time_to,
#                     )
#                     session.add(stock_sentiment_result)
# session.commit()
