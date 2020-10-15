import time
import numpy.random as random
from model.CeleryConfiguration import app

# Task that adds incoming numbers and sleeps for 1 second - simulates short asynchronous tasks
@app.task
def add(x, y):
    time.sleep(1)
    return x + y

@app.task
def monte_carlo(n_simulations):
	""" This method simulates random (x,y) points in a 2-D
	plane with domain as a square of side 1 unit. We then
	calculate the ratio of numbered points that lied inside
	the circle and total number of generated points.

	We know that the area of the square is 1 sq unit while
	the area of a circle is: pi * (1/2)^2 = pi/4.
	With a large amount of generated points:
	(area of circle / area of square) = (total n of pts inside circle / total n of pts inside square)
	that is: pi = 4 * (no. of pts inside circle / no. of pts inside square)"""
	circle_points = 0
	square_points = 0

	for i in range(n_simulations):
		rx = random.uniform(-1, 1)
		ry = random.uniform(-1, 1)

		origin_distance = rx**2 + ry**2

		if origin_distance <= 1:
			circle_points += 1

		square_points += 1

	return circle_points, square_points


@app.task
def est_pi(results_list):
	""" Task which is designed to run after all
	monte_carlo tasks have been completed.
	Task takes the list resulting from the
	Celery chord and sums up the
	circle points and square points then divides
	the totals then multiplies by 4 to result in
	a rough estimation of pi"""
	circle_totals = 0
	square_totals = 0

	for (circle_points, square_points) in results_list:
		circle_totals += circle_points
		square_totals += square_points

	print("Circle totals =", circle_totals)
	print("Square totals =", square_totals)
	pi = 4 * (circle_totals / square_totals)
	print("Finals estimation of Pi =", pi)
	return pi

