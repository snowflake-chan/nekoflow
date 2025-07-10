from PyInquirer import prompt

from accounts_library import AccountManager

if __name__ == '__main__':
    manager = AccountManager()

    while True:
        try:
            main_list = [
                {
                    'type': 'list',
                    'name': 'action',
                    'message': 'nekoflow',
                    'choices': [
                        'Collection',
                        'Add Account',
                        'About',
                        'Exit'
                    ]
                }
            ]

            action = prompt(main_list)['action']

            if action == 'Collection':
                pass

            elif action == 'Add Account':
                questions = [
                    {
                        'type': 'input',
                        'name': 'identity',
                        'message': 'identity> '
                    },
                    {
                        'type': 'input',
                        'name': 'password',
                        'message': 'password> '
                    }
                ]
                identity, password = prompt(questions).values()
                manager.add_account(identity, password)

            elif action == 'About':
                print('nekoflow(R) 2025. All rights reserved.')

            elif action == 'Exit':
                exit(0)

        except KeyboardInterrupt:
            exit(0)

        except Exception as e:
            print(e)