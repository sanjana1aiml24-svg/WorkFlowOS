import sqlite3

DB = "workflowos_crm.db"


def update_customer(name, email, request, attachment, status):

    connection = sqlite3.connect(DB)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            request TEXT,
            attachment TEXT,
            status TEXT
        )
    """)

    # Check whether customer already exists
    cursor.execute(
        "SELECT id FROM customers WHERE email = ?",
        (email,)
    )

    existing = cursor.fetchone()

    if existing:

        customer_id = existing[0]

        cursor.execute("""
            UPDATE customers
            SET name = ?,
                request = ?,
                attachment = ?,
                status = ?
            WHERE id = ?
        """, (
            name,
            request,
            attachment,
            status,
            customer_id
        ))

    else:

        cursor.execute("""
            INSERT INTO customers
            (name, email, request, attachment, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            email,
            request,
            attachment,
            status
        ))

        customer_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return customer_id


def show_customers():

    connection = sqlite3.connect(DB)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    print("\n===== WorkFlowOS CRM =====")

    for customer in customers:
        print(customer)

    connection.close()


if __name__ == "__main__":
    show_customers()