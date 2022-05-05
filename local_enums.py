from enum import Enum, auto

class THREAD_STATE(Enum):
	IDLE = auto()
	STARTING = auto()
	STARTED = auto()
	STOPPING = auto()
	STOPPED = auto()