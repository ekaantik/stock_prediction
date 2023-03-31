from datetime import datetime
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

time_from = datetime(2023, 3, 14, 0, 0, 0)
time_to = datetime(2023, 3, 20, 0, 0, 0)

# Loop over each stock and model to calculate the sentiment
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
                .join(SymbolConfig, SymbolConfig.id == SentimentResult.symbol_config_id)\
                .filter(and_(SymbolConfig.id == stock_id,
                             SentimentResult.model_name_id == model_id,
                             SentimentString.data_date >= time_from,
                             SentimentString.data_date < time_to,
                             SentimentResult.sentiment_score >= threshold))\
                .all()

            # Calculate the counts for each sentiment result
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            for sentiment_result, sentiment_score in sentiment_results:
                if sentiment_result == 'positive':
                    positive_count += 1
                elif sentiment_result == 'negative':
                    negative_count += 1
                else:
                    neutral_count += 1

            total_count = positive_count + negative_count + neutral_count

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