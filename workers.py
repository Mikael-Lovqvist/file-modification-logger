from threading import Thread, Lock, Event
from local_enums import THREAD_STATE
from local_datums import SENTINEL
from local_exceptions import InternalError
from queue import Queue
import pyinotify, os

class generic_thread(Thread):
	def __init__(self):
		self.state_lock = Lock()
		self.state = THREAD_STATE.IDLE
		self.is_ready = Event()
		super().__init__()

	def __init_subclass__(cls):
		cls._inner_run = cls.run
		cls.run = generic_thread._run_wrapper

	def _report_ready(self):
		with self.state_lock:
			assert self.state is THREAD_STATE.STARTING
			self.state = THREAD_STATE.STARTED
		self.is_ready.set()

	def _run_wrapper(self):
		self.pre_run()
		self._inner_run(self._report_ready)
		self.post_run()

		with self.state_lock:
			self.state = THREAD_STATE.STOPPED

	def start(self, synchronously=False):
		with self.state_lock:
			assert self.state is THREAD_STATE.IDLE

			self.state = THREAD_STATE.STARTING
			super().start()

		if synchronously:
			self.is_ready.wait()

	def stop(self, synchronously=False):
		self.abort()
		if synchronously:
			self.join()


class fs_monitor(generic_thread):

	#NOTE - the documentation for pyinotify states that paths ideally should not be unicode objects but it won't work sending in bytes-objects

	def pre_run(self):
		self.notify_flags = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_MOVED_TO | pyinotify.IN_MOVED_FROM | pyinotify.IN_CREATE | pyinotify.IN_DELETE | pyinotify.IN_DELETE_SELF | pyinotify.IN_MOVE_SELF
		self.pending_move_by_cookie = dict()

		self.watches = dict()
		self.watch_manager = pyinotify.WatchManager()
		#NOTE - we use a timeout here because otherwise we get stuck polling the inotify FD.
		#		In order to not do it like this we would have to make a custom Notifier that can be awakened both by the FD and by some other means
		self.notifier = pyinotify.Notifier(self.watch_manager, timeout=500)
		self.should_abort = Event()


	def process_event(self, event):
		#The sentinel will not have the name set
		if not event.name:
			return

		if event.mask & pyinotify.IN_CREATE:
			if event.mask & pyinotify.IN_ISDIR:
				self.application.on_new_directory(event.pathname)
			else:
				self.application.on_new_file(event.pathname)

		elif event.mask & pyinotify.IN_DELETE:
			if event.mask & pyinotify.IN_ISDIR:
				self.application.on_delete_directory(event.pathname)
			else:
				self.application.on_delete_file(event.pathname)

		elif event.mask & pyinotify.IN_MOVED_FROM:
			self.pending_move_by_cookie[event.cookie] = event.pathname

		elif event.mask & pyinotify.IN_MOVED_TO:
			if event.mask & pyinotify.IN_ISDIR:
				self.application.on_move_directory(self.pending_move_by_cookie.pop(event.cookie), event.pathname)
			else:
				self.application.on_move_file(self.pending_move_by_cookie.pop(event.cookie), event.pathname)

		elif event.mask & pyinotify.IN_CLOSE_WRITE:
			self.application.on_update_file(event.pathname)
		else:
			raise InternalError('Invalid event')

	def watch_directory(self, path):
		#TODO - we should make sure watches returns valid file descriptors and warn or bail if not

		#Make sure we are ready to watch files
		self.is_ready.wait()

		watches = self.watch_manager.add_watch(str(path), self.notify_flags, proc_fun=self.process_event)
		self.watches.update(watches)

	def run(self, report_ready):

		report_ready()
		def check_abort(n):
			return self.should_abort.is_set()
		self.notifier.loop(check_abort)

	def post_run(self):
		pass

	def abort(self):
		self.should_abort.set()
		#Add a sentinel to the queue
		self.notifier.append_event(pyinotify._RawEvent(next(iter(self.watches.values())), pyinotify.IN_CLOSE_WRITE, 0, ''))






class file_scanner(generic_thread):

	def pre_run(self):
		self.scan_queue = Queue()
		self.should_abort = Event()


	def run(self, report_ready):

		#Initialize initial scan
		for location in self.application.settings.locations:
			self.index_directory(location, location.path)

		report_ready()

		while not self.should_abort.is_set():
			pending_operation = self.scan_queue.get()

			if pending_operation is SENTINEL:
				return

			location, path = pending_operation

			for entry in path.iterdir():
				self.application.catalog_file(entry)

				if location.check_dir(entry):
					self.application.watch_directory(entry)
					self.index_directory(location, entry)



	def index_directory(self, location, path):
		self.scan_queue.put((location, path))

	def post_run(self):
		pass

	def abort(self):
		self.should_abort.set()

