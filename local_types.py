from data_utilities import iter_lines_with_content
from pathlib import Path
from queue import Queue
from types import ModuleType
from threading import Thread, Event
from dataclasses import dataclass, field
from local_interfaces import location_interface, application_interface

#TODO - implement all mutability functions and not just add - also make sure we can't mix types unless related
class generic_set(set):
	def set_by_lines(self, text):
		self.clear()
		for line in iter_lines_with_content(text):
			self.add(line)

class path_ancestor_set(generic_set):
	def add(self, item):
		new = Path(item)
		super().add(new)
		return new

class path_parts_set(generic_set):
	def add(self, item):
		new = Path(item).parts
		super().add(new)
		return new

class locations_set(generic_set):
	def add(self, item):
		new = location(Path(item))
		super().add(new)
		return new

@dataclass
class location(location_interface):
	#Member						Type				Field info
	#------						----				----------
	path:					Path = 					field()
	disallow_ancestors: 	path_ancestor_set = 	field(default_factory=path_ancestor_set, init=False)
	disallow_parts: 		path_parts_set = 		field(default_factory=path_parts_set, init=False)

	def __hash__(self):
		return hash(self.path)


@dataclass
class application_type(application_interface):
	#Member						Type				Field info
	#------						----				----------
	settings:					ModuleType = 		field()

	pending_operations:			Queue = 			field(default_factory=Queue, init=False)
	worker_thread:				Thread = 			field(default=None, init=False)

	application_ready:			Event = 			field(default_factory=Event, init=False)
	worker_loop_terminated:		Event = 			field(default_factory=Event, init=False)
