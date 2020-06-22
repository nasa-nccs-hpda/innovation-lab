# Celery configuration file
BROKER_URL = 'redis://localhost:6380/0'
#BROKER_URL = 'redis://ec2-172-31-54-47.compute-1.amazonaws.com:6380/0'
# BROKER_URL = 'redis://ec2-34-224-16-79.compute-1.amazonaws.com:6380/0'
#BROKER_URL = 'redis://10.100.35.214:6379/0'
#BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis'

# Enable next line to explicitly register tasks by default
CELERY_IMPORTS = ("model.Tasks")
#CELERY_IMPORTS = ("tasks","model.tests.test_Tasks")
CELERY_ENABLE_UTC = False

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

#CELERY_TIMEZONE = 'America/Los_Angeles'
#CELERY_ENABLE_UTC = True

## Broker settings.
#app.conf.broker_url = 'redis://localhost:6379/0'
#broker_url = 'redis://guest@localhost:6379//'

# List of modules to import when the Celery worker starts.
#imports = ('myapp.tasks',)

## Using the database to store task state and results.
#result_backend = 'db+sqlite:///results.db'

#task_annotations = {'tasks.add': {'rate_limit': '10/s'}}

#BROKER_TRANSPORT = "redis"

#BROKER_HOST = "localhost"  # Maps to redis host.
#BROKER_PORT = 6379         # Maps to redis port.
#BROKER_VHOST = "0"         # Maps to database number.

#Results
#You probably also want to store results in Redis:

#CELERY_RESULT_BACKEND = "redis"
#CELERY_REDIS_HOST = "localhost"
#CELERY_REDIS_PORT = 6379
#CELERY_REDIS_DB = 0

