from datetime import datetime
from tables import SymbolConfig, ModelDetails, SentimentResult, StockSentimentResults
from sqlalchemy import create_engine
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

# Loop over each stock and model to calculate the sentiment
for stock_id in stock_ids:
    for model_id in model_ids:
        # Get all sentiment results for the stock and model
        sentiment_results = session.query(SentimentResult.sentiment_result, SentimentResult.sentiment_score)\
            .filter(SentimentResult.symbol_config_id == stock_id, SentimentResult.model_name_id == model_id)\
            .all()
        
        # Calculate the counts for each sentiment result
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        for sentiment_result, sentiment_score in sentiment_results:
            if sentiment_result == 'positive' and sentiment_score >= threshold:
                positive_count += 1
            elif sentiment_result == 'negative' and sentiment_score >= threshold:
                negative_count += 1
            else:
                neutral_count += 1

        total_count = positive_count+negative_count+neutral_count

        # Determine the overall sentiment based on the counts
        if positive_count == max(positive_count, neutral_count, negative_count):
            overall_sentiment = 'positive'
            overall_score = positive_count/total_count
        elif negative_count == max(positive_count, neutral_count, negative_count):
            overall_sentiment = 'negative'
            overall_score = negative_count/total_count
        else:
            overall_sentiment = 'neutral'
            overall_score = neutral_count/total_count

        # # Determine the overall sentiment based on the counts
        # if positive_count > negative_count and positive_count > neutral_count:
        #     overall_sentiment = 'positive'
        # elif negative_count > positive_count and negative_count > neutral_count:
        #     overall_sentiment = 'negative'
        # else:
        #     overall_sentiment = 'neutral'
        #
        # # Calculate the final result based on the overall sentiment and sentiment scores
        # sentiment_scores = [sentiment_score for sentiment_result, sentiment_score in sentiment_results]
        # if overall_sentiment == 'positive':
        #     final_result = sum(sentiment_scores) / len(sentiment_scores)
        # elif overall_sentiment == 'negative':
        #     final_result = -sum(sentiment_scores) / len(sentiment_scores)
        # else:
        #     final_result = 0.0
        
        # Create a new record in the stock_sentiment_results table
        stock_sentiment_result = StockSentimentResults(
            stock_id=stock_id,
            model_id = model_id,
            overall_sentiment = overall_sentiment,
            overall_score = overall_score,
            time_from=datetime(2023, 3, 20, 0, 0, 0),
            time_to=datetime(2023, 3, 30, 0, 0, 0),
        )
        session.add(stock_sentiment_result)
    
    session.commit()
session.commit()
