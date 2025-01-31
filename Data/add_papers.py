import db_utils
from scholarly import scholarly
from datetime import datetime
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_person_type(prof_id: str, title: str, conn: Any) -> None:
    """
    Update the person's title in the database.
    
    Args:
        prof_id: Google Scholar ID
        title: New title to set
        conn: Database connection
    """
    sql = "UPDATE people SET title = %s WHERE id = %s"
    db_utils.execute_psql_statement(conn, sql, (title, f"GS{prof_id}"))

def update_active_status(prof_id: str, is_active: bool, conn: Any) -> None:
    """
    Update the person's active status in the database.
    
    Args:
        prof_id: Google Scholar ID
        is_active: Whether person is considered active
        conn: Database connection
    """
    sql = "UPDATE people SET is_active = %s WHERE id = %s"
    db_utils.execute_psql_statement(conn, sql, (is_active, f"GS{prof_id}"))

def insert_paper(paper_data: Dict[str, Any], conn: Any) -> None:
    """
    Insert or update paper details in the database.
    
    Args:
        paper_data: Dictionary containing paper details
        conn: Database connection
    """
    sql = """
        INSERT INTO research_papers (
            rp_id, people_id, title, abstract, 
            pub_year, pub_url, journal, num_citations
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (rp_id) DO UPDATE SET
            title = EXCLUDED.title,
            abstract = EXCLUDED.abstract,
            pub_year = EXCLUDED.pub_year,
            pub_url = EXCLUDED.pub_url,
            journal = EXCLUDED.journal,
            num_citations = EXCLUDED.num_citations
    """
    params = (
        paper_data['paper_id'],
        paper_data['author_id'], 
        paper_data['title'],
        paper_data['abstract'],
        paper_data['pub_year'],
        paper_data['pub_url'],
        paper_data['journal'],
        paper_data['num_citations']
    )
    db_utils.execute_psql_statement(conn, sql, params)

def get_papers(prof_id: str, conn: Any) -> None:
    """
    Retrieve and store publication details for a given professor ID.
    
    Args:
        prof_id: The Google Scholar ID of the professor
        conn: Database connection object
    """
    try:
        search_query = scholarly.search_author_id(prof_id)
        author = scholarly.fill(search_query, sections=["publications"])
        current_year = datetime.now().year
        
        # Get publications from last 20 years
        recent_pubs = [
            pub for pub in author["publications"] 
            if int(pub.get('bib', {}).get('pub_year', 0)) > current_year - 20
        ]
        
        total_pubs = len(author["publications"])
        logger.info(f"Found {total_pubs} total publications for {prof_id}, {len(recent_pubs)} from last 20 years")
        
        # Update person type based on publication count
        title = "professor" if total_pubs > 3 else "scholar"
        update_person_type(prof_id, title, conn)

        latest_pub_year = 0

        # Process each publication
        for pub in recent_pubs:
            try:
                pub_details = scholarly.fill(pub)
                bib = pub_details.get('bib', {})
                
                pub_year = bib.get('pub_year', 0)
                latest_pub_year = max(latest_pub_year, pub_year)
                
                paper_data = {
                    'paper_id': pub_details.get('author_pub_id', ''),
                    'author_id': f"GS{prof_id}",
                    'title': bib.get('title', ''),
                    'abstract': bib.get('abstract', ''),
                    'pub_year': pub_year,
                    'pub_url': pub_details.get('pub_url', ''),
                    'journal': bib.get('journal', ''),
                    'num_citations': pub_details.get('num_citations', 0)
                }
                
                insert_paper(paper_data, conn)
                
            except Exception as e:
                logger.error(f"Error processing publication for {prof_id}: {str(e)}")
                continue

        # Update active status based on latest publication
        is_active = (current_year - latest_pub_year) <= 6
        update_active_status(prof_id, is_active, conn)
        logger.info(f"Updated {prof_id} - Latest pub: {latest_pub_year}, Active: {is_active}")
                
    except Exception as e:
        logger.error(f"Error retrieving author data for {prof_id}: {str(e)}")

def main() -> None:
    """Main function to update publication data."""
    conn = db_utils.create_connection()
    updated = set()
    
    # Get recently updated profiles
    sql_statement = """
        SELECT DISTINCT people_id 
        FROM research_papers 
        WHERE last_updated >= NOW() - INTERVAL '30 days';
    """
    already_updated = db_utils.execute_psql_statement(conn, sql_statement)
    updated.update(row[0] for row in already_updated)

    # Get all profiles and update those not recently updated
    sql_statement = "SELECT id FROM people ORDER BY last_updated ASC NULLS FIRST"
    profs = db_utils.execute_psql_statement(conn, sql_statement)
    
    for prof in profs:
        prof_id = prof[0]
        if prof_id in updated:
            logger.info(f"Skipping recently updated profile: {prof_id}")
            continue

        #prof_ids are stored with prefix GS in database    
        logger.info(f"Processing profile: {prof_id}")
        get_papers(prof_id[2:], conn)    

if __name__ == "__main__":
    main()