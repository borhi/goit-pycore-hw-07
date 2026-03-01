from collections import UserDict
from datetime import datetime, timedelta


class PhoneValidationError(ValueError):
    pass


class RecordNotFoundError(KeyError):
    pass


class PhoneNotFoundError(KeyError):
    pass


class BirthdayValidationError(ValueError):
    pass


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not value:
            raise ValueError("Name must not be empty.")
        self._value = value


class Phone(Field):
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, str) or len(value) != 10 or not value.isdigit():
            raise PhoneValidationError("Phone number must be 10 digits.")
        self._value = value

    def __str__(self):
        return self.value

class Birthday(Field):
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        try:
            self._value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise BirthdayValidationError("Invalid date format. Use DD.MM.YYYY.")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise PhoneNotFoundError(f"Phone {old_phone} not found.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        birthday = self.birthday if self.birthday else 'None'
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        if name not in self.data:
            return None
        return self.data[name]

    def delete(self, name):
        if name not in self.data:
            raise RecordNotFoundError(f"Record '{name}' not found.")
        del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []
        
        for record in self.data.values():
            if record.birthday is None:
                continue

            try:
                birthday_this_year = record.birthday.value.replace(year=today.year)
            except (ValueError) as e:
                print(f"Warning: Skipping user '{record.name.value}' due to invalid date: {e}")
                print()
                continue
            
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)
            
            days_until_birthday = (birthday_this_year - today).days
            
            if 0 <= days_until_birthday < 7:
                congratulation_date = birthday_this_year
                
                weekday = congratulation_date.weekday()

                if weekday > 4:
                    congratulation_date += timedelta(days=7-weekday)
                
                upcoming.append({
                    "name": record.name.value,
                    "congratulation_date": congratulation_date.strftime("%d.%m.%Y")
                })
        
        return upcoming


if __name__ == "__main__":
    book = AddressBook()

    john_record = Record("John")
    try:
        john_record.add_phone("1234567890")
    except PhoneValidationError as e:
        print(f"PhoneValidationError: {e}")

    try:
        john_record.add_phone("5555555555")
    except PhoneValidationError as e:
        print(f"PhoneValidationError: {e}")

    book.add_record(john_record)

    jane_record = Record("Jane")
    try:
        jane_record.add_phone("9876543210")
    except PhoneValidationError as e:
        print(f"PhoneValidationError: {e}")

    book.add_record(jane_record)

    try:
        john = book.find("John")
    except RecordNotFoundError as e:
        print(f"RecordNotFoundError: {e}")
    else:
        try:
            john.edit_phone("1234567890", "1112223333")
        except PhoneNotFoundError as e:
            print(f"PhoneNotFoundError: {e}")
        else:
            print(john)
            found_phone = john.find_phone("5555555555")
            print(f"{john.name}: {found_phone}")

        try:
            john.add_birthday("03.03.2000")
        except BirthdayValidationError as e:
            print(f"BirthdayValidationError: {e}")

        try:
            john.add_birthday("wdsdsdsdsd")
        except BirthdayValidationError as e:
            print(f"BirthdayValidationError: {e}")

    for name, record in book.data.items():
        print(record)

    print(book.get_upcoming_birthdays())

    try:
        book.delete("Jane")
    except RecordNotFoundError as e:
        print(f"RecordNotFoundError: {e}")

    try:
        bad_record = Record("Bad")
        bad_record.add_phone("12345")
    except PhoneValidationError as e:
        print(f"PhoneValidationError: {e}")

    try:
        book.find("NonExistent")
    except RecordNotFoundError as e:
        print(f"RecordNotFoundError: {e}")

    try:
        john.edit_phone("0000000000", "9999999999")
    except PhoneNotFoundError as e:
        print(f"PhoneNotFoundError: {e}")
