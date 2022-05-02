#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
import sys
import logging
from typing import List
import xml.etree.ElementTree as ET


"""
Выполнить индивидуальное задание 2 лабораторной работы 2.19, добавив аннтотации типов.
Выполнить проверку программы с помощью утилиты mypy.
"""

# Класс пользовательского исключения в случае, если введенная
# команда является недопустимой.
class UnknownCommandError(Exception):

    def __init__(self, command, message="Unknown command"):
        self.command = command
        self.message = message
        super(UnknownCommandError, self).__init__(message)

    def __str__(self):
        return f"{self.command} -> {self.message}"


@dataclass(frozen=True)
class Student:
    name: str
    group: str
    grade: str


@dataclass
class Staff:
    students: List[Student] = field(default_factory=lambda: [])
    def add(self, name: str, group: str, grade: str) -> None:
        self.students.append(
            Student(
                name=name,
                group=group,
                grade=grade,
            )
        )
        self.students.sort(key=lambda student: student.name)

    def __str__(self) -> str:
        # Заголовок таблицы.
        table = []
        line = '+-{}-+-{}-+-{}-+-{}-+'.format(
            '-' * 4,
            '-' * 30,
            '-' * 20,
            '-' * 15
        )
        table.append(line)
        table.append(
            '| {:^4} | {:^30} | {:^20} | {:^15} |'.format(
                "No",
                "Ф.И.О.",
                "Группа",
                "Успеваемость"
            )
        )
        table.append(line)
        # Вывести данные о всех сотрудниках.
        for idx, student in enumerate(self.students, 1):
            table.append(
                '| {:>4} | {:<30} | {:<20} | {:>15} |'.format(
                    idx,
                    student.name,
                    student.group,
                    student.grade
                )
            )
        table.append(line)
        return '\n'.join(table)

    def select(self) -> List[Student]:
        count = 0
        result: List[Student] = []
        # Проверить сведения студентов из списка.
        for student in self.students:
            grade = list(map(int, student.grade.split()))
            if sum(grade) / max(len(grade), 1) >= 4.0:
                count += 1
                result.append(student)
        return result


    def load(self, filename: str) -> None:
        with open(filename, "r", encoding="utf-8") as fin:
            xml = fin.read()
        parser = ET.XMLParser(encoding="utf-8")
        tree = ET.fromstring(xml, parser=parser)

        self.students = []
        for student_element in tree:
            name, group, grade = None, None, None

            for element in student_element:
                if element.tag == 'name':
                    name = element.text
                elif element.tag == 'group':
                    group = element.text
                elif element.tag == 'grade':
                    grade = element.text

                if name is not None and group is not None \
                        and grade is not None:
                    self.students.append(
                        Student(
                            name=name,
                            group=group,
                            grade=grade
                        )
                    )

    def save(self, filename: str) -> None:
        root = ET.Element('students')
        for student in self.students:
            student_element = ET.Element('student')
            name_element = ET.SubElement(student_element, 'name')
            name_element.text = student.name
            post_element = ET.SubElement(student_element, 'group')
            post_element.text = str(student.group)
            year_element = ET.SubElement(student_element, 'grade')
            year_element.text = student.grade
            root.append(student_element)
        tree = ET.ElementTree(root)
        with open(filename, "w", encoding="utf-8") as fout:
            tree.write(fout, encoding="utf-8", xml_declaration=True)


if __name__ == '__main__':
    logging.basicConfig(
        filename='students.log',
        level=logging.INFO
    )

    staff = Staff()

    while True:
        try:
            # Запросить команду из терминала.
            command = input(">>> ").lower()
            # Выполнить действие в соответствие с командой.
            if command == 'exit':
                break
            elif command == 'add':
                    # Запросить данные о работнике.
                    name = input("Фамилия и инициалы? ")
                    group = input("Группа? ")
                    grade = input("Оценки ")
                    # Добавить работника.
                    staff.add(name, group, grade)
                    logging.info(
                    f"Добавлен студент: {name}, {group}, "
                    f"с оценками {grade}")
            elif command == 'list':
                    # Вывести список.
                    print(staff)
                    logging.info("Отображен список студентов.")
            elif command.startswith('select '):
                    parts = command.split(maxsplit=1)
                    # Запросить работников.
                    selected = staff.select()
                    # Вывести результаты запроса.
                    if selected:
                        for idx, student in enumerate(selected, 1):
                            print(
                            '{:>4}: {}'.format(idx, student.name)
                            )
                            logging.info(
                            f"Найдено {len(selected)} студентов со "
                            f"средним баллом >=4: {parts[1]}."
                            )
                    else:
                        print("Студентов с оценкой выше 4 не найдены.")
                        logging.warning(
                        f"Студентов со средним баллом более 4: {parts[1]}  не найдены."
                        )
            elif command.startswith('load '):
                    # Разбить команду на части для имени файла.
                    parts = command.split(maxsplit=1)
                    # Загрузить данные из файла.
                    staff.load(parts[1])
                    logging.info(f"Загружены данные из файла {parts[1]}.")
            elif command.startswith('save '):
                    # Разбить команду на части для имени файла.
                    parts = command.split(maxsplit=1)
                    # Сохранить данные в файл.
                    staff.save(parts[1])
                    logging.info(f"Сохранены данные в файл {parts[1]}.")
            elif command == 'help':
                    # Вывести справку о работе с программой.
                    print("Список команд:\n")
                    print("add - добавить студента;")
                    print("list - вывести список студентов;")
                    print("select <1> - запросить студентов со средним баллом >=4;")
                    print("load <имя_файла> - загрузить данные из файла;")
                    print("save <имя_файла> - сохранить данные в файл;")
                    print("help - отобразить справку;")
                    print("exit - завершить работу с программой.")
            else:
                    raise UnknownCommandError(command)
        except Exception as exc:
            logging.error(f"Ошибка: {exc}")
            print(exc, file=sys.stderr)