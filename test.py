from database import get_db_connection

if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        print("✅ Successfully connected to the Heritage Hub database!")
        cursor = conn.cursor()

        # Test: Admin user fetch karke dekhte hain
        cursor.execute("SELECT name, role FROM users WHERE email = 'admin@heritagehub.com'")
        admin = cursor.fetchone()
        if admin:
            print(f"👤 Found User: {admin[0]} | Role: {admin[1]}")
        else:
            print("⚠️ Connected, but Admin user not found. Did you run the SQL commands?")

        cursor.close()
        conn.close()
    else:
        print("❌ Failed to connect.")