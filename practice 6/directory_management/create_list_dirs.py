import os

os.makedirs("main_folder/sub_folder", exist_ok=True)
print("Nested directories created.")

print("\nList of files and folders:")
print(os.listdir())

print("\nCurrent directory:")
print(os.getcwd())