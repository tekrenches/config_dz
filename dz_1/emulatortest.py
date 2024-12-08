import unittest
from unittest.mock import patch, mock_open
from pathlib import Path, WindowsPath
import shutil
import os
from emulator import ls_command, cd_command, cp_command, cal_command, uname_command
import platform
class TestShellEmulator(unittest.TestCase):

    def setUp(self):
        """Создание тестовой структуры виртуальной файловой системы."""
        self.test_dir = Path('\\tmp\\virtual_fs')
        self.test_dir.mkdir(exist_ok=True)
        (self.test_dir / "common.txt").write_text("Content of file 1")
        (self.test_dir / "uncommon.txt").write_text("Content of file 2")
        (self.test_dir / "1").mkdir(exist_ok=True)

    def tearDown(self):
        """Очистка тестовой структуры файловой системы."""
        shutil.rmtree(self.test_dir)

    # Tests for `ls`
    def test_ls_command_list_files(self):
        with patch('builtins.print') as mock_print:
            ls_command(self.test_dir)
            mock_print.assert_any_call(self.test_dir / "common.txt")
            mock_print.assert_any_call(self.test_dir / "uncommon.txt")
            mock_print.assert_any_call(self.test_dir / "1")

    def test_ls_command_empty_dir(self):
        empty_dir = self.test_dir / "empty"
        empty_dir.mkdir()
        with patch('builtins.print') as mock_print:
            ls_command(empty_dir)
            mock_print.assert_not_called()  # Nothing to list

    def test_ls_command_invalid_path(self):
        with patch('builtins.print') as mock_print:
            ls_command("nonexistent_path")
            mock_print.assert_called_once_with("ls: cannot access 'nonexistent_path': No such file or directory")

    # Tests for `cd`
    def test_cd_command_change_directory(self):
        result = cd_command(self.test_dir, "1")
        self.assertEqual(result, str(self.test_dir.resolve() / "1")[2:])

    def test_cd_command_invalid_directory(self):
        with patch('builtins.print') as mock_print:
            result = cd_command(self.test_dir, "invalid_subdir")
            mock_print.assert_called_once_with("cd: invalid_subdir: No such directory")


    def test_cd_command_relative_path(self):
        subdir = self.test_dir / "1"
        result = cd_command(subdir, "..")
        self.assertEqual(result, str(self.test_dir))

    # Tests for `cp`
    def test_cp_command_copy_file(self):
        source = "common.txt"
        destination = "1"
        cp_command(source, destination, self.test_dir)
        self.assertTrue((self.test_dir / destination).exists())

    def test_cp_command_source_not_found(self):
        with patch('builtins.print') as mock_print:
            cp_command("nonexistent.txt", "1", self.test_dir)
            mock_print.assert_called_once_with("cp: cannot stat 'nonexistent.txt': No such file or directory")

    def test_cp_command_copy_directory(self):
        with patch('builtins.print') as mock_print:
            cp_command("1", "1\\2", self.test_dir)
            mock_print.assert_called_once_with("cp: cannot copy '1': Permission denied")

    # Tests for `cal`
    def test_cal_command_current_month(self):
        with patch('builtins.print') as mock_print:
            cal_command()
            self.assertTrue(mock_print.called)

    # Tests for `uname`
    def test_uname_command_output(self):
        with patch('builtins.print') as mock_print:
            uname_command()
            mock_print.assert_called_once_with(platform.system())

    def test_uname_command_multiple_calls(self):
        with patch('builtins.print') as mock_print:
            uname_command()
            uname_command()
            self.assertEqual(mock_print.call_count, 2)

if __name__ == '__main__':
    unittest.main()
