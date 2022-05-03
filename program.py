from datetime import datetime
import json
import hashlib
import datetime
import textwrap

def addQuestion(text, object):
    hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    today = datetime.date.strftime(datetime.date.today(), '%Y%m%d')
    object[hash] = {
        "id": hash,
        "text": text,
        "createdAt": today
    }

def addSeparator():
    print(colourOutput(50,50,50, "-" * 80))

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

def colourOutput(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;200;200;200m".format(r, g, b, text)

#######################

questions = {}
addQuestion("Vad ska du göra idag?", questions)
addQuestion("Vad har du gjort idag?", questions)

journal_base = {
    "questions": questions,
    "entries": {}
}

file_handle = 'journal.json'


try:
    with open(file_handle, "r", encoding='utf-8') as journal_file:
        print(colourOutput(0,0,0, ""))
except FileNotFoundError:
    with open(file_handle, "w+", encoding='utf-8') as journal_file:
        json.dump(journal_base, journal_file, ensure_ascii=False)

with open(file_handle, "r+", encoding='utf-8') as journal_file:
    journal = json.load(journal_file)
    while True:
        mapped = {}
        addSeparator()
        for index, question in enumerate(journal['questions']):
            print(f"[{index + 1}] {journal['questions'][question]['text']}")
            mapped[index + 1] = journal['questions'][question]['id']
        choice = 0
        while choice == 0:
            try:
                choice = input("[#] Svara, [v] Visa, [n] Skapa, [q] Avsluta: ")
                addSeparator()
                if choice.lower() == "q":
                    choice = 2000
                elif choice.lower() == "n":
                    choice = 3000
                elif choice.lower() == "v":
                    choice = 4000
                choice = int(choice)
            except ValueError:
                print(colourOutput(255, 0, 0, "Felaktigt input, försök igen."))
        if choice in mapped:
            print(f"{journal['questions'][mapped[choice]]['text']} [enter]")
            entry = input()
            today = datetime.date.strftime(datetime.date.today(), '%Y%m%d')
            id = f"{today}-{mapped[choice]}"
            if id not in journal['entries']:
                journal['entries'][id] = entry
            else:
                journal['entries'][id] += " " + entry
        elif choice == 2000:
            break
        elif choice == 3000:
            text = input("Ny fråga, [enter]: ")
            if len(text) > 0:
                if not text.endswith("?"):
                    text += "?"	
                addQuestion(text, journal['questions'])
                print(colourOutput(0, 255, 0, "Frågan sparad"))
        elif choice == 4000:
            page = "n"
            date = datetime.date.today()
            while True:
                if page == "<":
                    date = date - datetime.timedelta(days=1)
                elif page == ">":
                    date = date + datetime.timedelta(days=1)
                elif page == "t":
                    break
                elif page == "n":
                    date = datetime.date.today()
                else:
                    try:
                        date = datetime.datetime.strptime(page, '%Y%m%d')
                    except ValueError:
                        print(colourOutput(255, 0, 0, "Felaktigt datum, försök igen."))
                data = getEntries(journal['entries'], date)
                print(f"{data['date'].strftime('%A %d %B %Y')}")
                addSeparator()
                for entry in data['entries']:
                    print(colourOutput(255,255,255, entry['question']))
                    print('\n'.join(textwrap.wrap(entry['answer'], 80, break_long_words=False)))
                page = input(f"[< >], [yyyymmdd], [n] nu, [t] tillbaka: ")
with open(file_handle, "w", encoding='utf-8') as journal_file:
    json.dump(journal, journal_file, ensure_ascii=False)