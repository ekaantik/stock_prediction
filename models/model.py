import pandas as pd
from nltk.tokenize import word_tokenize
import re
import string
import pickle

# Load the pickled model from a file
with open('models/cvnew.pkl', 'rb') as f:
    cv = pickle.load(f)

# Load the pickled model from a file
with open('models/nbnew.pkl', 'rb') as f:
    nb = pickle.load(f)


def clean_text(sentence):
    sentence = sentence.lower()
    
    pattern = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    sentence = pattern.sub('', sentence)
    sentence = " ".join(filter(lambda x: x[0] != '@', sentence.split()))
    emo = re.compile("["
                           u"\U0001F600-\U0001FFFF"  
                           u"\U0001F300-\U0001F5FF"  
                           u"\U0001F680-\U0001F6FF"  
                           u"\U0001F1E0-\U0001F1FF" 
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE
                     )
    sentence = emo.sub(r'', sentence)
    sentence = sentence.lower()
    sentence = re.sub(r"[,.\"\'!@$%^&*(){}?/;`~:<>+=-]", "", sentence)
    tokens = word_tokenize(sentence)
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in tokens]
    words = [word for word in stripped if word.isalpha()]
    return " ".join(words)


def fuc(df):
    odf = pd.DataFrame()
    odf['Tweet'] = df['tweet']
    odf['id'] = df['id']
    odf['cleaned_tweets'] = odf['Tweet'].apply(lambda x: clean_text(x))
    live_input = cv.transform(odf['cleaned_tweets'].values.astype('U'))
    live_predictions = nb.predict(live_input)
    live_confidence = nb.predict_proba(live_input)
    class_map_rev = {0: "negative", 1: "positive", 4: "positive"}
    odf["sentiment"] = [class_map_rev[x] for x in live_predictions]
    cdf = pd.DataFrame(live_confidence)
    cdf.rename(columns=class_map_rev, inplace=True)
    fdf = pd.concat([odf,cdf], axis=1)
    fdf['score'] = [max(a,b) for a,b in zip(fdf['negative'],fdf['positive'])]
    return fdf


print("import ok")

# print(odf['sentiment'].value_counts())
