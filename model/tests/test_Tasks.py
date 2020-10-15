# Import argument parsing
import argparse

# Import Celery-specific packages
from celery import chord
from celery import group
from celery import Celery

# Import multiprocessing lib to get num of CPU cores
import multiprocessing

# Import tasks to be distributes via Celery
from model.Tasks import add, monte_carlo, est_pi

# Celery client instructions:
# 0)  Add project root to PYTHONPATH (e.g., export PYTHONPATH=/home/gtamkin/innovation-lab:$PYTHONPATH)
# 1)  Modify default values in model.CeleryConfiguration.py (if necessary)
# 2)  Modify application source code:
# 3)  	Import Celery-specific packages
# 4)	Import tasks to be distributes via Celery
# 5)	Import ILProcessController from model.ILProcessController
# 6)    Invoke ILProcessController using 'with' (8 PEP 343: The 'with' statement clarifies code that previously would
# 	use try...finally blocks to ensure that clean-up code is executed)
# 7)    Invoke application-specific Celery-based business logic

# Import ILProcessController from model.ILProcessController
from model.ILProcessController import ILProcessController

# Set commandline arguments to be used in determining number of simulations
parser = argparse.ArgumentParser(description='Monte-Carlo Celery Chords use-case')
parser.add_argument('--sims', type=int, default=1000000,
					help='number(int) of simulations to run. Default = 1000000')
parser.add_argument('--workers', type=int, default=multiprocessing.cpu_count(),
					help='number(int) of workers to run simulation on. Default=10')
args = parser.parse_args()

# -----------------------------------------------------------------------------
def main():

	# Invoke ILProcessController using 'with' statement
	with ILProcessController() as processController:

		# Perform application-specific Celery-based business logic
		print("\nBegin application-specific business logic...")

		n_simulations = args.sims #Total number of simulations
		n_per_worker = int(args.sims / args.workers) #Number of simulations per worker 
		n = args.workers #Number of times to call MC sim i.e. number of workers
		print('\nNumber of workers: ', n)
		result = chord([monte_carlo.s(n_per_worker) for i in range(n)], est_pi.s())()

		# Consume output
		print ('\nResult:  model.Tasks.monte_carlo() (Estimation of pi): ', result.get())

		#Uncomment to run add use-case
		#Celery.GroupResult.wpi = group(add.s(i, i) for i in range(10))()
		#result = Celery.GroupResult.wpi.get()

		# Consume output
		#print ('\nResult:  model.Tasks.add(): ', result)

# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
		main()
		print("\nCompleted application-specific business logic.  Exiting...")


