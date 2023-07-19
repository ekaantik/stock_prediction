from datetime import datetime
from tables import SymbolConfig, SentimentResult, SentimentString, WordFrequency
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string, re 

# Set up database connection
engine = create_engine('postgresql://postgres:postgres@localhost:5432/analysis')
Session = sessionmaker(bind=engine)
session = Session()

# Get distinct stock IDs
stock_ids = [id for (id,) in session.query(SymbolConfig.id).distinct()]

time_from = datetime(2023, 3, 14, 0, 0, 0)
time_to = datetime(2023, 3, 20, 0, 0, 0)
relevant_keywords = ['stock', 'market', 'trading', 'investing', 'investor', 'finance', 'economy', 'shares', 'prices', 'analysis', 'growth','increase','decrease','highest','lowest','buy','sell','bear','bull',]

# Define stopwords and punctuation
stop_words = set(stopwords.words('english'))
punctuations = set(string.punctuation)

# Define preprocess_text function
def preprocess_text(text):
    # Remove URLs and mentions
    text = re.sub(r'https?:\/\/\S+', '', text)
    text = re.sub(r'@\S+', '', text)

    # Tokenize the text
    tokens = word_tokenize(text)

    # Remove stopwords, punctuation, and symbols
    tokens = [token.lower() for token in tokens if token.lower() in relevant_keywords]

    # Join the remaining tokens to form a single string
    preprocessed_text = ' '.join(tokens)

    return preprocessed_text

# Loop over each stock to calculate the sentiment
for stock_id in stock_ids:
    # Get all sentiment results for the stock in the specified date range
    sentiment_results = session.query(SentimentString.strings)\
        .join(SentimentResult, SentimentResult.tweet_id == SentimentString.tweet_id)\
        .join(SymbolConfig, SymbolConfig.id == SentimentResult.symbol_config_id)\
        .filter(and_(SymbolConfig.id == stock_id,
                     SentimentString.data_date >= time_from,
                     SentimentString.data_date < time_to))\
        .all()

    # Tokenize and preprocess the tweets
    words = []
    for (tweet,) in sentiment_results:
        # Preprocess the tweet
        preprocessed_tweet = preprocess_text(tweet)

        # Tokenize the preprocessed tweet
        tokens = word_tokenize(preprocessed_tweet)

        # Add the remaining tokens to the list of words
        words.extend(tokens)

    # Calculate the frequency of the most used words
    word_freq = {}
    for word in words:
        if word in word_freq:
            word_freq[word] += 1
        else:
            word_freq[word] = 1

    # Sort the words by frequency and print the top 10
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    top_words = sorted_words[:10]
    # print(top_words)

    # Create a new record in the WordFrequency table for each of the top 10 words, if it doesn't already exist
    for word, freq in top_words:
        # Check if the word already exists for the stock and time range
        existing_word = session.query(WordFrequency).filter_by(symbol_config_id=stock_id, word=word, time_from=time_from, time_to=time_to).first()
        if existing_word:
            # If the word already exists, update its frequency count
            existing_word.word_count += freq
        else:
            # If the word doesn't exist, create a new record for it
            word_frequency = WordFrequency(
                symbol_config_id=stock_id,
                word=word,
                word_count=freq,
                time_from=time_from,
                time_to=time_to,
            )
            session.add(word_frequency)
session.commit()