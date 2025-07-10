from InquirerPy import inquirer

from accounts_library import AccountManager

if __name__ == '__main__':
    manager = AccountManager()

    while True:
        try:
            action = inquirer.select(
                message='nekoflow',
                choices=[
                    'Collection',
                    'Add Account',
                    'About',
                    'Exit'
                ],
                default='Collection'
            ).execute()

            if action == 'Collection':
                collection = manager.get_collection()
                inquirer.checkbox(
                    message=f'collection> 1 / {collection["page_count"]}',
                    choices=collection["choices"]
                ).execute()

            elif action == 'Add Account':
                identity = inquirer.text(message='identity> ').execute()
                password = inquirer.text(message='password> ').execute()
                manager.add_account(identity, password)

            elif action == 'About':
                print('nekoflow(R) 2025. All rights reserved.')

            elif action == 'Exit':
                exit(0)

        except KeyboardInterrupt:
            exit(0)

        except Exception as e:
            print(e)