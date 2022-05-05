import sys
from pathlib import Path
from termcolor import colored, cprint
from colorama import init, Style, Fore
import json
import hashlib
import datetime
import textwrap
import os
init(autoreset=True)


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


def getEntries(dict, search_date):
    day = {
        "date": search_date,
        "entries": []
    }
    string_date = datetime.date.strftime(search_date, '%Y%m%d')
    for entry in dict:
        if entry.startswith(string_date):
            day['entries'].append({
                "question": journal['questions'][entry.split('-')[1]]['text'],
                "answer": dict[entry]
            })
    return day


def getMainChoice():
    choice = 0
    while True:
        try:
            print((f"{colored('[v]', 'white', attrs=['bold'])}" +
                   " Visa " +
                   f"{colored('[n]', 'white', attrs=['bold'])}" +
                   " Ny fråga " +
                   f"{colored('[enter]', 'white', attrs=['bold'])}" +
                   " Avsluta"))
            choice = input(prompt)
            printSeparator()
            if choice == "":
                choice = 2000
            elif choice.lower() == "n":
                choice = 3000
            elif choice.lower() == "v":
                choice = 4000
            return int(choice)
        except ValueError:
            cprint("Felaktigt input, försök igen.",
                   'red', attrs=['bold'], file=sys.stderr)


def saveError(error, file):
    print(f"Skriver fel till {colored(file , 'red', attrs=['underline'])}")
    with open(file, "a+", encoding='utf-8') as err_file:
        print(f"[{datetime.datetime.now().strftime('%c')}] {err}", file=err_file)
#######################


questions = {}
addQuestion("Vad ska du göra idag?", questions)
addQuestion("Vad har du gjort idag?", questions)

journal_base = {
    "questions": questions,
    "entries": {},
    "favourites": []
}

prompt = colored("❯ ", 'green', attrs=['bold', 'blink'])

file_handle = 'journal'
file_dir = '.journal'
file_home = str(Path.home())
file_path = file_home + '/' + file_dir + '/' + file_handle
file_json = file_path + '.json'
file_temp = file_path + '.tmp'
file_err = file_path + '.err'

journal = False

try:
    with open(file_json, "r", encoding='utf-8') as journal_file:
        journal = json.load(journal_file)
        print(
            f"\nLaddar in journal från {colored(file_json , 'cyan', attrs=['underline'])}")
except FileNotFoundError:
    path = os.path.join(file_home, file_dir)
    os.makedirs(path, exist_ok=True)
    with open(file_json, "w+", encoding='utf-8') as journal_file:
        print(
            f"\nSkapar journal {colored(file_json, 'cyan', attrs=['underline'])}")
        json.dump(journal_base, file_json, ensure_ascii=False)
        journal = journal_base
except json.decoder.JSONDecodeError as err:
    print(
        f"\nFelaktigt format i journalfilen {colored(file_json , 'cyan', attrs=['underline'])}")
    saveError(err, file_err)
    sys.exit(1)
except PermissionError as err:
    print(
        f"\nKan inte läsa/skriva till journal {colored(file_json, 'cyan', attrs=['underline'])}")
    saveError(err, file_err)
    sys.exit(1)
except Exception as err:
    print(
        f"\nOkänt fel i journal {colored(file_json, 'cyan', attrs=['underline'])}")
    saveError(err, file_err)
    sys.exit(1)


while True:
    mapped = {}
    printSeparator()
    for index, question in enumerate(journal['questions']):
        index_text = f"[{index + 1}] "
        print((f"{colored(index_text, 'white', attrs=['bold'])}" +
                f"{colored(journal['questions'][question]['text'], 'magenta')}"))
        mapped[index + 1] = journal['questions'][question]['id']
    choice = getMainChoice()
    if choice in mapped:
        print(f"{journal['questions'][mapped[choice]]['text']} " +
                colored("[enter]", 'white', attrs=['bold']))
        today = datetime.date.strftime(datetime.date.today(), '%Y%m%d')
        id = f"{today}-{mapped[choice]}"
        if id in journal['entries']:
            cprint('\n'.join(textwrap.wrap(
                journal['entries'][id], 80, break_long_words=False)), 'white', attrs=['dark'])
        entry = input(prompt)
        if id not in journal['entries']:
            journal['entries'][id] = entry
        else:
            journal['entries'][id] += " " + entry
    elif choice == 2000:
        break
    elif choice == 3000:
        print((f"{colored('[enter]', 'white', attrs=['bold'])} " +
                f"{colored('Ny fråga', 'magenta')}"))
        text = input(prompt)
        if len(text) > 0:
            if not text.endswith("?"):
                text += "?"
            addQuestion(text, journal['questions'])
    elif choice == 4000:
        page = "i"
        date = datetime.date.today()
        while True:
            if page == "<":
                date = date - datetime.timedelta(days=1)
            elif page == ">":
                date = date + datetime.timedelta(days=1)
            elif page == "*":
                journal['favourites'].append(
                    datetime.date.strftime(date, '%Y%m%d'))
                journal['favourites']
            elif page == "":
                break
            elif page.lower() == "i":
                date = datetime.date.today()
            else:
                try:
                    date = datetime.datetime.strptime(page, '%Y%m%d')
                except ValueError:
                    cprint("Felaktigt datum, försök igen.",
                            'red', attrs=['bold'], file=sys.stderr)
            data = getEntries(journal['entries'], date)
            cprint(data['date'].strftime('%A %d %B %Y'),
                    'yellow', attrs=['bold'])
            printSeparator()
            for entry in data['entries']:
                cprint(entry['question'], 'magenta', attrs=['bold'])
                print('\n'.join(textwrap.wrap(
                    entry['answer'], 80, break_long_words=False)))
            if len(data['entries']) > 0:
                printSeparator()
            print((f"{colored('[<]', 'white', attrs=['bold'])} " +
                    f"{colored('[>]', 'white', attrs=['bold'])} " +
                    f"{colored('[yyyymmdd]', 'white', attrs=['bold'])} " +
                    f"{colored('[i]', 'white', attrs=['bold'])} " +
                    "Idag " +
                    f"{colored('[*]', 'white', attrs=['bold'])} " +
                    "Favorit " +
                    f"{colored('[enter]', 'white', attrs=['bold'])} " +
                    "Avsluta"))
            page = input(prompt)
            printSeparator()

with open(file_temp, "w", encoding='utf-8') as temp_file:
    try:
        json.dump(journal, temp_file, ensure_ascii=False)
        with open(file_json, "w", encoding='utf-8') as journal_file:
            json.dump(journal, journal_file, ensure_ascii=False)
            os.remove(file_temp)
        print(
            f"Journal sparad {colored(file_path, 'cyan', attrs=['underline'])}")
    except Exception as err:
        print(
            f"Kunde inte spara {colored(file_json, 'cyan', attrs=['underline'])}")
        saveError(err, file_err)
        sys.exit(1)
