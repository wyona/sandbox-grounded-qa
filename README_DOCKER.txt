python3 rest_demo.py --cohere_api_key J2qwX5TdARa15Ty9mhFHN8JdKfNl0HOfBW3lQeoO --serp_api_key 0cfeea5c866740f934f499d1cbf4fced689cc0661c5fc58a1d08113ffe470831 --verbosity 2

docker build -t cohere-grounded-qa .

docker run -p 5007:5007 -e COHERE_API_KEY=J2qwX5TdARa15Ty9mhFHN8JdKfNl0HOfBW3lQeoO -e SERP_API_KEY=0cfeea5c866740f934f499d1cbf4fced689cc0661c5fc58a1d08113ffe470831 -e GENERATE_MODEL=command cohere-grounded-qa

docker-compose up -d
docker-compose logs -f
docker-compose down

curl -k --request POST --url http://0.0.0.0:5007/api/v1/ask --header 'content-type: application/json' --data '{ "question":"What is the highest mountain of the world?" }'

curl -k --request POST --url http://0.0.0.0:5007/api/v1/ask --header 'content-type: application/json' --data '{ "question":"How does GraphQL work?","site-url":"https://weaviate.io" }'

curl -k --request POST --url https://grounded-qa.ukatie.com/api/v1/ask --header 'content-type: application/json' --data '{ "question":"How does GraphQL work?","site-url":"https://weaviate.io" }'
