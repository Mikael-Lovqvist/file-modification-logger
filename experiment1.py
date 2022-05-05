import pyinotify
from pathlib import Path
import time


#from local_interfaces import generic_thread
#from queue import Queue

# class test(generic_thread):

# 	def pre_run(self):
# 		self.queue = Queue()

# 	def run(self, report_ready):
# 		print('this is the thread')
# 		report_ready()
# 		while True:
# 			if self.queue.get() == 'ABORT':
# 				return

# 	def post_run(self):
# 		del self.queue

# 	def abort(self):
# 		self.queue.put('ABORT')


# t = test()
# print('starting')
# t.start(True)
# print('Running')
# t.stop(True)






import configuration, settings

from local_types import application_type


application = application_type(settings)
print('Starting')
application.start(True)
print('Started')

while True:
	time.sleep(20)
print('Stopping')
application.stop(True)
print('Done')

# result= list()
# for location in settings.locations:
# 	for d in location.scan_directories():
# 		result.append(d)

# print(len(result))

exit()
