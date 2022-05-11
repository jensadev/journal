import sys
from pathlib import Path
from termcolor import colored, cprint
import colorama
import json
import hashlib
import datetime
import textwrap
import os
import os.path
import time
import locale
from i18n import resource_loader
from i18n.translator import t
from i18n import config


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path, 'translations')


relative_path = os.path.join(os.path.dirname(__file__))

TRANSLATION_FOLDER = resource_path(relative_path)
resource_loader.init_loaders()
config.set('load_path', [TRANSLATION_FOLDER])
config.set("file_format", "json")
config.set('filename_format', '{locale}.{format}')
config.set('fallback', 'en')

locale.setlocale(locale.LC_ALL, '')
loc, encoding = locale.getdefaultlocale()

if loc == 'sv_SE':
    config.set('locale', 'sv')

resource_loader.init_json_loader()

colorama.init(autoreset=True)

SLEEP_TIME = 0.35


def input_colorama(message):
    print(message, end='')
    return input()


def addQuestion(text, object):
    hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    today = datetime.date.strftime(datetime.date.today(), '%Y%m%d')
    object[hash] = {
        "id": hash,
        "text": text,
        "createdAt": today
    }


def printSeparator():
    cprint("-" * 80, 'yellow')


def clearScreen():
    # print("\033c")
    os.system('cls||clear')


def newScreen(heading=False):
    clearScreen()
    if heading:
        print(" " + heading)
    printSeparator()


def getEntries(dict, search_date):
    string_date = datetime.date.strftime(search_date, '%Y%m%d')
    day = {
        "date": search_date,
        "favourite": string_date in journal['favourites'],
        "entries": []
    }
    for entry in dict:
        # handle removed questions
        try:
            if entry.startswith(string_date):
                day['entries'].append({
                    "question": journal['questions'][entry.split('-')[1]]['text'],
                    "answer": dict[entry]
                })
        except KeyError:
            pass
    return day


def getMainChoice():
    while True:
        try:
            edit_text = t('QUESTION.EDIT_NUMBER', count=1)
            history_text = t('HISTORY')
            print((f"{colored('[' + history_text[0].lower() + ']', 'white', attrs=['bold'])}" +
                   f" {history_text} " +
                   f"{colored('[' + edit_text[0].lower() + ']', 'white', attrs=['bold'])}" +
                   f" {edit_text} " +
                   f"{colored('[enter]', 'white', attrs=['bold'])}" +
                   f" {t('QUIT')}"))
            choice = input_colorama(prompt)
            if choice == "":
                choice = 2000
            elif choice.lower() == edit_text[0].lower():
                choice = 3000
            elif choice.lower() == history_text[0].lower():
                choice = 4000
            return int(choice)
        except ValueError:
            cprint(t('ERRORS.WRONG_INPUT_TRY_AGAIN'), 'red',
                   attrs=['bold'], file=sys.stderr)


def saveError(error, file):
    print(
        f"{t('SAVING_ERROR_TO_FILE')} {colored(file , 'red', attrs=['underline'])}")
    with open(file, "a+", encoding='utf-8') as err_file:
        print(f"[{datetime.datetime.now().strftime('%c')}] {err}", file=err_file)

def printQuestions(i_text = True, map = False):
    mapped = {}
    for index, question in enumerate(journal['questions']):
        index_text = ''
        if i_text:
            index_text = colored(f"[{index + 1}] ", 'white', attrs=['bold'])

        print(index_text + f"{colored(journal['questions'][question]['text'], 'magenta')}")
        if map:
            mapped[index + 1] = journal['questions'][question]['id']
    return mapped

################################################################################


questions = {}
addQuestion(t('QUESTIONS.1.QUESTION'), questions)
addQuestion(t('QUESTIONS.2.QUESTION'), questions)
addQuestion(t('QUESTIONS.3.QUESTION'), questions)

journal_base = {
    "questions": questions,
    "entries": {},
    "favourites": []
}

prompt = colored(": ", 'white', attrs=['bold'])

file_handle = 'journal'
file_dir = '.journal'
file_home = str(Path.home())
file_path = str(os.path.join(file_home, file_dir, file_handle))
file_json = file_path + '.json'
file_temp = file_path + '.tmp'
file_err = file_path + '.err'

journal = False

try:
    with open(file_json, "r", encoding='utf-8') as journal_file:
        journal = json.load(journal_file)
        heading = f"\n{t('LOADING_JOURNAL_FROM_FILE')} {colored(file_json , 'cyan', attrs=['underline'])}"
        newScreen(heading)
except FileNotFoundError:
    path = os.path.join(file_home, file_dir)
    os.makedirs(path, exist_ok=True)
    with open(file_json, "w+", encoding='utf-8') as journal_file:
        json.dump(journal_base, journal_file, ensure_ascii=False)
        journal = journal_base
        heading = f"\n{t('CREATING_JOURNAL_FILE')} {colored(file_json, 'cyan', attrs=['underline'])}"
        newScreen(heading)
except json.decoder.JSONDecodeError as err:
    heading = f"\n{t('WRONG_FORMAT_IN_FILE')} {colored(file_json , 'cyan', attrs=['underline'])}"
    newScreen(heading)
    cprint(t('QUITTING'), 'red', attrs=['bold'])
    saveError(err, file_err)
    sys.exit(1)
except PermissionError as err:
    heading = f"\n{t('CANNOT_OPEN_FILE')} {colored(file_json, 'cyan', attrs=['underline'])}"
    newScreen(heading)
    cprint(t('QUITTING'), 'red', attrs=['bold'])
    saveError(err, file_err)
    sys.exit(1)
