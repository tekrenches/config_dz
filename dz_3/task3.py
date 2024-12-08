import re
import json
import argparse

# Регулярные выражения для элементов языка
COMMENT_REGEX = r"^\s*\*.*$"
DICT_START_REGEX = r"^\s*@{\s*$"
DICT_END_REGEX = r"^\s*}\s*$"
ASSIGNMENT_REGEX = r"^\s*([a-zA-Z][_a-zA-Z0-9]*)\s*=\s*(.+);\s*$"
LET_REGEX = r"^\s*let\s+([a-zA-Z][_a-zA-Z0-9]*)\s*=\s*(.+)$"
CONST_USE_REGEX = r"\$\(([a-zA-Z][_a-zA-Z0-9]*)\)"

class ConfigParser:
    def __init__(self):
        self.constants = {}

    def parse(self, lines):
        result = {}
        stack = [result]
        for i, line in enumerate(lines, start=1):
            line = line.strip()
            if re.match(COMMENT_REGEX, line):
                continue  # Пропускаем комментарии
            elif re.match(DICT_START_REGEX, line):
                new_dict = {}
                stack[-1].setdefault('nested_dicts', []).append(new_dict)
                stack.append(new_dict)
            elif re.match(DICT_END_REGEX, line):
                if len(stack) <= 1:
                    raise SyntaxError(f"Unexpected '}}' at line {i}")
                stack.pop()
            elif match := re.match(ASSIGNMENT_REGEX, line):
                key, value = match.groups()
                value = self._evaluate_constants(value, i)
                stack[-1][key] = self._parse_value(value)
            elif match := re.match(LET_REGEX, line):
                key, value = match.groups()
                self.constants[key] = self._evaluate_constants(value, i)
            elif line:
                raise SyntaxError(f"Invalid syntax at line {i}: {line}")
        if len(stack) != 1:
            raise SyntaxError("Mismatched braces in configuration")
        return result

    def _evaluate_constants(self, value, line_num):
        def replacer(match):
            const_name = match.group(1)
            if const_name not in self.constants:
                raise SyntaxError(f"Undefined constant '{const_name}' at line {line_num}")
            return self.constants[const_name]
        return re.sub(CONST_USE_REGEX, replacer, value)

    def _parse_value(self, value):
        value = value.strip()
        if value.isdigit():
            return int(value)
        elif re.match(DICT_START_REGEX, value):
            raise ValueError("Nested dictionaries must be explicitly opened with @{")
        return value
def main():
    parser = argparse.ArgumentParser(description="Учебный конфигурационный парсер.")
    parser.add_argument("input_file", help="Путь к входному файлу конфигурации")
    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as file:
            lines = file.readlines()
        config_parser = ConfigParser()
        result = config_parser.parse(lines)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        exit(1)

if __name__ == "__main__":
    main()
