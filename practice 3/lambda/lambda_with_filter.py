words = ["apple", "banana", "kiwi", "cherry", "fig"]

# Оставляем слова длиной больше 4
long_words = list(filter(lambda w: len(w) > 4, words))

print(long_words)