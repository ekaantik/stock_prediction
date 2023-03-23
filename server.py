# import os
# import logging
# import sys
#
# import joblib
import ast
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

# configure logging
# log-level used on gunicorn CLI sets level only for the error logs, not for access logs
# use that level for both the flask app logger and access logs
# if __name__ != '__main__':
#     gunicorn_error_logger = logging.getLogger('gunicorn.error')
#     app.logger.handlers = gunicorn_error_logger.handlers
#     app.logger.setLevel(gunicorn_error_logger.level)
#     gunicorn_access_logger = logging.getLogger('gunicorn.access')
#     gunicorn_access_logger.setLevel(gunicorn_error_logger.level)

# Parse config
# config = load_config()

# Load serialized model instance
# setattr(sys.modules["__main__"], "GuardinexModel", GuardinexModel)
# model = joblib.load(config.modelpath)


@app.route("/")
def home():
    return "hello world"


@app.route("/po", methods=["POST"])
def process():
    pda = ast.literal_eval(request.data.decode("utf-8"))

    import nb_new

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
