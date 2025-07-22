import asyncio
from tqdm.asyncio import tqdm_asyncio

from InquirerPy import inquirer

from accounts_library import AccountManager
from InquirerPy.base.control import Choice

from user import single_request

async def like_reply(reply_id):
    ticked = await manager.get_ticked()
    await ticked.like_reply(reply_id)

async def report_reply(reply_id):
    ticked = await manager.get_ticked()
    await ticked.report_reply(reply_id)

async def like_work(work_id):
    ticked = await manager.get_ticked()
    await ticked.like_work(work_id)

async def collect_work(work_id):
    ticked = await manager.get_ticked()
    await ticked.collect_work(work_id)

async def fork_work(work_id):
    ticked = await manager.get_ticked()
    await ticked.fork_work(work_id)

async def follow_user(user_id):
    ticked = await manager.get_ticked()
    await ticked.follow(user_id)

async def activate_work(work_id, number):
    await tqdm_asyncio.gather(*(single_request(work_id) for _ in range(number)))

if __name__ == '__main__':
    manager = AccountManager()

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
            elif action == 'Work':
                work_id = inquirer.number(message='work id> ').execute()
                work_action = inquirer.select(
                    message='work> ',
                    choices=[
                        'Activate',
                        'Like',
                        'Collect',
                        'Fork'
                    ]
                ).execute()
                if work_action == 'Activate':
                    number = inquirer.number(message='number> ').execute()
                    asyncio.run(activate_work(work_id, int(number)))
                elif work_action == 'Like':
                    asyncio.run(like_work(work_id))
                elif work_action == 'Collect':
                    asyncio.run(collect_work(work_id))
                elif work_action == 'Fork':
                    asyncio.run(fork_work(work_id))
            elif action == 'Follow User':
                user_id = inquirer.number(message='user id> ').execute()
                asyncio.run(follow_user(user_id))
            elif action == 'Like Reply':
                reply_id = inquirer.number(message='reply id> ').execute()
                asyncio.run(like_reply(reply_id))

            elif action == 'Report Reply':
                reply_id = inquirer.number(message='reply id> ').execute()
                asyncio.run(report_reply(reply_id))

            elif action == 'About':
                print('nekoflow(R) 2025. All rights reserved.')

            elif action == 'Exit':
                exit(0)

        except KeyboardInterrupt:
            exit(0)