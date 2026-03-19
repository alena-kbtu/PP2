names = ["Alena", "Bob", "Charlie"]

print("enumerate():")
for i, name in enumerate(names):
    print(i, name)

numbers = [1, 2, 3]

print("\nzip():")
for n, name in zip(numbers, names):
    print(n, name)