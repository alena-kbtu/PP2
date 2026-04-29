import csv
import json
import psycopg2
from connect import connect

def add_contact():
    name = input("Name: ")
    email = input("Email: ")
    birthday = input("Birthday (YYYY-MM-DD): ")
    group_name = input("Group (Family/Work/Friend/Other): ")
    phone = input("Phone: ")
    phone_type = input("Phone type (home/work/mobile): ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO groups (name)
        VALUES (%s)
        ON CONFLICT (name) DO NOTHING
    """, (group_name,))

    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    group_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO contacts (name, email, birthday, group_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (name, email, birthday, group_id))

    contact_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO phones (contact_id, phone, type)
        VALUES (%s, %s, %s)
    """, (contact_id, phone, phone_type))

    conn.commit()
    cur.close()
    conn.close()

    print("Contact added successfully!")


def add_phone_to_contact():
    name = input("Contact name: ")
    phone = input("New phone: ")
    phone_type = input("Phone type (home/work/mobile): ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))

    conn.commit()
    cur.close()
    conn.close()

    print("Phone added!")


def move_contact_to_group():
    name = input("Contact name: ")
    group_name = input("New group: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("CALL move_to_group(%s, %s)", (name, group_name))

    conn.commit()
    cur.close()
    conn.close()

    print("Contact moved to group!")


def show_all_contacts():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            c.id,
            c.name,
            c.email,
            c.birthday,
            g.name,
            p.phone,
            p.type,
            c.created_at
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        ORDER BY c.id
    """)

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def filter_by_group():
    group_name = input("Enter group name: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.name, c.email, c.birthday, g.name, p.phone, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        WHERE g.name ILIKE %s
    """, (group_name,))

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def search_by_email():
    email = input("Search email: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.name, c.email, c.birthday, g.name, p.phone, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        WHERE c.email ILIKE %s
    """, ('%' + email + '%',))

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def search_all_fields():
    query = input("Search: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_contacts(%s)", (query,))

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def sort_contacts():
    print("1. Sort by name")
    print("2. Sort by birthday")
    print("3. Sort by date added")

    choice = input("Choose: ")

    if choice == "1":
        order_by = "c.name"
    elif choice == "2":
        order_by = "c.birthday"
    elif choice == "3":
        order_by = "c.created_at"
    else:
        print("Wrong choice")
        return

    conn = connect()
    cur = conn.cursor()

    cur.execute(f"""
        SELECT c.name, c.email, c.birthday, g.name, p.phone, p.type, c.created_at
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        ORDER BY {order_by}
    """)

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def pagination():
    limit = 5
    page = 0

    conn = connect()
    cur = conn.cursor()

    while True:
        offset = page * limit

        cur.execute("""
            SELECT c.id, c.name, c.email, c.birthday, g.name
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
            ORDER BY c.id
            LIMIT %s OFFSET %s
        """, (limit, offset))

        rows = cur.fetchall()

        print("\n--- PAGE", page + 1, "---")

        if not rows:
            print("No contacts on this page.")
        else:
            for row in rows:
                print(row)

        command = input("next / prev / quit: ")

        if command == "next":
            page += 1
        elif command == "prev":
            if page > 0:
                page -= 1
            else:
                print("You are already on the first page.")
        elif command == "quit":
            break
        else:
            print("Wrong command.")

    cur.close()
    conn.close()


def export_to_json():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            c.id,
            c.name,
            c.email,
            c.birthday,
            g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY c.id
    """)

    contacts = cur.fetchall()

    data = []

    for contact in contacts:
        contact_id = contact[0]

        cur.execute("""
            SELECT phone, type
            FROM phones
            WHERE contact_id = %s
        """, (contact_id,))

        phones = cur.fetchall()

        data.append({
            "name": contact[1],
            "email": contact[2],
            "birthday": str(contact[3]),
            "group": contact[4],
            "phones": [
                {
                    "phone": p[0],
                    "type": p[1]
                }
                for p in phones
            ]
        })

    with open("exported_contacts.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    cur.close()
    conn.close()

    print("Contacts exported to exported_contacts.json")


def import_from_json():
    filename = input("JSON filename: ")

    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    conn = connect()
    cur = conn.cursor()

    for item in data:
        name = item["name"]

        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        existing = cur.fetchone()

        if existing:
            answer = input(f"{name} already exists. skip or overwrite? ")

            if answer == "skip":
                continue
            elif answer == "overwrite":
                cur.execute("DELETE FROM contacts WHERE name = %s", (name,))
            else:
                print("Wrong answer, skipped.")
                continue

        group_name = item["group"]

        cur.execute("""
            INSERT INTO groups (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING
        """, (group_name,))

        cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
        group_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO contacts (name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (item["name"], item["email"], item["birthday"], group_id))

        contact_id = cur.fetchone()[0]

        for phone in item["phones"]:
            cur.execute("""
                INSERT INTO phones (contact_id, phone, type)
                VALUES (%s, %s, %s)
            """, (contact_id, phone["phone"], phone["type"]))

    conn.commit()
    cur.close()
    conn.close()

    print("JSON imported successfully!")


def import_from_csv():
    filename = input("CSV filename: ")

    conn = connect()
    cur = conn.cursor()

    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            name = row["name"]
            email = row["email"]
            birthday = row["birthday"]
            group_name = row["group"]
            phone = row["phone"]
            phone_type = row["type"]

            cur.execute("""
                INSERT INTO groups (name)
                VALUES (%s)
                ON CONFLICT (name) DO NOTHING
            """, (group_name,))

            cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
            group_id = cur.fetchone()[0]

            cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
            existing = cur.fetchone()

            if existing:
                contact_id = existing[0]
            else:
                cur.execute("""
                    INSERT INTO contacts (name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (name, email, birthday, group_id))

                contact_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO phones (contact_id, phone, type)
                VALUES (%s, %s, %s)
            """, (contact_id, phone, phone_type))

    conn.commit()
    cur.close()
    conn.close()

    print("CSV imported successfully!")


def delete_contact():
    name = input("Enter contact name to delete: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("DELETE FROM contacts WHERE name = %s", (name,))

    conn.commit()
    cur.close()
    conn.close()

    print("Contact deleted!")


def menu():
    while True:
        print("\n========== PHONEBOOK MENU ==========")
        print("1. Add contact")
        print("2. Add phone to contact")
        print("3. Move contact to group")
        print("4. Show all contacts")
        print("5. Filter by group")
        print("6. Search by email")
        print("7. Search all fields")
        print("8. Sort contacts")
        print("9. Pagination")
        print("10. Export to JSON")
        print("11. Import from JSON")
        print("12. Import from CSV")
        print("13. Delete contact")
        print("0. Exit")

        choice = input("Choose option: ")

        if choice == "1":
            add_contact()
        elif choice == "2":
            add_phone_to_contact()
        elif choice == "3":
            move_contact_to_group()
        elif choice == "4":
            show_all_contacts()
        elif choice == "5":
            filter_by_group()
        elif choice == "6":
            search_by_email()
        elif choice == "7":
            search_all_fields()
        elif choice == "8":
            sort_contacts()
        elif choice == "9":
            pagination()
        elif choice == "10":
            export_to_json()
        elif choice == "11":
            import_from_json()
        elif choice == "12":
            import_from_csv()
        elif choice == "13":
            delete_contact()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Wrong option. Try again.")


if __name__ == "__main__":
    menu()