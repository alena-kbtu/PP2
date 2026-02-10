class Person:
    def __init__(self, fname, lname):
        self.firstname = fname
        self.lastname = lname

    def printname(self):
        print(self.firstname, self.lastname)


class Student(Person):
    def printname(self):
        print("Student:", self.firstname, self.lastname)


x = Student("Mike", "Olsen")
x.printname()