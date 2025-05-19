'''Contains packaging information about nwcommitaverages.py.'''

# GLOBAL MODULES
from setuptools import setup

# INFORMATION
MODULE_ALIAS : str = "nwca"
MODULE_NAME : str = "nwcommitaverages"
MODULE_VERSION : str = "1.0.0"

# SETUP
if __name__ == "__main__":
    setup(
        name = MODULE_NAME,
        version = MODULE_VERSION,
        description = "A CLI application designed to calculate the average time between git commits.",
        author = "numbworks",
        url = f"https://github.com/numbworks/{MODULE_NAME}",
        py_modules = [ MODULE_NAME ],
        install_requires = [ 
			"tabulate>=0.9.0"
		],
        python_requires = ">=3.12",
        license = "MIT"
    )