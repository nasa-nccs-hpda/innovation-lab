import time
from model.CeleryConfiguration import app

# Task that adds incoming numbers and sleeps for 1 second - simulates short asynchronous tasks
@app.task
def add(x, y):
    time.sleep(1)
    return x + y

