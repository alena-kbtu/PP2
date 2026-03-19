import os
import shutil
shutil.copy("sample.txt", "backup_sample.txt")
print("File copied to backup_sample.txt\n")

if os.path.exists("backup_sample.txt"):
    os.remove("backup_sample.txt")
    print("Backup file deleted safely.")
else:
    print("File does not exist.")