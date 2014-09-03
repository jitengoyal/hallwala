from setuptools import setup

requires = [
'pyramid_chameleon', 
'pyramid',
]

setup(name='tutorial',
	entry_points="""\
	[paste.app_factory]
	main = tutorial:main
	""",
)
