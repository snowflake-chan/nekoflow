from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from accounts_library import AccountManager

class CollectionUI:
    def __init__(self, manager:AccountManager):
        self.manager = manager

        self.current_page = 0
        self.page_count = self.manager.get_collection_count()

    def get_current_page_options(self):
        collection = [Choice(value=row[0], name=row[1], enabled=row[2])
                      for row in self.manager.get_collection(self.current_page)]
        options = []
        if self.current_page > 0:
            options.append(Choice(value="__prev_page__", name="▲ Page up"))
        options.extend(collection)
        if self.current_page < self.page_count - 1:
            options.append(Choice(value="__next_page__", name="▼ Page down"))

        return options

    def run(self, message="collection> "):
        selected = set()

        while True:
            choices = self.get_current_page_options()

            prompt = inquirer.checkbox(
                message=message,
                choices=choices,
                default=selected,
                transformer=lambda result: f"{len(result)} entries selected"
            )

            response = prompt.execute()

            if "__next_page__" in response:
                self.current_page = min(self.current_page + 1, self.page_count - 1)
                selected = selected.intersection(set(response))
                continue
            elif "__prev_page__" in response:
                self.current_page = max(0, self.current_page - 1)
                selected = selected.intersection(set(response))
                continue
            else:
                result = [item for item in response if item not in ("__next_page__", "__prev_page__")]
                self.manager.tick(result)
                break