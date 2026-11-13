
import pickle
from pathlib import Path

from address_book import AddressBook


DEFAULT_FILE = Path(__file__).resolve().parent / "addressbook.pkl"


def save_data(book: AddressBook, filename: Path | str = DEFAULT_FILE) -> None:


    path = Path(filename)
    tmp_path = path.with_name(path.name + ".tmp")
    with open(tmp_path, "wb") as f:
        pickle.dump(book, f)
    tmp_path.replace(path)


def load_data(filename: Path | str = DEFAULT_FILE) -> AddressBook:

    try:
        with open(filename, "rb") as f:
            book = pickle.load(f)
    except FileNotFoundError:
        return AddressBook()
    except Exception:
        print("Warning: the data file is damaged or incompatible. Starting with an empty address book.")
        return AddressBook()

    if not isinstance(book, AddressBook):
        print("Warning: the data file does not contain an address book. Starting with an empty one.")
        return AddressBook()
    return book