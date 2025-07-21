from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from accounts_library import AccountManager

def run(manager: AccountManager):
    entry_count = manager.get_collection_count()
    while True:
        choices = [Choice(value=row[0], name=row[1], enabled=row[2])
                  for row in manager.get_collection()]

        response = inquirer.checkbox(
            message="collection> ",
            choices=choices,
            transformer=lambda x: f"{len(x)} / {entry_count}",
        ).execute()

        result = [item for item in response]
        manager.tick(result)
        break