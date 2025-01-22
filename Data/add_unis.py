from scholarly import scholarly
import db_utils

def add_uni(uni, city, country, conn):
    search_query = scholarly.search_org(uni)
    print(search_query)
    try:
        sql_statement = "INSERT INTO universities (uni_id, name, city, country) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING"
        params = ("GS"+search_query[0]['id'], search_query[0]['Organization'], city, country)
        db_utils.execute_psql_statement(conn,sql_statement, params)
    except Exception as e:
        print(f"Error inserting university: {e}")

if __name__ == "__main__":
    # Example usage
    conn = db_utils.create_connection()
    add_uni("Boston University","Boston", "United States of America", conn)
    if conn:
        conn.close()
