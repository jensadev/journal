# Journal

Doing something with Python for once. Inspired by https://github.com/trys/JournalBook .

A simple program for writing daily logs. The journal asks simple retrospective questions 
for the user to answer. The answers are stored in a file and can be appended.
The user cannot erase or edit the journal, and you can only add entries for the current day.

## Usage

Requires python3. Tested on windows and linux.

Run with `python journal.py` or build your own exe.

```
pyinstaller -F --add-data "translations/en.json;." --add-data "translations/sv.json;." .\journal.py
```
