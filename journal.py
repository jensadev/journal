import sys
from pathlib import Path
from termcolor import colored, cprint
import colorama
import json
import hashlib
import datetime
import textwrap
import os
import time
colorama.init(autoreset=True)


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
    print("\033c")


def newScreen(heading = False):
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
    choice = 0
    while True:
        try:
            print((f"{colored('[h]', 'white', attrs=['bold'])}" +
                   " Historik " +
                   f"{colored('[r]', 'white', attrs=['bold'])}" +
                   " Redigera frågor " +
                   f"{colored('[enter]', 'white', attrs=['bold'])}" +
                   " Avsluta"))
            choice = input_colorama(prompt)
            if choice == "":
                choice = 2000
            elif choice.lower() == "r":
                choice = 3000
            elif choice.lower() == "h":
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
        heading = f"\nLaddar in journal från {colored(file_json , 'cyan', attrs=['underline'])}"
        newScreen(heading)
except FileNotFoundError:
    path = os.path.join(file_home, file_dir)
    os.makedirs(path, exist_ok=True)
    with open(file_json, "w+", encoding='utf-8') as journal_file:
        json.dump(journal_base, journal_file, ensure_ascii=False)
        journal = journal_base
        heading = f"\nSkapar journal {colored(file_json, 'cyan', attrs=['underline'])}"
        newScreen(heading)
except json.decoder.JSONDecodeError as err:
    heading = f"\nFelaktigt format i journalfilen {colored(file_json , 'cyan', attrs=['underline'])}"
    newScreen(heading)
    cprint("Avslutar", 'red', attrs=['bold'])
    saveError(err, file_err)
    sys.exit(1)
except PermissionError as err:
    heading = f"\nKan inte läsa/skriva till journal {colored(file_json, 'cyan', attrs=['underline'])}"
    newScreen(heading)
    cprint("Avslutar", 'red', attrs=['bold'])
    saveError(err, file_err)
    sys.exit(1)
except Exception as err:
    heading = f"\nOkänt fel i journal {colored(file_json, 'cyan', attrs=['underline'])}"
    newScreen(heading)
    cprint("Avslutar", 'red', attrs=['bold'])
    saveError(err, file_err)
    sys.exit(1)


while True:
    time.sleep(0.3)
    heading = colored("Journal", 'yellow', attrs=['bold'])
    newScreen(heading)
    mapped = {}
    for index, question in enumerate(journal['questions']):
        index_text = f"[{index + 1}] "
        print((f"{colored(index_text, 'white', attrs=['bold'])}" +
               f"{colored(journal['questions'][question]['text'], 'magenta')}"))
        mapped[index + 1] = journal['questions'][question]['id']
    choice = getMainChoice()
    if choice in mapped:
        newScreen(colored("Svara", 'yellow', attrs=['bold']))
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
        heading = colored("Redigera", 'yellow', attrs=['bold'])
        newScreen(heading)
        print((f"{colored('[enter]', 'white', attrs=['bold'])}" +
            " Skriv ny " +
               f"{colored('fråga', 'magenta')}" +
               " eller en existerande " +
               f"{colored('fråga', 'magenta')}" +
               " för att radera"))
        text = input()
        if len(text) > 0:
            if not text.endswith("?"):
                text += "?"
            question_exists = False # False or stored question
            for question in journal['questions']:
                if text.lower() == journal['questions'][question]['text'].lower():
                    question_exists = question
                    break
            if not question_exists:
                addQuestion(text, journal['questions'])
            else:
                del journal['questions'][question_exists]


    elif choice == 4000:
        page = "i"
        date = datetime.date.today()
        while True:
            if page == "<":
                date = date - datetime.timedelta(days=1)
            elif page == ">":
                date = date + datetime.timedelta(days=1)
            elif page == "f":
                date_string = datetime.date.strftime(date, '%Y%m%d')
                if not date_string in journal['favourites']:
                    journal['favourites'].append(date_string)
                else:
                    journal['favourites'].remove(date_string)
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
            # cprint(data['date'].strftime('%A %d %B %Y'),
            #        'yellow', attrs=['bold'])
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
                print(f"Svar saknas")
            for entry in data['entries']:
                cprint(entry['question'], 'magenta')
                print('\n'.join(textwrap.wrap(
                    entry['answer'], 80, break_long_words=False)))
            printSeparator()
            print((f"{colored('[<]', 'white', attrs=['bold'])} " +
                   f"{colored('[>]', 'white', attrs=['bold'])} " +
                   f"{colored('[yyyymmdd]', 'white', attrs=['bold'])} " +
                   f"{colored('[i]', 'white', attrs=['bold'])} " +
                   "Idag " +
                   f"{colored('[f]', 'white', attrs=['bold'])} " +
                   "Favorit " +
                   f"{colored('[enter]', 'white', attrs=['bold'])} " +
                   "Tillbaka"))
            # page = input(prompt)
            page = input_colorama(prompt)

file_check = False

with open(file_temp, "w", encoding='utf-8') as temp_file:
    try:
        json.dump(journal, temp_file, ensure_ascii=False)
        file_check = True
    except Exception as err:
        heading = f"Kunde inte spara {colored(file_json, 'cyan', attrs=['underline'])}"
        newScreen(heading)
        cprint("Avslutar", 'red', attrs=['bold'])
        saveError(err, file_err)
        sys.exit(1)

if file_check:
    os.remove(file_temp)
    with open(file_json, "w", encoding='utf-8') as journal_file:
        json.dump(journal, journal_file, ensure_ascii=False)
        clearScreen()
    print(
        f"Journal sparad {colored(file_json, 'cyan', attrs=['underline'])}")
