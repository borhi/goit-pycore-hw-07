from typing import Callable, Dict

from address_book import AddressBook, Record, RecordNotFoundError


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeError:
            return "Wrong arguments. Check the command format (command help for more information)."
        except ValueError as e:
            return str(e)
        except KeyError as e:
            return e.args[0] if e.args else str(e) 
        except Exception as e:
            return f"Error: {e}"

    return inner


def parse_input(user_input: str) -> tuple:
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def command_handler(func: Callable, contacts: AddressBook) -> Callable:
    @input_error
    def handler(args: list) -> str:
        return func(*args, contacts=contacts)

    return handler


def add_contact(name: str, phone: str, contacts: AddressBook) -> str:
    contact = contacts.find(name)
    if contact:
        contact.add_phone(phone)
        return "Contact updated."
    else:
        contact = Record(name)
        contact.add_phone(phone)
        contacts.add_record(contact)
        return "Contact added."

def change_contact(name: str, phone: str, new_phone: str, contacts: AddressBook) -> str:
    contact = contacts.find(name)
    if contact:
        contact.edit_phone(phone, new_phone)
        return "Contact updated."
    else:
        raise RecordNotFoundError(f"Record '{name}' not found.")

def show_phone(name: str, contacts: AddressBook) -> str:
    contact = contacts.find(name)
    if contact:
        return "\n".join(str(p) for p in contact.phones)
    else:
        raise RecordNotFoundError(f"Record '{name}' not found.")


def show_all(contacts: AddressBook) -> str:
    if not contacts:
        return "No contacts saved."

    return "\n".join(f"{record}" for record in contacts.data.values())

def add_birthday(name: str, birthday: str, contacts: AddressBook) -> str:
    contact = contacts.find(name)
    if contact:
        contact.add_birthday(birthday)
        return "Birthday added."
    else:
        raise RecordNotFoundError(f"Record '{name}' not found.")

def show_birthday(name: str, contacts: AddressBook) -> str:
    contact = contacts.find(name)
    if contact:
        if contact.birthday is None:
            return "Birthday not set."
        return str(contact.birthday)
    else:
        raise RecordNotFoundError(f"Record '{name}' not found.")

def birthdays(contacts: AddressBook) -> str:
    upcoming_birthdays = contacts.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays."
    return "\n".join([f"{p['name']}: {p['congratulation_date']}" for p in upcoming_birthdays])

def help_command() -> str:
    return (
        "Available commands:\n"
        "  add [name] [phone]               - Add a new contact or phone to existing one\n"
        "  change [name] [old] [new]        - Change a phone number\n"
        "  phone [name]                     - Show phone numbers for a contact\n"
        "  all                              - Show all contacts\n"
        "  add-birthday [name] [DD.MM.YYYY] - Add birthday to a contact\n"
        "  show-birthday [name]             - Show birthday for a contact\n"
        "  birthdays                        - Show upcoming birthdays (next 7 days)\n"
        "  hello                            - Get a greeting\n"
        "  help                             - Show this help message\n"
        "  close / exit                     - Exit the program"
    )

def main():
    contacts = AddressBook()
    print("Welcome to the assistant bot!")

    commands: Dict[str, Callable] = {
        "hello": lambda args: "How can I help you?",
        "add": command_handler(add_contact, contacts),
        "change": command_handler(change_contact, contacts),
        "phone": command_handler(show_phone, contacts),
        "all": command_handler(show_all, contacts),
        "add-birthday": command_handler(add_birthday, contacts),
        "show-birthday": command_handler(show_birthday, contacts),
        "birthdays": command_handler(birthdays, contacts),
        "help": lambda args: help_command(),
    }

    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input:
            continue

        command, *args = parse_input(user_input)

        if command in ("close", "exit"):
            print("Good bye!")
            break

        handler = commands.get(command)
        if handler:
            print(handler(args))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
