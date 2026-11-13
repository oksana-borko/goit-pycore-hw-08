
from collections import UserDict
from datetime import date, datetime, timedelta

DATE_FORMAT = "%d.%m.%Y"


class Field:


    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):


    def __init__(self, value: str):
        if not value or not value.strip():
            raise ValueError("Name cannot be empty.")
        super().__init__(value.strip())


class Phone(Field):


    def __init__(self, value: str):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError(f"Invalid phone number '{value}'. Phone must contain exactly 10 digits.")
        super().__init__(value)


class Birthday(Field):


    def __init__(self, value: str):
        try:
            birthday = datetime.strptime(value, DATE_FORMAT).date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        if birthday > date.today():
            raise ValueError("Birthday cannot be in the future.")
        super().__init__(birthday)

    def __str__(self):
        return self.value.strftime(DATE_FORMAT)


class Record:


    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.birthday: Birthday | None = None

    def add_phone(self, phone: str) -> None:
        if self.find_phone(phone):
            raise ValueError(f"Phone {phone} already exists for {self.name}.")
        self.phones.append(Phone(phone))

    def find_phone(self, phone: str) -> Phone | None:
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def remove_phone(self, phone: str) -> None:
        self.phones.remove(self._get_phone(phone))

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        old = self._get_phone(old_phone)

        new = Phone(new_phone)
        self.phones[self.phones.index(old)] = new

    def add_birthday(self, birthday: str) -> None:

        self.birthday = Birthday(birthday)

    def _get_phone(self, phone: str) -> Phone:

        found = self.find_phone(phone)
        if found is None:
            raise ValueError(f"Phone {phone} not found for {self.name}.")
        return found

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones) or "no phones"
        birthday = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones}{birthday}"


class AddressBook(UserDict):


    def add_record(self, record: Record) -> None:
        self.data[record.name.value] = record

    def find(self, name: str) -> Record | None:
        return self.data.get(name)

    def delete(self, name: str) -> None:
        if name not in self.data:
            raise KeyError(f"Contact '{name}' not found.")
        del self.data[name]

    def get_upcoming_birthdays(self, days: int = 7) -> list[dict]:

        today = date.today()
        upcoming = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday = record.birthday.value
            birthday_this_year = self._birthday_in_year(birthday, today.year)
            if birthday_this_year < today:
                birthday_this_year = self._birthday_in_year(birthday, today.year + 1)

            if (birthday_this_year - today).days < days:
                congratulation_date = birthday_this_year

                if congratulation_date.weekday() >= 5:
                    congratulation_date += timedelta(days=7 - congratulation_date.weekday())
                upcoming.append({
                    "name": record.name.value,
                    "congratulation_date": congratulation_date.strftime(DATE_FORMAT),
                })

        upcoming.sort(key=lambda item: datetime.strptime(item["congratulation_date"], DATE_FORMAT))
        return upcoming

    @staticmethod
    def _birthday_in_year(birthday: date, year: int) -> date:

        try:
            return birthday.replace(year=year)
        except ValueError:
            return birthday.replace(year=year, day=28)

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())