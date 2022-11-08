FROM python:3.10-slim

COPY requirements.txt .
RUN mkdir qa
RUN mkdir qa/prompt_data
COPY qa/prompt_data/get_contextual_search_query.prompt qa/prompt_data/.
COPY qa/prompt_data/get_sample_answer.prompt qa/prompt_data/.
COPY qa/answer.py qa/.
COPY qa/bot.py qa/.
COPY qa/model.py qa/.
COPY qa/search.py qa/.
COPY qa/util.py qa/.
COPY rest_demo.py .
  
RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "python", "./rest_demo.py", "--cohere_api_key", "TODO", "--serp_api_key", "TODO", "--verbosity", "2" ]
