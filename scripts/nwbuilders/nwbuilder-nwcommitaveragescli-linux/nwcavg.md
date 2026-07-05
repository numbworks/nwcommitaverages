% nwcavg

# NAME
nwcavg - calculate the average time between Git commits

# SYNOPSIS
**nwcavg** [command] [options]

# DESCRIPTION
**nwcavg** is a CLI application designed to calculate the average time between Git commits.

# OPTIONS
**-?, -h, --help**
Show help and usage information.

**--folder_path**
The path to the Git repository folder for which the average commit value is calculated.

# PRE-REQUISITES
In order to work, it requires to be run against a local Git repository and that Git itself is installed on the machine.

# EXAMPLES
**Run it against the current folder:**

```text
nwcavg
```

**Run it against another folder:**

```text
nwcavg --folder_path /home/test_application
```

# AUTHOR
numbworks (numbworks@gmail.com)