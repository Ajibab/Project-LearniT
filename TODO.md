commands:

celery -A core worker --loglevel=info

celery -A core beat -l info

celery --broker=amqps://wldzngjp:6UpIo4qyc-1VxK_t7sH0Voy-prubEwqc@hawk.rmq.cloudamqp.com/wldzngjp flower --port=5555

redis-server

redis-server --port 6380

redis-cli ping
PONG