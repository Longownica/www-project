pip install poetry
docker run -d -p 27017:27017 --name test-mongo mongo:latest
pip install checkers
poetry install
