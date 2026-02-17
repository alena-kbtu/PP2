def square_generator(N):
    for i in range(N + 1):
        yield i * i


def even_numbers(n):
    for i in range(n + 1):
        if i % 2 == 0:
            yield i


def divisible_by_3_and_4(n):
    for i in range(n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i


def squares(a, b):
    for i in range(a, b + 1):
        yield i * i


def countdown(n):
    while n >= 0:
        yield n
        n -= 1


N = int(input())
for value in square_generator(N):
    print(value, end=" ")
print()

n = int(input())
print(",".join(str(x) for x in even_numbers(n)))

n = int(input())
for value in divisible_by_3_and_4(n):
    print(value, end=" ")
print()

a = int(input())
b = int(input())
for value in squares(a, b):
    print(value, end=" ")
print()

n = int(input())
for value in countdown(n):
    print(value, end=" ")
print()
