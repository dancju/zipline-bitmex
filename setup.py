from setuptools import setup

setup(
		name='zipline-bitmex',
		version='0.1.1',
		url='https://github.com/nerdDan/zipline_bitmex',
		license='GPL',
		author='Daniel Zhou',
		author_email='danichau93@gmail.com',
		description='BitMEX bundle for Zipline',
		long_description=open('README.rst').read(),
		install_requires=['requests', 'zipline>=1.1.1'],
		packages=['zipline_bitmex'])
