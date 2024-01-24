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

ARG COHERE_API_KEY
ENV COHERE_API_KEY=$COHERE_API_KEY
ARG SERP_API_KEY
ENV SERP_API_KEY=$SERP_API_KEY
ARG VERBOSITY
ENV VERBOSITY=$VERBOSITY
ARG GENERATE_MODEL
ENV GENERATE_MODEL=$GENERATE_MODEL

CMD [ "sh", "-c", "echo $COHERE_API_KEY; python rest_demo.py --cohere_api_key $COHERE_API_KEY --serp_api_key $SERP_API_KEY --verbosity $VERBOSITY --generate_model $GENERATE_MODEL" ]
#CMD [ "python", "./rest_demo.py", "--cohere_api_key", "$COHERE_API_KEY", "--serp_api_key", "$SERP_API_KEY", "--verbosity", "$VERBOSITY", "--generate_model", "$GENERATE_MODEL" ]
