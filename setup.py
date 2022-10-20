#!/usr/bin/env python3
from setuptools import setup

setup(name="ghidra_wrap",
	version='0.0.1',
	description="Python Wrapper for Ghidra headless",
	author="Luca Borzacchiello",
	author_email="lucaborza@gmail.com",
	url="https://github.com/borzacchiello/ghidra_wrapper",
	packages=["ghidra_wrap"],
	python_requires=">=3.6",
	entry_points = {
			'console_scripts': [
				'ghidra_wrap = ghidra_wrap.__main__:main',                  
			],
		},
)
