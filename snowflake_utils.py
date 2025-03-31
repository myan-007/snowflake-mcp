import logging
from snowflake.connector import connect
from config import SNOWFLAKE_CONFIG

logger = logging.getLogger(__name__)

def get_connection():
    """Create and return a connection to Snowflake."""
    try:
        connection = connect(
            user=SNOWFLAKE_CONFIG['user'],
            password=SNOWFLAKE_CONFIG['password'],
            account=SNOWFLAKE_CONFIG['account'],
            warehouse=SNOWFLAKE_CONFIG['warehouse'],
            database=SNOWFLAKE_CONFIG['database'],
            schema=SNOWFLAKE_CONFIG['schema']
        )
        logger.info("Successfully connected to Snowflake")
        return connection
    except Exception as e:
        logger.error(f"Error connecting to Snowflake: {e}")
        raise

def execute_query(query, params=None):
    """
    Execute a SQL query on Snowflake and return the results.
    
    Args:
        query (str): SQL query to execute
        params (dict, optional): Parameters for the query
        
    Returns:
        tuple: (column_names, results)
    """
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description] if cursor.description else []
        
        # Format results as list of dictionaries
        formatted_results = [dict(zip(column_names, row)) for row in results]
        
        return formatted_results
    
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise
    
    finally:
        if connection:
            connection.close()