except Exception as err:
    heading = f"\n{t('UNKNOWN_ERROR')}"
    newScreen(heading)
    cprint(t('QUITTING'), 'red', attrs=['bold'])
    saveError(err, file_err)
    sys.exit(1)

time.sleep(SLEEP_TIME)

TITLE_HEADING = colored("Journal", 'yellow', attrs=['bold'])

while True:
    newScreen(TITLE_HEADING)
    mapped = printQuestions(map=True)
    choice = getMainChoice()
    if choice in mapped:
        newScreen(colored(t('ANSWER'), 'yellow', attrs=['bold']))
        print(f"{colored(journal['questions'][mapped[choice]]['text'], 'magenta')} " +
              colored("[enter]", 'white', attrs=['bold']))
        today = datetime.date.strftime(datetime.date.today(), '%Y%m%d')
        id = f"{today}-{mapped[choice]}"
        if id in journal['entries']:
            cprint('\n'.join(textwrap.wrap(
                journal['entries'][id], 80, break_long_words=False)), 'white', attrs=['dark'])
        entry = input()
        if id not in journal['entries']:
            journal['entries'][id] = entry
        else:
            journal['entries'][id] += " " + entry
    elif choice == 2000:
        break
    elif choice == 3000:
        heading = colored(t('QUESTION.EDIT_NUMBER', count=1),
                          'yellow', attrs=['bold'])
        newScreen(heading)
        printQuestions(False)
        print((f"{colored('[enter]', 'white', attrs=['bold'])}" +
               f" {t('QUESTION.WRITE_NEW')} " +
               f"{colored(t('QUESTION.QUESTION').lower(), 'magenta')}" +
               f" {t('QUESTION.OR_EXISTING')} " +
               f"{colored(t('QUESTION.QUESTION').lower(), 'magenta')}" +
               f" {t('QUESTION.TO_REMOVE')}"))
        text = input()
        if len(text) > 0:
            if not text.endswith("?"):
                text += "?"
            question_exists = False  # False or stored question
            for question in journal['questions']:
                if text.lower() == journal['questions'][question]['text'].lower():
                    question_exists = question
                    break
            if not question_exists:
                addQuestion(text, journal['questions'])
            else:
                del journal['questions'][question_exists]

    elif choice == 4000:
        page = "init"
        date = datetime.date.today()
        favourite_text = t('FAVOURITE')
        while True:
            if page == "<":
                date = date - datetime.timedelta(days=1)
            elif page == ">":
                date = date + datetime.timedelta(days=1)
            elif page == favourite_text[0].lower():
                date_string = datetime.date.strftime(date, '%Y%m%d')
                if not date_string in journal['favourites']:
                    journal['favourites'].append(date_string)
                else:
                    journal['favourites'].remove(date_string)
            elif page == "" or page == "init":
                today = datetime.date.today()
                if date == today and not page == "init":
                    break
                else:
                    date = datetime.date.today()
            else:
                try:
                    date = datetime.datetime.strptime(page, '%Y%m%d')
                except ValueError:
                    cprint(t('ERRORS.INCORRECT_TYPE_FORMAT_TRY_AGAIN', type=t('DATE').lower()),
                           'red', attrs=['bold'], file=sys.stderr)
                    time.sleep(SLEEP_TIME)
            data = getEntries(journal['entries'], date)
            if data['favourite']:
                heading_favourite = colored("*", 'yellow', attrs=['bold'])
            else:
                heading_favourite = colored("*", 'white', attrs=['dark'])
            date_string = data['date'].strftime('%A %d %B %Y')
            heading = (f"{colored(date_string, 'yellow', attrs=['bold'])} " +
                       " " * (76 - len(date_string)) +
                       heading_favourite)
            newScreen(heading)
            if not len(data['entries']):
                print(t('NO_ENTRIES'))
            for entry in data['entries']:
                if entry['answer']:
                    cprint(entry['question'], 'magenta')
                    print('\n'.join(textwrap.wrap(
                        entry['answer'], 80, break_long_words=False)))
            printSeparator()

            print((f"{colored('[<]', 'white', attrs=['bold'])} " +
                   f"{colored('[>]', 'white', attrs=['bold'])} " +
                   f"{colored('[yyyymmdd]', 'white', attrs=['bold'])} " +
                   f"{colored('[' + favourite_text[0].lower() + ']', 'white', attrs=['bold'])}" +
                   f" {favourite_text} " +
                   f"{colored('[enter]', 'white', attrs=['bold'])} " +
                   t('BACK')))
            page = input_colorama(prompt)

file_check = False

with open(file_temp, "w", encoding='utf-8') as temp_file:
    try:
        json.dump(journal, temp_file, ensure_ascii=False)
        file_check = True
    except Exception as err:
        heading = f"{t('ERRORS.CANNOT_WRITE_FILE')} {colored(file_json, 'cyan', attrs=['underline'])}"
        newScreen(heading)
        cprint(t('QUITTING'), 'red', attrs=['bold'])
        saveError(err, file_err)
        sys.exit(1)

if file_check:
    os.remove(file_temp)
    with open(file_json, "w", encoding='utf-8') as journal_file:
        json.dump(journal, journal_file, ensure_ascii=False)
        clearScreen()
    print(
        f"{t('SAVED_JOURNAL_TO_FILE')} {colored(file_json, 'cyan', attrs=['underline'])}")
