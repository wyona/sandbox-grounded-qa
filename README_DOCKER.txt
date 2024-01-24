python3 rest_demo.py --cohere_api_key REPLACE_BY_COHERE_API_KEY --serp_api_key REPLACE_BY_SERP_API_KEY --verbosity 2

docker build -t cohere-grounded-qa .

docker run -p 5007:5007 -e COHERE_API_KEY=REPLACE_BY_COHERE_API_KEY -e SERP_API_KEY=REPLACE_BY_SERP_API_KEY -e GENERATE_MODEL=command cohere-grounded-qa

docker-compose up -d
docker-compose logs -f
docker-compose down

curl -k --request POST --url http://0.0.0.0:5007/api/v1/ask --header 'content-type: application/json' --data '{ "question":"What is the highest mountain of the world?" }'

curl -k --request POST --url http://0.0.0.0:5007/api/v1/ask --header 'content-type: application/json' --data '{ "question":"How does GraphQL work?","site-url":"https://weaviate.io" }'

curl -k --request POST --url https://grounded-qa.ukatie.com/api/v1/ask --header 'content-type: application/json' --data '{ "question":"How does GraphQL work?","site-url":"https://weaviate.io" }'
