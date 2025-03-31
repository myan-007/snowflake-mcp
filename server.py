import logging
from flask import Flask, request, jsonify
from config import FLASK_CONFIG
from snowflake_utils import get_connection, execute_query

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/execute_query', methods=['POST'])
def query_endpoint():
    """Execute a SQL query on Snowflake and return the results."""
    try:
        data = request.json
        query = data.get('query')
        params = data.get('params')
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        try:
            formatted_results = execute_query(query, params)
            
            return jsonify({
                "status": "success",
                "results": formatted_results,
                "row_count": len(formatted_results)
            })
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return jsonify({"error": str(e)}), 500
    
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({"error": "Invalid request format"}), 400

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    try:
        connection = get_connection()
        connection.close()
        return jsonify({"status": "healthy", "message": "Connected to Snowflake successfully"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=FLASK_CONFIG['port'], debug=FLASK_CONFIG['debug'])
