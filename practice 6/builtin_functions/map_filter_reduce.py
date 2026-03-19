from functools import reduce

nums = [1, 2, 3, 4, 5]

mapped = list(map(lambda x: x * 2, nums))
print("map():", mapped)

filtered = list(filter(lambda x: x % 2 == 0, nums))
print("filter():", filtered)

reduced = reduce(lambda x, y: x + y, nums)
print("reduce():", reduced)