import ast
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "hello world"


@app.route("/po", methods=["POST"])
def process():
    pda = ast.literal_eval(request.data.decode("utf-8"))

    import models.nb_new as nb_new

    # pd.set_option('display.max_columns', None)

    temp_df = pd.DataFrame.from_dict(pda, orient='index', columns=['tweet'])
    temp_df.index.name = 'id'
    temp_df.reset_index(inplace=True)
    # print(temp_df)

    recv_df = nb_new.fuc(temp_df).drop(['Tweet', 'cleaned_tweets', 'negative', 'positive'], axis=1)
    # print(recv_df)

    recv_dict = dict(zip(recv_df['id'], zip(recv_df['sentiment'], recv_df['score'])))
    recv_dict = {k: tuple(v) for k, v in recv_dict.items()}
    # print(recv_dict)
    return jsonify(recv_dict)


@app.route("/health")
def health_check():
    return jsonify({
        "status": "ok",
        "name": "bert app",
        "version": "1.0.0",
    })


if __name__ == "__main__":
    app.run()
