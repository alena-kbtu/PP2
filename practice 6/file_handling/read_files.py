import os
import shutil

with open("sample.txt", "a") as f:
    f.write("New line added\n")

print("After appending:")
with open("sample.txt", "r") as f:
    print(f.read())