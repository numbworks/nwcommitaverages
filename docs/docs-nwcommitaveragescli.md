# nwcommitaveragescli
Contact: numbworks@gmail.com

## Revision History

| Date | Author | Description |
|---|---|---|
| 2025-05-19 | numbworks | Created. |
| 2026-03-30 | numbworks | Last update (2.0.0). |

## Introduction

`nwcommitaveragescli` is a command-line application built on the top of `nwcommitaverages`.

## CLI Reference

|*Command*|*Sub Command*|Options|Exit Codes|
|---|---|---|---|
|||*--help, -h*|Success|

|Option|Value|Default|
|---|---|---|
|--folder_path|`<folder path>`|-|

## Examples

Run it against the current folder:

```sh
root@149754910e58:/home# python -m nwcommitaveragescli
```

```
*****************************************************************
'##::: ##:'##:::::'##::'######:::::'###::::'##::::'##::'######:::
 ###:: ##: ##:'##: ##:'##... ##:::'## ##::: ##:::: ##:'##... ##::
 ####: ##: ##: ##: ##: ##:::..:::'##:. ##:: ##:::: ##: ##:::..:::
 ## ## ##: ##: ##: ##: ##:::::::'##:::. ##: ##:::: ##: ##::'####:
 ##. ####: ##: ##: ##: ##::::::: #########:. ##:: ##:: ##::: ##::
 ##:. ###: ##: ##: ##: ##::: ##: ##.... ##::. ## ##::: ##::: ##::
 ##::. ##:. ###. ###::. ######:: ##:::: ##:::. ###::::. ######:::
..::::..:::...::...::::......:::..:::::..:::::...::::::......::::
**********************************************Version: 2.0.0*****

Folder:'/home'

+-------------+--------+-----------+---------------+------------+
| YearMonth   | Days   | Commits   | DailyAvgMin   | RefNames   |
+=============+========+===========+===============+============+
| 2025-05     | 2      | 29        | 16.71         |            |
+-------------+--------+-----------+---------------+------------+
| 2026-03     | 2      | 26        | 16.43         |            |
+-------------+--------+-----------+---------------+------------+
| 2026-04     | 1      | 4         | 73.76         |            |
+-------------+--------+-----------+---------------+------------+
```

Run it against another folder::

```sh
root@149754910e58:/home# python -m nwcommitaveragescli --folder_path /home/test
```

```
*****************************************************************
'##::: ##:'##:::::'##::'######:::::'###::::'##::::'##::'######:::
 ###:: ##: ##:'##: ##:'##... ##:::'## ##::: ##:::: ##:'##... ##::
 ####: ##: ##: ##: ##: ##:::..:::'##:. ##:: ##:::: ##: ##:::..:::
 ## ## ##: ##: ##: ##: ##:::::::'##:::. ##: ##:::: ##: ##::'####:
 ##. ####: ##: ##: ##: ##::::::: #########:. ##:: ##:: ##::: ##::
 ##:. ###: ##: ##: ##: ##::: ##: ##.... ##::. ## ##::: ##::: ##::
 ##::. ##:. ###. ###::. ######:: ##:::: ##:::. ###::::. ######:::
..::::..:::...::...::::......:::..:::::..:::::...::::::......::::
**********************************************Version: 2.0.0*****

Folder:'/home/test'

Command '['git', '-C', '/home/test', 'log', '--pretty=format:%cs;%ct;%D', '--reverse']' returned non-zero exit status 128.
```

## Markdown Toolset

Suggested toolset to view and edit this Markdown file:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)
- [Markdown PDF](https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf)