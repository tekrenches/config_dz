# import os
import zipfile
import xml.etree.ElementTree as ET
import calendar
import platform
import shutil
import sys
from http.cookiejar import cut_port_re
from pathlib import *

# Функция для загрузки конфигурационного файла (XML)
def load_config(config_path):
    try:
        tree = ET.parse(config_path)
        root = tree.getroot()
        zip_path = root.find('path').text
        return zip_path
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)


def open_zip(zip_path, temp):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp)
    except FileNotFoundError:
        print(f"Error: Zip file '{zip_path}' not found.")
        sys.exit(1)
    except zipfile.BadZipFile:
        print(f"Error: Invalid zip file '{zip_path}'.")
        sys.exit(1)

# Реализация команды ls
def ls_command(current_dir):
    path=Path(current_dir)
    try:
       # for entry in os.listdir(current_dir):
       for entry in path.iterdir():
            print(entry)
    except FileNotFoundError:
        print(f"ls: cannot access '{current_dir}': No such file or directory")

# Реализация команды cd
def cd_command(current_dir, target_dir):
    new_dir=Path(current_dir).joinpath(target_dir).resolve()
    #new_dir = os.path.join(current_dir, target_dir)
    #if os.path.isdir(new_dir):

    if new_dir.is_dir():
        return str(new_dir)[2:]
    else:
        print(f"cd: {target_dir}: No such directory")
        return current_dir

# Реализация команды exit
def exit_command():
    print("Exiting shell emulator.")
    sys.exit(0)

# Реализация команды cal
def cal_command():
    year = calendar.datetime.datetime.now().year
    month = calendar.datetime.datetime.now().month
    print(calendar.month(year, month))

# Реализация команды uname
def uname_command():
    print(platform.system())

# Реализация команды cp
def cp_command(source, destination, current_dir):
    source_path=PurePath(current_dir).joinpath(source)
    destination_path=PurePath(current_dir).joinpath(destination)
  #  source_path = os.path.join(current_dir, source)
   # destination_path = os.path.join(current_dir, destination)
    try:
        shutil.copy(source_path, destination_path)
        print(f"Copied '{source}' to '{destination}'")
    except FileNotFoundError:
        print(f"cp: cannot stat '{source}': No such file or directory")
    except PermissionError:
        print(f"cp: cannot copy '{source}': Permission denied")
    except IsADirectoryError:
        print(f"cp: '{source}' is a directory (not copied)")

# Основной цикл эмулятора оболочки
def shell_emulator(virtual_fs_path):
    current_dir = virtual_fs_path
    print("Starting shell emulator. Type 'exit' to quit.")

    while True:
        # Отображение текущего каталога в prompt
        try:
            user_input = input(f"{current_dir}$ ").strip()
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt detected. Exiting.")
            break

        if not user_input:
            continue

        # Разделение ввода на команду и аргументы
        command_parts = user_input.split()
        command = command_parts[0]
        args = command_parts[1:]

        # Обработка команд
        if command == 'ls':
            ls_command(current_dir)
        elif command == 'cd':
            if args:
                current_dir = cd_command(current_dir, args[0])
            else:
                print("cd: missing argument")
        elif command == 'exit':
            exit_command()
        elif command == 'cal':
            cal_command()
        elif command == 'uname':
            uname_command()
        elif command == 'cp':
            if len(args) < 2:
                print("cp: missing file operand")
            else:
                cp_command(args[0], args[1], current_dir)
        else:
            print(f"{command}: command not found")

# Основная функция
def main():
    config_path = 'config.xml'  # Путь к конфигурационному файлу
    zip_path = load_config(config_path)
    temp = '\\tmp\\virtual_fs'  # Временная директория для виртуальной ФС

    open_zip(zip_path, temp)
    shell_emulator(temp)

if __name__ == "__main__":
    main()
