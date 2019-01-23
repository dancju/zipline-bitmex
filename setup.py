from setuptools import setup

setup(
    name='zipline-bitmex',
    version='0.1.2',
    url='https://github.com/nerdDan/zipline-bitmex',
    license='GPL',
    author='Daniel Zhou',
    author_email='danichau93@gmail.com',
    description='BitMEX bundle for Zipline',
    long_description=open('README.rst').read(),
    long_description_content_type="text/x-rst",
    packages=['zipline_bitmex'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
)
