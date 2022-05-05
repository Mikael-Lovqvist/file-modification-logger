from pathlib import Path
import time

#TODO - track metadata changes

from collections import defaultdict
#NOTE - we must import configuration so that the module settings is updated with the settings we want
import configuration, settings
from local_types import application_type, dataclass, field
import hashlib

def sha256(data):
	return hashlib.sha256(data).digest()

@dataclass
class snapshot:
	#Member						Type				Field info
	#------						----				----------
	inode:						int = 				field()
	mtime:						float =				field()
	sha256:						bytes = 			field()
	data:						bytes = 			field()
	timestamp:					float =				field(default_factory=time.time, init=False)

	def resolve(self):
		return self

#NOTE - if the member snapshot specifies type snapshot, we get a recursion error. This seem to be some magic that dataclass is doing in a weird way.
@dataclass
class snapshot_reference:
	#Member						Type				Field info
	#------						----				----------
	snapshot:					object =			field()
	timestamp:					float =				field(default_factory=time.time, init=False)

	def resolve(self):
		return self.snapshot.resolve()


@dataclass
class snapshot_log:
	#Member						Type				Field info
	#------						----				----------
	path:						Path = 				field(default=None, init=False)
	snapshots:					list =				field(default_factory=list)

	def update(self, path):
		if self.path is None:
			self.path = path

		stat = path.stat()

		if stat.st_size > settings.max_size:
			print(f'File too big: {path}')
			return

		#TODO - bail if big

		if self.snapshots:
			last = self.snapshots[-1].resolve()

			if last.inode == stat.st_ino:
				if last.mtime == stat.st_mtime:
					print('No change!')
				else:
					data = path.read_bytes()
					s256 = sha256(data)

					#Check backlog to see if we have seen this version
					for back_index in range(min(settings.max_backlog_check, len(self.snapshots))):
						previous = self.snapshots[-(back_index+1)].resolve()

						if previous.sha256 == s256 and previous.data == data:
							if back_index == 0:		#No change was made
								return

							print(f'This version was seen before, {back_index + 1} versions ago.')
							self.append_reference(path, previous)
							break
					else:
						self.append_snapshot(path, snapshot(stat.st_ino, stat.st_mtime, s256, data))
			else:
				print('Radical change?')

		else:
			#print('New!', path)
			data = path.read_bytes()
			self.append_snapshot(path, snapshot(stat.st_ino, stat.st_mtime, sha256(data), data))

	def append_snapshot(self, path, entry):
		print(f'Added snapshot for {path}')
		self.snapshots.append(entry)

	def append_reference(self, path, entry):
		print(f'Reused snapshot for {path}')
		self.snapshots.append(snapshot_reference(entry))


@dataclass
class snapshot_database:
	#Member						Type				Field info
	#------						----				----------
	file_table:					dict = 				field(default_factory=lambda : defaultdict(snapshot_log))


db = snapshot_database()


class test_application(application_type):
	def on_update_file(self, path):
		self.catalog_file(path)

	def catalog_file(self, path):
		path = Path(path)	#convert type

		if path.is_file():
			db.file_table[path].update(path)


application = test_application(settings)
application.start()
