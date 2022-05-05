from data_utilities import sequence_contains_sequence
from collections import deque
from local_exceptions import ApplicationStateException
from workers import fs_monitor, file_scanner



#TODO - decide how to deal with symlinks


class location_interface:
	def check_dir(self, path):
		if not path.is_dir():
			return False

		for check in self.disallow_ancestors:
			if path.is_relative_to(check):
				return False

		for check in self.disallow_parts:
			if sequence_contains_sequence(path.parts, check):
				return False

		return True

	#deprecated - we scan in the filescanner
	def scan_directories(self, abort_condition=None):
		to_check = deque((self.path,))

		while to_check:
			if abort_condition and abort_condition():
				return

			path = to_check.popleft()
			yield path
			for sub_directory in path.iterdir():
				if self.check_dir(sub_directory):
					to_check.append(sub_directory)



class application_interface:

	def start(self, synchronously=True):
		self.fs_monitor = fs_monitor()
		self.fs_monitor.application = self

		self.file_scanner = file_scanner()
		self.file_scanner.application = self

		self.fs_monitor.start(synchronously)
		self.file_scanner.start(synchronously)

	def stop(self, synchronously=True):
		self.fs_monitor.stop(synchronously)
		self.file_scanner.stop(synchronously)

	def on_new_directory(self, path):
		print(f'New directory: {path}')

	def on_new_file(self, path):
		print(f'New file: {path}')

	def on_delete_directory(self, path):
		print(f'Delete directory: {path}')

	def on_delete_file(self, path):
		print(f'Delete file: {path}')

	def on_move_directory(self, from_path, to_path):
		print(f'Move directory from {from_path} to {to_path}')

	def on_move_file(self, from_path, to_path):
		print(f'Move file from {from_path} to {to_path}')

	def on_update_file(self, path):
		print(f'Update file {path}')

	def watch_directory(self, path):
		self.fs_monitor.watch_directory(str(path))

