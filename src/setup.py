'''Contains packaging information about nwcommitaverages.py.'''

# GLOBAL MODULES
from setupinfo import MODULE_NAME, MODULE_VERSION
from setuptools import setup

# SETUP
if __name__ == "__main__":
    setup(
        name = MODULE_NAME,
        version = MODULE_VERSION,
        description = "A CLI application designed to calculate the average time between Git commits.",
        author = "numbworks",
        url = f"https://github.com/numbworks/{MODULE_NAME}",
        py_modules = [ MODULE_NAME ],
        install_requires = [ 
			"tabulate>=0.9.0"
		],
        python_requires = ">=3.12",
        license = "MIT"
    )