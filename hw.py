from classes import Record, Name, Phone, Birthday, AddressBook, Iterator
import re


STOP_LIST = ("good bye", "close", "exit")
FILE_PATH = "./address.book"

address_book = AddressBook()


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Контакт або номер телефону не знайдений."
        except (IndexError, AttributeError):
            return "Не вірна команда."
        except ValueError:
            return "Введені данні некоректні."
    return inner


def user_input_split(user_input):
    matches = re.match(r'\w+\s+(\D+)\s([+]?\d{7,15})', user_input)
    if matches:
        name = Name(matches.group(1))
        phone = Phone(matches.group(2))
        return name, phone
    else:
        return "Данні відсутні."
    

def handle_hello():
    return "Добрий день. Чим можу допомогти?"


@input_error
def handle_add(*args):
    args = args[0].split(' ')
    name = Name(args[1])
    birthday = ''
    record = Record(name, birthday=birthday)
    if len(args) >= 4:
        match = re.match(r"^([0-9]{2})[\\\/\-\., ]?([0-9]{2})[\\\/\-\., ]?([0-9]{4})$", args[-1])
        if bool(match):
            birthday = Birthday(args[-1])
            record = Record(name, birthday=birthday)
            for p in args[2:-1]:
                phone = Phone(p)
                record.add_phone(phone)
        else:
            for p in args[2:]:
                phone = Phone(p)
                record.add_phone(phone)
    else:
        phone = Phone(args[2])
        record.add_phone(phone)
    if str(name) not in address_book.data.keys():
        address_book.add_record(record)
        address_book.serialize(FILE_PATH)
    else:
        current_rec = address_book.data[str(name)].phones
        for p in record.phones:
            if p in current_rec:
                current_rec.remove(p)
        address_book.update_record(record)
        address_book.serialize(FILE_PATH)
    return f"Name: {str(name)}\n{address_book.data[str(name)]}\n"


@input_error
def handle_change(user_input):
    matches = re.match(r'\w+\s+(\D+)\s([+]?\d{7,15})\s([+]?\d{7,15})', user_input)
    name, old_phone, new_phone = matches.group(1), Phone(matches.group(2)), Phone(matches.group(3))
    if name in address_book.data.keys():
        record = address_book.data[name]
        record.change_phone(old_phone, new_phone)
        address_book.add_record(record)
        address_book.serialize(FILE_PATH)
        return f"Контакт {name} був змінений. Новий номер телефону {new_phone}.\n"
    else:
        raise KeyError
 
    
@input_error
def handle_delete(user_input):
    matches = re.match(r'\w+\s+(\D+)\s([+]?\d{7,15})', user_input)
    if matches:
        name, phone = matches.group(1), matches.group(2)
    if name in address_book.data.keys():
        record = address_book.data[name]
        record.delete_phone(phone)
        if record.phones:
            address_book.add_record(record)
            address_book.serialize(FILE_PATH)
        else:
            del address_book.data[name]
            address_book.serialize(FILE_PATH)
        return f"Контакт {name} був змінений. Номер телефону {phone} видалений.\n"
    else:
        return f"У контакта {name} номер телефона {phone} не знайдений.\n"

    
@input_error   
def handle_phone(user_input):
    name = re.match(r'\w+\s+(\D+)', user_input).group(1)
    if name in address_book.data.keys():
        return f"Контакт {name}: {address_book.data[name]}\n"
    else:
        raise KeyError
    
@input_error 
def handle_search(user_input):
    search_str = re.match(r'\w+\s+(\w+)$', user_input).group(1)
    search_results = address_book.search(search_str)
    if search_results:
        return search_results
    else:
        print("Контактів зі збігом не знайдено.")
    
@input_error 
def handle_birthday(user_input):
    name = re.match(r'\w+\s+(\D+)', user_input).group(1)
    if name in address_book.data.keys():
        record = address_book.data[name]
        days = record.days_to_birthday()
        return f"До дня народження {name} залишилось {days}д. День народження {record.birthday}\n"
    else:
        raise KeyError 
    
def handle_showall():
    if not address_book.data:
        return "Книга контактів порожня"
    else:
        iterator = Iterator(address_book)
        for record in iterator:
            print(record)
            try:
                input("Нажміть 'Enter' для продовження\n")
            except KeyboardInterrupt:
                break
    return "Кінець\n"

def commands(user_input):
        if user_input.lower() == "Добрий день!":
            response = handle_hello()
        elif re.search(r"^add ", user_input, re.IGNORECASE):
            response = handle_add(user_input)
        elif re.search(r"^change ", user_input, re.IGNORECASE):
            response = handle_change(user_input)
        elif re.search(r"^delete ", user_input, re.IGNORECASE):
            response = handle_delete(user_input)    
        elif re.search(r"^phone ", user_input, re.IGNORECASE):
            response = handle_phone(user_input)
        elif re.search(r"^birthday ", user_input, re.IGNORECASE):
            response = handle_birthday(user_input)
        elif re.search(r"^search ", user_input, re.IGNORECASE):
            response = handle_search(user_input)       
        elif user_input.lower() == "show all":
            response = handle_showall()
        else:
            response = "Не вірна команда."
        if response:
            print(response)    


def main():
    try:
        address_book.deserialize(FILE_PATH)
    except FileNotFoundError:
        print("Файл з даними не знайдено. Створено нову адресну книгу.")
        
    while True:
        user_input = input("Введіть будь-ласка команду: ")
        if user_input in STOP_LIST:
            address_book.serialize(FILE_PATH)
            print("Данні збережені. До побачення!")
            break
        else:
            commands(user_input)

      
if __name__ == "__main__":
        main()