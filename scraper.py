from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, BigInteger, Float
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm import declarative_base
import snscrape.modules.twitter as tw 
from sqlalchemy import Enum

# create the engine
engine = create_engine('postgresql://postgres:postgres@localhost:5432/analysis')

# create a session factory
Session = sessionmaker(bind=engine)

# create a session
session = Session()

# create the base class for declarative models
Base = declarative_base()

# define the symbol_config table
class SymbolConfig(Base):
    __tablename__ = 'symbol_config'
    id = Column(Integer, primary_key=True)
    type = Column(Enum('stock', 'crypto', 'commodity', name='type_enum'))   
    name = Column(String, unique=True) 
    symbol_name = Column(String)
    subtype = Column(String)
    created_date = Column(DateTime, default=datetime.now)
    updated_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    status = Column(Enum('enabled', 'disabled', name='status_enum'))
    sentiment_strings = relationship("SentimentString", backref="symbol_config")

# define the sentiment_strings table
class SentimentString(Base):
    __tablename__ = 'sentiment_strings'
    id = Column(Integer, primary_key=True)
    symbol_config_id = Column(Integer, ForeignKey('symbol_config.id'))
    tweet_id = Column(BigInteger, unique=True)
    strings = Column(String)
    data_date = Column(DateTime)
    created_date = Column(DateTime, default=datetime.now)
    updated_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# define the modeldetails table
class ModelDetails(Base):
    __tablename__ = 'model_details'
    id = Column(Integer, primary_key=True)
    model_name = Column(String)
    model_version = Column(String, default='1.0')

# define the sentiment_results table
class SentimentResult(Base):
    __tablename__ = 'sentiment_results'
    id = Column(Integer, primary_key=True)
    tweet_id = Column(BigInteger,primary_key=True)
    symbol_config_id = Column(Integer, ForeignKey('symbol_config.id'))
    sentiment_result = Column(String)
    sentiment_score = Column(Integer)
    model_name_id = Column(Integer, ForeignKey('model_details.id'))
    created_date = Column(DateTime, default=datetime.now)

# define the stock_sentiment_results table
class StockSentimentResults(Base):
    __tablename__ = 'stock_sentiment_results'
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('symbol_config.id'))
    final_result = Column(Float)
    time_from = Column(DateTime)
    time_to = Column(DateTime)
    created_date = Column(DateTime, default=datetime.now)

# create the tables
Base.metadata.create_all(engine)

# Get all SymbolConfig objects
symbols = session.query(SymbolConfig).all()
print(symbols)

# Set the date range for tweets
since_date = datetime(2023, 3, 23, 0, 0, 0)
until_date = datetime(2023, 3, 26, 0, 0, 0) 

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





