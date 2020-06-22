from celery import group
from model.Tasks import add
from model.ILProcessController import ILProcessController
import sys

# -----------------------------------------------------------------------------
def main():

	with ILProcessController() as processController:
		try:
			wpi = group(add.s(i, i) for i in range(10))()
			result = wpi.get()
			print ('result.get() = ', result)
			wpi.forget()
		except Exception as inst:
			print(type(inst))  # the exception instance
			print(inst.args)  # arguments stored in .args
			print(inst)  # __str__ allows args to be printed directly,

# ------------------------------------------------------------------------------
# Invoke the main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
	try:
		sys.exit(main())
	except Exception as inst:
		print(type(inst))  # the exception instance
		print(inst.args)  # arguments stored in .args
		print(inst)  # __str__ allows args to be printed directly,


