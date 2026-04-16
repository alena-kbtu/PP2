import csv
from connect import get_connection


def insert_from_csv():
    conn = get_connection()
    cur = conn.cursor()

    with open("contacts.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            cur.execute(
                "INSERT INTO contracts (name, phone) VALUES (%s, %s)",
                (row["name"], row["phone"])
            )

    conn.commit()
    cur.close()
    conn.close()
    print("CSV imported")


def insert_from_console():
    name = input("Name: ")
    phone = input("Phone: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO contracts (name, phone) VALUES (%s, %s)",
        (name, phone)
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Added")


def search_by_name():
    name = input("Search name: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM contracts WHERE name ILIKE %s",
        ('%' + name + '%',)
    )

    rows = cur.fetchall()
    for row in rows:
        print(row)

    cur.close()
    conn.close()


def search_by_prefix():
    prefix = input("Phone prefix: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM contracts WHERE phone LIKE %s",
        (prefix + '%',)
    )

    rows = cur.fetchall()
    for row in rows:
        print(row)

    cur.close()
    conn.close()


def update_contact():
    old_phone = input("Old phone: ")
    new_name = input("New name: ")
    new_phone = input("New phone: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE contracts SET name = %s, phone = %s WHERE phone = %s",
        (new_name, new_phone, old_phone)
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Updated")


def delete_contact():
    phone = input("Phone to delete: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM contracts WHERE phone = %s",
        (phone,)
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Deleted")


while True:
    print("\n1 - Import CSV")
    print("2 - Add contact")
    print("3 - Search by name")
    print("4 - Search by phone prefix")
    print("5 - Update contact")
    print("6 - Delete contact")
    print("0 - Exit")

    choice = input("Choose: ")

    if choice == "1":
        insert_from_csv()
    elif choice == "2":
        insert_from_console()
    elif choice == "3":
        search_by_name()
    elif choice == "4":
        search_by_prefix()
    elif choice == "5":
        update_contact()
    elif choice == "6":
        delete_contact()
    elif choice == "0":
        break
    else:
        print("Wrong option")
