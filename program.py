from datetime import datetime
import json
import hashlib
import os
import datetime

def is_file_empty(file_path):
    # return os.path.exists(file_path) and os.stat(file_path).st_size == 0
    return os.path.isfile(file_path) and os.path.getsize(file_path) == 0

questions = {}
def addQuestion(text, object):
    hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    today = datetime.date.strftime(datetime.date.today(), '%Y%m%d')
    object[hash] = {
        "id": hash,
        "text": text,
        "createdAt": today
    }

addQuestion("Vad ska du göra idag?", questions)
addQuestion("Vad har du gjort idag?", questions)

journal_base = {
    "questions": questions,
    "entries": {}
}

file_handle = 'journal.json'


try:
    with open(file_handle, "r", encoding='utf-8') as journal_file:
        print("Journal file exists")
except FileNotFoundError:
    with open(file_handle, "w+", encoding='utf-8') as journal_file:
        json.dump(journal_base, journal_file, ensure_ascii=False)

with open(file_handle, "r+", encoding='utf-8') as journal_file:
    journal = json.load(journal_file)
    while True:
        mapped = {}
        for index, question in enumerate(journal['questions']):
            print(f"[{index + 1}] {journal['questions'][question]['text']}")
            mapped[index + 1] = journal['questions'][question]['id']
        choice = 0
        while choice == 0:
            try:
                choice = input("Välj en fråga att svara på eller avsluta [q], [n] ny fråga: ")
                if choice == "q":
                    choice = 2000
                elif choice == "n":
                    choice = 3000
                choice = int(choice)
            except ValueError:
                print("Du måste välja en fråga.")
        if choice in mapped:
            entry = input("Skriv, avsluta med [enter]: ")
            today = datetime.date.strftime(datetime.date.today(), '%Y%m%d')
            id = f"{today}-{mapped[choice]}"
            print(type(journal['entries']))
            if id not in journal['entries']:
                journal['entries'][id] = entry
            print(journal)
        elif choice == 2000:
            break
        elif choice == 3000:
            text = input("Skriv fråga: ")
            addQuestion(text, journal['questions'])

with open(file_handle, "w", encoding='utf-8') as journal_file:
    json.dump(journal, journal_file, ensure_ascii=False)