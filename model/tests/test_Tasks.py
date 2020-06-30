# Import Celery-specific packages
from celery import group
from celery import Celery

# Import tasks to be distributes via Celery
from model.Tasks import add

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

# -----------------------------------------------------------------------------
def main():

	# Invoke ILProcessController using 'with' statement
	with ILProcessController() as processController:

		# Perform application-specific Celery-based business logic
		print("\nBegin application-specific business logic...")

		Celery.GroupResult.wpi = group(add.s(i, i) for i in range(10))()
		result = Celery.GroupResult.wpi.get()

		# Consume output
		print ('\nResult:  model.Tasks.add(): ', result)

# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
		main()
		print("\nCompleted application-specific business logic.  Exiting...")


