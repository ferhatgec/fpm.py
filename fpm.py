# MIT License
#
# Copyright (c) 2021 Ferhat Geçdoğan All Rights Reserved.
# Distributed under the terms of the MIT License.
#

# Fpm[dot]Py
#   Python3 implementation of Fegeya Package Manager (executable)
#
#   github.com/ferhatgec/fpm.py
#


from pathlib import Path

default_fpi_repository = 'https://github.com/ferhatgec/repository.git'
default_directory = '/etc/fpm'

installed = '✅'
uninstalled = '❎'


class Fpm:
    def __init__(self):
        self.app_name: str = ''
        self.app_desc: str = ''
        self.app_author: str = ''
        self.app_license: str = ''
        self.app_exec: str = ''
        self.app_repo: str = ''
        self.app_folder: str = ''
        self.app_build_instruction: str = ''

    @staticmethod
    def is_exists(data):
        print(f'{data} already installed!\n'
              'Would you like to run it? (y/n) : ', end='')

    @staticmethod
    def is_not_exists(data):
        print(f'{data} is not installed.\n'
              f'Do you want to install {data}? (y/N) : ', end='')

    @staticmethod
    def is_not_super_user(data):
        print(f'Use {data} as super user.')

    @staticmethod
    def is_not_found(data):
        print(f'{data} not found. Aborted.')

    @staticmethod
    def cannot_be_removed(data):
        print(f'Really? {data} is not installed. Cannot be removed.')

    @staticmethod
    def uninstall(data):
        print(f'Do you want to uninstall {data}? (y/n) : ', end='')

    def what_is_this(self, arg: str, package: str):
        if arg == '--i' or arg == '--install':
            self.install_function(package)
        elif arg == '--uni' or arg == '--uninstall':
            self.uninstall_function(package)
        elif arg == '--info':
            self.info_function(package)
        elif arg == '--upd' or arg == '--update':
            self.update_package_list(package)
        else:
            self.help_function()

    def install(self,
                name: str,
                repository: str,
                object: str,
                folder: str,
                uninstall: int):
        if not Path('/bin/{object}'.format(object=object)).exists():
            if uninstall == 1:
                self.cannot_be_removed(name)
            else:
                self.is_not_exists(name)
                character = input()

                if character.lower() == 'y':
                    from os import chdir, getenv
                    if Path('/usr/bin/git').exists():
                        chdir(getenv('HOME'))
                        from subprocess import run, DEVNULL
                        run(['git', 'clone', repository], stdout=DEVNULL)
                        path = '{home}/{folder}'.format(home=getenv('HOME'), folder=folder)
                        chdir(path)

                        if Path('/usr/bin/sudo').exists():
                            if len(self.app_build_instruction) > 0:
                                for line in self.app_build_instruction.splitlines():
                                    run(line.split(' '), stdout=DEVNULL)
                            else:
                                run(['sudo', 'sh', 'install.sh'], stdout=DEVNULL)

                            if Path(f'/bin/{object}').exists() or Path(f'/usr/bin/{object}').exists():
                                print('Installed!')
                            else:
                                print('Could not install.')

                        print('Cleaning')

                        [f.unlink()
                         for f in Path(path).glob('*') if f.is_file()]
        else:
            if uninstall == 1:
                self.uninstall(name)
                character = input()
                if character.lower() == 'y':
                    Path(f'/bin/{object}').unlink()
                    if not Path(f'/bin/{object}').exists():
                        print('Removed.')
                    else:
                        print('Could not remove.')
                else:
                    print('Aborted.')
            else:
                self.is_exists(name)
                character = input()
                if character.lower() == 'y':
                    from subprocess import run
                    run([object])
                else:
                    print('Aborted.')

    @staticmethod
    def check_installed(name: str,
                        data: str,
                        object: str):
        if Path(f'/bin/{object}').exists():
            print(f'{installed}', '\x1b[1;32m', name,
                  '\x1b[0;95m', f'({data})')
        else:
            print(f'{uninstalled}', '\x1b[1;32m', name,
                  '\x1b[0;92m', f'({data})')

    @staticmethod
    def help_function():
        print('Fegeya Package Manager (fpm)\n'
              'Usage: fpm [--i --install] [--uni --uninstall] [--info] [--update] package')

    def install_function(self, arg: str):
        print('Checking.')
        if not Path(F'{default_directory}/packages/').exists():
            self.fetch_repository_data(default_fpi_repository)

        self.parse_repository_file(arg)
        self.install(self.app_name,
                     self.app_repo,
                     self.app_exec,
                     self.app_folder, 0)

    def uninstall_function(self, arg: str):
        print('Checking.')
        if not Path(f'{default_directory}/packages/').exists():
            self.fetch_repository_data(default_fpi_repository)

        self.parse_repository_file(arg)
        self.install(self.app_name,
                     self.app_repo,
                     self.app_exec,
                     self.app_folder, 1)

    def info_function(self, arg: str):
        if not Path(f'{default_directory}/packages/').exists():
            self.fetch_repository_data(default_fpi_repository)

        self.parse_repository_file(arg)
        self.info()

    def info(self):
        print(f'App       : {self.app_name}\n'
              f'Desc      : {self.app_desc}\n'
              f'Author    : {self.app_author}\n'
              f'License   : {self.app_license}\n'
              f'File      : {self.app_exec}\n'
              f'Repository: {self.app_repo}')

    def update_package_list(self, package: str):
        if not Path(f'{default_directory}/packages/').exists():
            print('Fetching latest package list.')
            self.fetch_repository_data(default_fpi_repository)
        else:
            print('Is this ok? (y/N) : ')
            ok = input()[0]
            if package == 'repository' or package == 'all':
                if ok.lower() == 'y':
                    [f.unlink() for f in Path(f'{default_directory}/').glob('*') if f.is_file()]
                    self.fetch_repository_data(default_fpi_repository)
            else:
                print('Aborted.')

    @staticmethod
    def fetch_repository_data(repository: str):
        if not Path('/etc/fpm').exists():
            from subprocess import run, DEVNULL
            run(['git', 'clone', repository, '/etc/fpm'], stdout=DEVNULL)

    def parse_repository_file(self, arg: str):
        if Path(f'/etc/fpm/packages/{arg}.repo').exists():
            self.init_parser(f'/etc/fpm/packages/{arg}.repo')

    def init_parser(self, path: str):
        self.app_name = self.get_line_of(path, 'NAME=')
        self.app_desc = self.get_line_of(path, 'DESC=')
        self.app_author = self.get_line_of(path, 'AUTHOR=')
        self.app_license = self.get_line_of(path, 'LICENSE=')
        self.app_exec = self.get_line_of(path, 'EXEC=')
        self.app_repo = self.get_line_of(path, 'REPOSITORY=')
        self.app_folder = self.get_line_of(path, 'REPOSITORY_FOLDER=')
        self.app_build_instruction = self.get_build_recipe(path)

        print(self.app_name)

    @staticmethod
    def get_line_of(file: str, substring: str):
        with open(file) as file:
            for line in file:
                if f'{substring}' in line:
                    return line.replace(f'{substring}', '')[:-1]

    @staticmethod
    def get_build_recipe(file: str):
        is_recipe = False
        recipe: str = ''
        with open(file) as file:
            for line in file:
                if is_recipe:
                    if 'instruction <' in line:
                        is_recipe = False
                        return recipe

                    recipe += line.strip()
                    continue

                if 'instruction()' in line:
                    is_recipe = True

        return ''


init = Fpm()
from sys import argv

if len(argv) < 3:
    init.help_function()
    exit(1)

init.what_is_this(argv[1], argv[2])
