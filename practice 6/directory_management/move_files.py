import os
import shutil

print("Searching for .txt files:")
for file in os.listdir():
    if file.endswith(".txt"):
        print(file)

# Copy file to subfolder
shutil.copy("info.txt", "main_folder/info_copy.txt")
print("\nFile copied to main_folder.")

# Move file to nested folder
shutil.move("info.txt", "main_folder/sub_folder/info.txt")
print("File moved to sub_folder.")