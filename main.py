
from datetime import datetime
from functools import wraps

from address_book import DATE_FORMAT, AddressBook, Record
from storage import load_data, save_data


def input_error(func):


    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as error:
            return str(error) or "Invalid value."
        except KeyError as error:
            return error.args[0] if error.args else "Contact not found."
        except IndexError:
            return "Enter the argument for the command."

    return inner


def parse_input(user_input: str) -> tuple:
    cmd, *args = user_input.split()
    return cmd.strip().lower(), *args


def get_record(book: AddressBook, name: str) -> Record:

    record = book.find(name)
    if record is None:
        raise KeyError(f"Contact '{name}' not found.")
    return record


def require_args(args: list, count: int, usage: str) -> None:

    if len(args) < count:
        raise ValueError(f"Not enough arguments. Usage: {usage}")



def hello(args, book: AddressBook):
    return "How can I help you?"


@input_error
def add_contact(args, book: AddressBook):
    require_args(args, 2, "add [name] [phone]")
    name, phone, *_ = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."
    record.add_phone(phone)
    return "Contact updated."


@input_error
def change_contact(args, book: AddressBook):
    require_args(args, 3, "change [name] [old phone] [new phone]")
    name, old_phone, new_phone, *_ = args
    get_record(book, name).edit_phone(old_phone, new_phone)
    return "Phone updated."


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = get_record(book, name)
    phones = "; ".join(p.value for p in record.phones) or "no phones"
    return f"{name}: {phones}"


@input_error
def show_all(args, book: AddressBook):
    return str(book) if book else "No contacts saved."


@input_error
def add_birthday(args, book: AddressBook):
    require_args(args, 2, "add-birthday [name] [DD.MM.YYYY]")
    name, birthday, *_ = args
    get_record(book, name).add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = get_record(book, name)
    if record.birthday is None:
        return f"{name} has no birthday set."
    return f"{name}: {record.birthday}"


@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."

    by_date: dict[str, list[str]] = {}
    for item in upcoming:
        by_date.setdefault(item["congratulation_date"], []).append(item["name"])

    lines = []
    for day, names in by_date.items():
        weekday = datetime.strptime(day, DATE_FORMAT).strftime("%A")
        lines.append(f"{weekday} {day}: {', '.join(names)}")
    return "\n".join(lines)


COMMANDS = {
    "hello": hello,
    "add": add_contact,
    "change": change_contact,
    "phone": show_phone,
    "all": show_all,
    "add-birthday": add_birthday,
    "show-birthday": show_birthday,
    "birthdays": birthdays,
}

EXIT_COMMANDS = ("close", "exit")


def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    try:
        while True:
            user_input = input("Enter a command: ")
            if not user_input.strip():
                continue

            command, *args = parse_input(user_input)

            if command in EXIT_COMMANDS:
                print("Good bye!")
                break

            handler = COMMANDS.get(command)
            print(handler(args, book) if handler else "Invalid command.")
    except (KeyboardInterrupt, EOFError):

        print("\nGood bye!")
    finally:
        save_data(book)


if __name__ == "__main__":
    main()
