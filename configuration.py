import settings

location = settings.locations.add('/home/devilholk/Projects')

location.disallow_ancestors.set_by_lines('''

	/home/devilholk/Projects/Affiliated
	/home/devilholk/Projects/bash
	/home/devilholk/Projects/zim-package
	/home/devilholk/Projects/vr-sand-mandela
	/home/devilholk/Projects/trashbin
	/home/devilholk/Projects/silabs-usbxpress
	/home/devilholk/Projects/security_research
	/home/devilholk/Projects/rpi3
	/home/devilholk/Projects/qt-examples
	/home/devilholk/Projects/fix-obs-bug
	/home/devilholk/Projects/ftdi_libmpsse
	/home/devilholk/Projects/github
	/home/devilholk/Projects/others
	/home/devilholk/Projects/openscad
	/home/devilholk/Projects/lmms
	/home/devilholk/Projects/ipxe
	/home/devilholk/Projects/libopencm3-examples
	/home/devilholk/Projects/js-node-editor/experiments/node_modules

''')

location.disallow_parts.set_by_lines('''

	linux/trunk
	trunk/src
	lib/libopencm3
	freetype-2.11.0
	experiments/harfbuzz-2.8.2
	.git
	.cache
	__pycache__

''')

settings.max_size = 16 << 20 		#16 MiB
settings.max_backlog_check = 10		#Max 10 versions back