import psycopg2
import json

def generate_modified_sql(parsed_query, modifications):
    """
    Generates a modified SQL query based on the provided modifications.
    
    Args:
    - parsed_query: Dictionary containing parsed query information from preprocessing.
    - modifications: List of modifications to apply on the parsed query.

    Returns:
    - modified_sql: The modified SQL query as a string.
    """
    modified_sql = parsed_query['original_sql']

    # Apply join modifications
    for modification in modifications:
        if modification['type'] == 'join_change':
            if modification['new_type'] == 'Merge Join':
                modified_sql = modified_sql.replace("HASH JOIN", "MERGE JOIN")
            elif modification['new_type'] == 'Hash Join':
                modified_sql = modified_sql.replace("MERGE JOIN", "HASH JOIN")

        elif modification['type'] == 'scan_change':
            # Replace scan types in the SQL if applicable (for simplicity, assuming Seq Scan or Index Scan)
            if modification['new_type'] == 'Index Scan':
                modified_sql = modified_sql.replace("SEQ SCAN", "INDEX SCAN")
            elif modification['new_type'] == 'Seq Scan':
                modified_sql = modified_sql.replace("INDEX SCAN", "SEQ SCAN")

    return modified_sql

def retrieve_aqp(modified_sql):
    """
    Connects to PostgreSQL, retrieves the AQP, and calculates the cost of the modified query.
    
    Args:
    - modified_sql: The modified SQL query to execute EXPLAIN on.

    Returns:
    - aqp_data: JSON representation of the AQP and estimated cost.
    """
    try:
        # Database connection (replace with your credentials)
        conn = psycopg2.connect(
            database="postgres",
            user="postgres",
            password="password",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()

        # Retrieve the AQP with cost using EXPLAIN (FORMAT JSON)
        cur.execute(f"EXPLAIN (FORMAT JSON) {modified_sql}")
        aqp_result = cur.fetchone()[0]
        
        # The AQP data is in JSON format
        aqp_data = aqp_result[0]  # Assuming the result is a list with a JSON object

        # Close the connection
        cur.close()
        conn.close()

        print(aqp_data)
        return aqp_data

    except Exception as e:
        print(f"An error occurred while retrieving AQP: {e}")
        return None
