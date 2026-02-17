from datetime import datetime, timedelta


current_date = datetime.now()
new_date = current_date - timedelta(days=5)
print(new_date)



today = datetime.now().date()
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)

print(yesterday)
print(today)
print(tomorrow)



now = datetime.now()
without_microseconds = now.replace(microsecond=0)
print(without_microseconds)




date1 = datetime(2025, 1, 1, 12, 0, 0)
date2 = datetime(2025, 1, 2, 12, 0, 0)

difference = date2 - date1
print(int(difference.total_seconds()))
