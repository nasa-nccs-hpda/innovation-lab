from celery import group
from celery import Celery
from celery import result
from redis import exceptions
from model.Tasks import add
from model.ILProcessController import ILProcessController
from contextlib import suppress

# -----------------------------------------------------------------------------
def main():

	with ILProcessController() as processController:
		try:
			Celery.GroupResult.wpi = group(add.s(i, i) for i in range(10))()
			result = Celery.GroupResult.wpi.get()
			print ('result.get() = ', result)
#			result.delete()
			Celery.GroupResult.wpi.forget()
#			del result
#			del processController
#			wpi.forget()
#			wpi.backend.remove_pending_result(wpi)
#			del wpi
			Celery.GroupResult.wpi.delete()
#			print ('wpi.get() = ', wpi.get)
#			sys.exit(0)
		except exceptions.ConnectionError as inst:
			print("Connection Error ignore")
		except Exception as inst:
			print(type(inst))  # the exception instance
			print(inst.args)  # arguments stored in .args
			print(inst)  # __str__ allows args to be printed directly,

		finally:
#			del processController
			print ("leaving..")
# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
#	try:
		main()
		print("adsf")
#		print("adsf2")
#	except exceptions.ConnectionError as inst:
#		print("Connection Error ignore")
#	except Exception as inst:
#		print(type(inst))  # the exception instance
#		print(inst.args)  # arguments stored in .args
#		print(inst)  # __str__ allows args to be printed directly,


