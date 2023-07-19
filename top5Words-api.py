from flask import Flask, jsonify
from flask_caching import Cache
from datetime import datetime
from tables import WordFrequency
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set up database connection
engine = create_engine('postgresql://postgres:postgres@localhost:5432/analysis')
Session = sessionmaker(bind=engine)
session = Session()

# Set up Flask app and cache
app = Flask(__name__)
app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)

# Define function to get top 5 words from database for a given stock and time range
def get_top_5_words(stock_id, time_from, time_to):
    # Check cache first
    cache_key = f'{stock_id}_{time_from}_{time_to}'
    top_words = cache.get(cache_key)
    if top_words:
        return top_words

    # Get top 5 words from database
    word_freqs = session.query(WordFrequency)\
        .filter_by(symbol_config_id=stock_id, time_from=time_from, time_to=time_to)\
        .order_by(WordFrequency.word_count.desc())\
        .limit(5)\
        .all()

    top_words = [(word_freq.word, word_freq.word_count) for word_freq in word_freqs]
    
    # Set cache for 5 minutes
    cache.set(cache_key, top_words, timeout=300)

    return top_words

# Define endpoint to get top 5 words for a given stock and time range
@app.route('/top_words/<int:stock_id>/<string:time_from>/<string:time_to>')
def top_5_words(stock_id, time_from, time_to):
    time_from = datetime.strptime(time_from, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
    time_to = datetime.strptime(time_to, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
    top_words = get_top_5_words(stock_id, time_from, time_to)
    return jsonify({'top_words': top_words})

if __name__ == '__main__':
    app.run()
