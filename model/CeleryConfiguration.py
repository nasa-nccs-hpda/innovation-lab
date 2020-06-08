# -*- coding: utf-8 -*-

# ---
# /etc/redis/redis.conf
# /var/log/redis/redis-server.log
# /var/lib/redis (working directory)
#
# In terminal 1:
#     docker run -it -v /Users/rlgill/Desktop/Source/innovation-lab:/home/ilUser/hostFiles -v /Users/rlgill/Desktop/SystemTesting:/home/ilUser/SystemTesting innovation-lab:1.0
#     redis-server&
#     cd ~/hostFiles
#     celery -A model.CeleryConfiguration worker --loglevel=info
#
# In terminal 2:
#     docker ps
#     docker exec -it [container ID] bash
#     cd ~/hostFiles
#     export PYTHONPATH=`pwd`
#     ???
#     check terminal 1
#
# In terminal 3, for debugging:
#     docker ps
#     docker exec -it [container ID] bash
#     check terminal 1 for debugger port
#     telnet localhost [port]
#
# To run Flower:
# celery flower -A model.CeleryConfiguration -port 5555
# ---

from celery import Celery


# app = Celery('innovation-lab',
#              backend='redis://localhost:6379/0',
#              broker='redis://localhost:6379/0',
#              track_started=True,
#              include=['model.MaxEntRequestCelery',
#         'projects.aviris_regression_algorithms.model.ApplyAlgorithmCelery'])

app = Celery('innovation-lab',
             backend='redis://localhost:6379/0',
             broker='redis://localhost:6379/0',
             track_started=True,
             include=['projects.aviris_regression_algorithms.model.ApplyAlgorithmCelery'])

app.conf.accept_content = ['application/json',
                           'json',
                           'pickle',
                           'application/x-python-serialize']
