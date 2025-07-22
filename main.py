import asyncio

from InquirerPy import inquirer

from accounts_library import AccountManager
from InquirerPy.base.control import Choice


async def like_reply():
    ticked = await manager.get_ticked()
    await ticked.like_reply(id)

async def report_reply():
    ticked = await manager.get_ticked()
    await ticked.report_reply(id)

if __name__ == '__main__':
    manager = AccountManager()

    action = 'Collection'

    while True:
        try:
            action = inquirer.select(
                message='nekoflow',
                choices=[
                    'Collection',
                    'Add Account',
                    'Like Reply',
                    'Report Reply',
                    'About',
                    'Exit'
                ],
                default=action
            ).execute()

            if action == 'Collection':
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

            elif action == 'Add Account':
                identity = inquirer.text(message='identity> ').execute()
                password = inquirer.text(message='password> ').execute()
                asyncio.run(manager.add_account(identity, password))

            elif action == 'Like Reply':
                id = inquirer.number(message='reply id> ').execute()
                asyncio.run(like_reply())

            elif action == 'Report Reply':
                id = inquirer.number(message='reply id> ').execute()
                asyncio.run(report_reply())

            elif action == 'About':
                print('nekoflow(R) 2025. All rights reserved.')

            elif action == 'Exit':
                exit(0)

        except KeyboardInterrupt:
            exit(0)