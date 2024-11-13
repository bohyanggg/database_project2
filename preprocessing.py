import re

def parse_query(sql_query):
    """
    Parses the SQL query to identify its components, such as tables, joins, and conditions.
    This is a simplified example and may need enhancement for complex queries.
    """
    # Extract table names from the query
    tables = re.findall(r'from\s+(\w+)', sql_query, re.IGNORECASE)
    tables += re.findall(r'join\s+(\w+)', sql_query, re.IGNORECASE)

    print("tables:")
    print(tables)

    # Extract join conditions
    join_conditions = re.findall(r'on\s+(\w+\.\w+)\s*=\s*(\w+\.\w+)', sql_query, re.IGNORECASE)
    print("join conditions:")
    print(join_conditions)

    parsed_query = {
        'tables': tables,
        'join_conditions': join_conditions,
        'original_sql': sql_query
    }
    print("parsed query")
    print(parsed_query)
    return parsed_query

def prepare_modifications(qep_structure, modifications):
    """
    Prepares modifications for the what-if analysis.
    Takes the QEP structure and applies the user-defined modifications to return a modified structure.
    
    Args:
    - qep_structure: The QEP structure parsed from PostgreSQL JSON output.
    - modifications: A dictionary of modifications, e.g., changing join types or scan types.

    Returns:
    - modified_qep_structure: The updated QEP structure with modifications applied.
    """
    modified_qep_structure = qep_structure.copy()
    
    for modification in modifications:
        if modification['type'] == 'join_change':
            # Find the join node in the QEP structure and change the join type
            for node in modified_qep_structure:
                if node['Node Type'] == 'Hash Join' and modification['new_type'] == 'Merge Join':
                    node['Node Type'] = 'Merge Join'
                elif node['Node Type'] == 'Merge Join' and modification['new_type'] == 'Hash Join':
                    node['Node Type'] = 'Hash Join'
        
        elif modification['type'] == 'scan_change':
            # Find the scan node in the QEP structure and change the scan type
            for node in modified_qep_structure:
                if node['Node Type'] == 'Seq Scan' and modification['new_type'] == 'Index Scan':
                    node['Node Type'] = 'Index Scan'
                elif node['Node Type'] == 'Index Scan' and modification['new_type'] == 'Seq Scan':
                    node['Node Type'] = 'Seq Scan'
    
    return modified_qep_structure
