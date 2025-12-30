import re
from collections import UserDict
from datetime import datetime, date, timedelta

# -------------------- Поля --------------------
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        # Очищення від зайвих знаків
        cleaned = "".join(filter(str.isdigit, value))
        
        # Обробка формату +380...
        if len(cleaned) == 12 and cleaned.startswith('380'):
            cleaned = cleaned[2:]
            
        if len(cleaned) != 10:
            raise ValueError("Phone number must be 10 digits long.")
            
        super().__init__(cleaned)


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
    
# -------------------- Контакт --------------------
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        p = self.find_phone(phone)
        if p:
            self.phones.remove(p)
        else:
            raise ValueError("Phone not found")

    def edit_phone(self, old_phone, new_phone):
        p = self.find_phone(old_phone)
        if p:
            new_phone_obj = Phone(new_phone)
            self.phones[self.phones.index(p)] = new_phone_obj
        else:
            raise ValueError("Old phone not found")

    def find_phone(self, phone):
        target = phone.value if isinstance(phone, Phone) else phone
        for p in self.phones:
            if p.value == target:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = "; ".join(p.value for p in self.phones) if self.phones else "N/A"
        birthday_str = self.birthday.value if self.birthday else "N/A"
        return f"Contact name: {self.name.value}; phones: {phones_str}; birthday: {birthday_str}"


    

# -------------------- Адресна книга -------------------
    
    
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def adjust_for_weekend(self, bday: date) -> date:
        """Якщо день народження випадає на вихідні, перенести на понеділок"""
        if bday.weekday() == 5:  # субота
            return bday + timedelta(days=2)
        elif bday.weekday() == 6:  # неділя
            return bday + timedelta(days=1)
        return bday
    

    def get_upcoming_birthdays(self, days=7):
        upcoming = []
        today = date.today()

        for record in self.data.values():
            if not record.birthday:
                continue

            bday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()

            bday_this_year = bday.replace(year=today.year)
            if bday_this_year < today:
                bday_this_year = bday_this_year.replace(year=today.year + 1)
            bday_this_year = self.adjust_for_weekend(bday_this_year)
            if 0 <= (bday_this_year - today).days <= days:
                upcoming.append({
                    "name": record.name.value,
                    "birthday": bday_this_year.strftime("%d.%m.%Y")
                })
        return upcoming
    
    

    def __str__(self):
        if not self.data:
            return "Address book is empty."
        return "\n".join(str(record) for record in self.data.values())


# -------------------- Декоратор для обробки помилок --------------------
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"Value error: {e}"
        except IndexError:
            return "Enter the argument for the command."
        except KeyError:
            return "Contact not found."
    return inner


# -------------------- Команди --------------------
@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 1:
        return "Please provide a name."
    
    name = args[0]
    phone = args[1] if len(args) > 1 else None
    
    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    else:
        message = "Contact updated."

    if phone:
        record.add_phone(phone)
    
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_p, new_p = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.edit_phone(old_p, new_p)
    return "Contact updated."


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record or not record.phones:
        raise KeyError

    phones = ", ".join(p.value for p in record.phones)
    return f"{name}'s phones: {phones}"


@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "No contacts found."
    return str(book)


@input_error
def add_birthday(args, book: AddressBook):
    name, bday = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.add_birthday(bday)
    return f"Birthday added for {name}."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record or not record.birthday:
        raise KeyError
    return f"{name}'s birthday: {record.birthday.value}"


@input_error
def birthdays(args, book: AddressBook):
    days = int(args[0]) if args else 7
    upcoming = book.get_upcoming_birthdays(days)
    if not upcoming:
        return "No upcoming birthdays."
    return "\n".join(f"{item['name']}: {item['birthday']}" for item in upcoming)


# -------------------- Парсер команд --------------------
def parse_input(user_input):
    parts = user_input.split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]





# -------------------- Головна функція --------------------
def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ("exit", "close"):
            print("Good bye!")
            break
        elif command == "help":
            print("Available commands: add, change, phone, all, add-birthday, show-birthday, birthdays, exit")

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
