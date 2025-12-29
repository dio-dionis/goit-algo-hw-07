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
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must consist of 10 digits")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            birthday_date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(birthday_date)
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
            self.phones[self.phones.index(p)] = Phone(new_phone)
        else:
            raise ValueError("Old phone not found")

    def find_phone(self, phone):
        phone_value = phone.value if isinstance(phone, Phone) else phone
        for p in self.phones:
            if p.value == phone_value:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = "; ".join(str(p) for p in self.phones) if self.phones else "N/A"
        birthday_str = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "N/A"
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {birthday_str}"

# -------------------- Адресна книга --------------------
def adjust_for_weekend(bday: date) -> date:
    """Якщо день народження випадає на вихідні, перенести на понеділок"""
    if bday.weekday() == 5:  # субота
        return bday + timedelta(days=2)
    elif bday.weekday() == 6:  # неділя
        return bday + timedelta(days=1)
    return bday

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
    
    

    def get_upcoming_birthdays(self, days=7):
        upcoming = []
        today = date.today()
        for record in self.data.values():
            if not record.birthday:
                continue
            bday = record.birthday.value
            bday_this_year = bday.replace(year=today.year)
            if bday_this_year < today:
                bday_this_year = bday_this_year.replace(year=today.year + 1)
            bday_this_year = adjust_for_weekend(bday_this_year)
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
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if  record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record or not record.phones:
        raise KeyError
    return f"{name}: {record.phones[0].value}"


@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "No contacts found."
    return "\n".join(str(record) for record in book.data.values())


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record or not record.birthday:
        raise KeyError
    return f"{name}: {record.birthday.value.strftime('%d.%m.%Y')}"


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

        if command in ["exit", "close"]:
            print("Good bye!")
            break

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
