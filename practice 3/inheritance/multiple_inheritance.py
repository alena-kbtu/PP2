class Person:
    def __init__(self, fname):
        self.firstname = fname

    def show_name(self):
        print(self.firstname)


class Student:
    def __init__(self, year):
        self.year = year

    def show_year(self):
        print(self.year)


class Worker(Person, Student):
    def __init__(self, fname, year):
        Person.__init__(self, fname)
        Student.__init__(self, year)


x = Worker("Mike", 2024)
x.show_name()
x.show_year()