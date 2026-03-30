'''Contains packaging instructions.'''

# GLOBAL MODULES
from setupinfo import PROJECT_VERSION, PROJECT_AUTHOR, PROJECT_ALIAS, PROJECT_URL, LIBRARY_NAME, LIBRARY_DESCRIPTION
from setuptools import setup

# SETUP
if __name__ == "__main__":
    setup(
        name = LIBRARY_NAME,
        version = PROJECT_VERSION,
        description = LIBRARY_DESCRIPTION,
        author = PROJECT_AUTHOR,
        url = PROJECT_URL,
        py_modules = [ LIBRARY_NAME ],
        install_requires = [ 
			"tabulate>=0.9.0"
		],
        python_requires = ">=3.12",
        license = "MIT"
    )