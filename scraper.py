from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import snscrape.modules.twitter as tw 
from tables import SymbolConfig, SentimentString

# create the engine
engine = create_engine('postgresql://postgres:postgres@localhost:5432/analysis')

# create a session factory
Session = sessionmaker(bind=engine)

# create a session
session = Session()

# create the base class for declarative models
Base = declarative_base()

# create the tables
Base.metadata.create_all(engine)

# Get all SymbolConfig objects
symbols = session.query(SymbolConfig).all()
print(symbols)

# prompt the user to enter the start and end dates
start_date_str = input("Enter the start date in YYYY-MM-DD format: ")
end_date_str = input("Enter the end date in YYYY-MM-DD format: ")

# convert the user input into datetime objects
start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

# Set the date range for tweets
since_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
until_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

for symbol in symbols:
    # Build query for snscrape library
    query = f"{symbol.name} lang:en since:{since_date.strftime('%Y-%m-%d')} until:{until_date.strftime('%Y-%m-%d')}"

    # Initialize tweet counter
    tweet_count = 0

    for tweet in tw.TwitterSearchScraper(query).get_items():
        # Check if maximum tweet count is reached for this symbol
        if tweet_count >= 500:
            break
        
        # Check if tweet is a retweet or reply
        if not tweet.inReplyToUser and not tweet.retweetedTweet:
            # Build sentiment string
            sentiment_string = f"{tweet.content}"
            # Check if sentiment string already exists in database
            existing_sentiment = session.query(SentimentString).filter_by(tweet_id=tweet.id).first()

            if existing_sentiment:
                # Update existing sentiment string
                existing_sentiment.updated_date = datetime.now()
            else:
                # Create new sentiment string with symbol config id
                sentiment = SentimentString(symbol_config_id=symbol.id, strings=sentiment_string, data_date=tweet.date, tweet_id=tweet.id)
                session.add(sentiment) # Add new sentiment string to session

            # Increment tweet counter
            tweet_count += 1

    print(f"Processed {tweet_count} tweets for {symbol.name}")

# commit the changes to the database
session.commit()

# close the session
session.close()