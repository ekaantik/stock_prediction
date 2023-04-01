from datetime import datetime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, Enum, Float
from sqlalchemy import create_engine

# create the base class for declarative models
Base = declarative_base()

# create the engine
engine = create_engine('postgresql://postgres:postgres@localhost:5432/analysis')

# define the symbol_config table
class SymbolConfig(Base):
    __tablename__ = 'symbol_config'
    id = Column(Integer, primary_key=True)
    type = Column(Enum('stock', 'crypto', 'commodity', name='type_enum'))
    name = Column(String)
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

# define the model_details table
class ModelDetails(Base):
    __tablename__ = 'model_details'
    id = Column(Integer, primary_key=True)
    model_name = Column(String)
    model_version = Column(String, default='1.0')

# define the sentiment_results table
class SentimentResult(Base):
    __tablename__= 'sentiment_results'
    id = Column(Integer, primary_key=True)
    tweet_id = Column(BigInteger,primary_key=True)
    symbol_config_id = Column(Integer, ForeignKey('symbol_config.id'))
    sentiment_result = Column(String)
    sentiment_score = Column(Integer)
    model_name_id = Column(Integer, ForeignKey('model_details.id'))
    created_date = Column(DateTime, default=datetime.now)
    symbol_config = relationship("SymbolConfig", backref="sentiment_results")

# define the stock_sentiment_results table
class StockSentimentResults(Base):
    __tablename__ = 'stock_sentiment_results'
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('symbol_config.id'))
    model_id = Column(Integer, ForeignKey('model_details.id'))
    overall_score = Column(Float)
    overall_sentiment = Column(String)
    time_from = Column(DateTime)
    time_to = Column(DateTime)
    created_date = Column(DateTime, default=datetime.now)


# define the word_frequency table
class WordFrequency(Base):
    __tablename__ = 'word_frequency'
    id = Column(Integer, primary_key=True)
    symbol_config_id = Column(Integer, ForeignKey('symbol_config.id'))
    word = Column(String)
    word_count = Column(Integer)
    time_from = Column(DateTime)
    time_to = Column(DateTime)
    created_date = Column(DateTime, default=datetime.now)

# create the tables
Base.metadata.create_all(engine)