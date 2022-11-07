import time
import logging
import os
import uuid

from flask import abort, Flask, jsonify, request

app = Flask(__name__)

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Get answer to question
# curl --request POST --url http://localhost:5007/api/v1/ask --header 'content-type: application/json' --data '{ "question":"What is the capital of Brazil?" }'
@app.route('/api/v1/ask', methods=['POST'])
def getAnswer():
    if not request.json or not 'question' in request.json:
        abort(400)
    question = request.json['question']
    logger.info(f"Get answer to question '{question}' ...")

    answer = "TODO_ANSWER"
    relevant_paragraph = "TODO_PARA"
    source = "TODO_SOURCE"

    response = {'answer': answer, 'relevant_paragraphs': relevant_paragraph, 'source': source}
    return jsonify(response), 200

# Health check endpoint
@app.route('/api/v1/health', methods=['GET'])
def checkHealth():
    logger.info("Check health ...")

    response = {'status':'UP'}
    return jsonify(response), 200
 
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5007)
