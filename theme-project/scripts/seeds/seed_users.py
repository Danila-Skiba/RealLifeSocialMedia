import psycopg2
from faker import Faker

fake = Faker("ru_RU")

DB_CONFIG = {
    'host': 'localhost',
    'database': 'omstu_db',
    'user': 'omstu',
    'password': 'omstu', 
    'port': 5430,
}

def seed_users(count = 100):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    inserted = 0

    while inserted < count:
        email = fake.email()
        password = fake.password(length=12)
        name = fake.name()
        try: 
            cursor.execute(
                "INSERT INTO users (email, password, name) VALUES (%s, %s, %s)",
                (email, password, name)
            )
            inserted += 1
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            continue
        conn.commit()

    cursor.close()
    conn.close()

if __name__ == "__main__":
    seed_users()
