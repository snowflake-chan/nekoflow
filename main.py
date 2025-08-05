import asyncio
from tqdm.asyncio import tqdm_asyncio
from InquirerPy import inquirer
from accounts_library import AccountManager
from InquirerPy.base.control import Choice
from user import single_request

manager = AccountManager()

async def batch_user_action(method, *args):
    ticked = await manager.get_ticked()
    await getattr(ticked, method)(*args)

async def view_work(work_id, number):
    resp = await tqdm_asyncio.gather(*(single_request(work_id) for _ in range(number)))
    succeeded = resp.count(True)
    print(f"{succeeded} / {number} OK")

action_map = {
    'Like Reply': lambda: asyncio.run(batch_user_action("like_reply", inquirer.number(message='reply id> ').execute())),
    'Report Reply': lambda: asyncio.run(batch_user_action("report_reply", inquirer.number(message='reply id> ').execute())),
    'Like': lambda: asyncio.run(batch_user_action("like_work", inquirer.number(message='work id> ').execute())),
    'Collect': lambda: asyncio.run(batch_user_action("collect_work", inquirer.number(message='work id> ').execute())),
    'Fork': lambda: asyncio.run(batch_user_action("fork_work", inquirer.number(message='work id> ').execute())),
    'Follow User': lambda: asyncio.run(batch_user_action("follow", inquirer.number(message='user id> ').execute())),
    'View': lambda: asyncio.run(view_work(
        inquirer.number(message='work id> ').execute(),
        int(inquirer.number(message='number> ').execute())
    )),
}

if __name__ == '__main__':
    action = 'Collection'
    while True:
        try:
            action = inquirer.select(
                message='nekoflow> ',
                choices=[
                    'Collection',
                    'Add Account',
                    'Work',
                    'Follow User',
                    'Like Reply',
                    'Report Reply',
                    'About',
                    'Exit'
                ],
                default=action
            ).execute()

            if action == 'Collection':
                entry_count = manager.get_collection_count()
                choices = [Choice(value=row[0], name=row[1], enabled=row[2])
                            for row in manager.get_collection()]
                response = inquirer.checkbox(
                    message="collection> ",
                    choices=choices,
                    transformer=lambda x: f"{len(x)} / {entry_count}",
                ).execute()
                manager.tick([item for item in response])

            elif action == 'Add Account':
                identity = inquirer.text(message='identity> ').execute()
                password = inquirer.text(message='password> ').execute()
                asyncio.run(manager.add_account(identity, password))

            elif action == 'Work':
                work_action = inquirer.select(
                    message='work> ',
                    choices=['View', 'Like', 'Collect', 'Fork']
                ).execute()
                action_map[work_action]()

            elif action in action_map:
                action_map[action]()

            elif action == 'About':
                print('nekoflow(R) 2025. All rights reserved.')

            elif action == 'Exit':
                exit(0)

        except KeyboardInterrupt:
            exit(0)