from scholarly import scholarly
import db_utils


def insert_person(val, uni_id, conn):
    """Insert or update a person in the database."""
    title = 'professor' if val.get('citedby', 0) > 10 else 'scholar'
    sql_statement = """
        INSERT INTO people (id, uni_id, title, name, photo) 
        VALUES (%s, %s, %s, %s, %s) 
        ON CONFLICT (id) DO UPDATE 
        SET uni_id = EXCLUDED.uni_id, 
            title = EXCLUDED.title, 
            name = EXCLUDED.name, 
            photo = EXCLUDED.photo
    """
    params = (f"GS{val['scholar_id']}", f"GS{uni_id}", title, val['name'], val['url_picture'])
    try:
        db_utils.execute_psql_statement(conn, sql_statement, params)
    except Exception as e:
        print(f"Error inserting/updating person '{val['name']}': {e}")


def insert_research_area(research_area, conn):
    """Insert a research area into the database."""
    sql_statement = """
        INSERT INTO research_areas (area) 
        VALUES (%s) 
        ON CONFLICT DO NOTHING
    """
    try:
        db_utils.execute_psql_statement(conn, sql_statement, (research_area.lower(),))
    except Exception as e:
        print(f"Error inserting research area '{research_area}': {e}")


def insert_people_research_area(scholar_id, research_area, conn):
    """Link a person to a research area in the bridge table."""
    sql_statement = """
        INSERT INTO people_research_areas (id, area) 
        VALUES (%s, %s) 
        ON CONFLICT DO NOTHING
    """
    try:
        db_utils.execute_psql_statement(conn, sql_statement, (f"GS{scholar_id}", research_area.lower()))
    except Exception as e:
        print(f"Error linking person to research area '{research_area}': {e}")


def add_people(uni_id, conn):
    """Fetch authors by organization and populate the database."""
    try:
        search_query = scholarly.search_author_by_organization(uni_id)
        for val in search_query:
            insert_person(val, uni_id, conn)
            
            # Process research interests
            for research_area in val.get('interests', []):
                if research_area:
                    insert_research_area(research_area, conn)
                    insert_people_research_area(val['scholar_id'], research_area, conn)
    except Exception as e:
        print(f"Error in add_people: {e}")


if __name__ == "__main__":
    # Example usage
    try:
        conn = db_utils.create_connection()
        add_people("18405750730531958119", conn)
    finally:
        if conn:
            conn.close()
