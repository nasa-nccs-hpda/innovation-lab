from celery import Celery
import time

from model.ILProcessController import ILProcessController

#app = Celery('model.tests.test_Tasks',
#			 broker='redis://ec2-172-31-54-47.compute-1.amazonaws.com:6380/0',
#			 backend='redis://ec2-172-31-54-47.compute-1.amazonaws.com:6380/0')
app = Celery('model.Tasks',  # TODO - replace hard-coded path with user-supplied path
			 broker='redis://localhost:6380/0',
			 backend='redis://localhost:6380/0')

@app.task
def add(x, y):
    time.sleep(1)
    return x + y

