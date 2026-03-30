# nwcommitaveragescli
Contact: numbworks@gmail.com

## Revision History

| Date | Author | Description |
|---|---|---|
| 2025-05-19 | numbworks | Created. |
| 2026-03-30 | numbworks | Last update. |

## Introduction

`nwcommitaveragescli` is a command-line application built on the top of `nwcommitaverages`.

## CLI Reference

|*Command*|*Sub Command*|Options|Exit Codes|
|---|---|---|---|
|||*--help, -h*|Success|

|Option|Value|Default|
|---|---|---|
|--file_paths|`<file path>`|-|

```sh
```

## ------------------- TBU --------------------

## The CLI

This application is designed to run as a CLI (command-line interface) from within a terminal.

Invoking the script with the `-h` option :

```
root@17b38eb6123b:/# python nwcommitaverages.py -h
```

will return the help information:

```
usage: nwcommitaverages.py [-h] [--file_path FILE_PATH] [--logtype {table,daily,monthly}]

Calculates the average commit value and logs the result.

options:
  -h, --help            show this help message and exit

  --file_path FILE_PATH, -fp FILE_PATH
    The file path to the Git repository for which the average commit value is calculated.
    
  --logtype {table,daily,monthly}, -lt {table,daily,monthly}
    The type of log ('table' for a tabular overview, 'daily' and 'monthly' for a list of statuses). The default is 'table'.
```

Invoking the script without arguments:

```
root@17b38eb6123b:/# python nwcommitaverages.py
```

will run the script against the current folder's `Git` repository and logs a tabular overview:

```
+-------------+--------+-----------+---------------+------------+
| YearMonth   | Days   | Commits   | DailyAvgMin   | RefNames   |
+=============+========+===========+===============+============+
| 2025-05     | 2      | 26        | 13.86         |            |
+-------------+--------+-----------+---------------+------------+
```

Using the `--logtype` option:

```
root@17b38eb6123b:/# python nwcommitaverages.py --logtype daily
```

will return a list of statuses instead of a tabular overview:

```
DailyStatus(date_str='2025-05-19', timestamps=[1747679247, 1747679425, ...], avg_minutes=13.7, ref_names=[])
DailyStatus(date_str='2025-05-20', timestamps=[1747730448, 1747731075, ...], avg_minutes=14.03, ref_names=[])
```

Using the `--file_path` option:

```
root@17b38eb6123b:/# python nwcommitaverages.py --file_path /workspaces/nwsomething
```

will allow you to run the script against a different `Git` repository than the current folder's one.

If `Git` is not installed on the host machine or other issues occur, an error message will be logged.

## Wheh installed via `pip`...

Wheh installed via `pip`, the command to run the application is `python -m <application name>`:

```
pip install --extra-index-url https://numbworks.github.io nwcommitaverages==1.0.0
python -m nwcommitaverages
```

## ------------------- TBU --------------------

## Markdown Toolset

Suggested toolset to view and edit this Markdown file:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)
- [Markdown PDF](https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf)