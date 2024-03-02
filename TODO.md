commands:

celery -A core worker --loglevel=info

celery -A core beat -l info

celery --broker=${RABBITMQ_URL} flower --port=5555

redis-server

redis-server --port 6380

redis-cli ping
PONG