import unittest
import json
from unittest.mock import patch, MagicMock
from server import app

class TestAPI(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('server.get_snowflake_connection')
    def test_health_endpoint_success(self, mock_get_connection):
        # Mock the connection
        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection
        
        # Call health endpoint
        response = self.app.get('/health')
        data = json.loads(response.data)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['message'], 'Connected to Snowflake successfully')
        
        # Verify connection was closed
        mock_connection.close.assert_called_once()
    
    @patch('server.get_snowflake_connection')
    def test_health_endpoint_failure(self, mock_get_connection):
        # Mock connection failure
        mock_get_connection.side_effect = Exception('Connection error')
        
        # Call health endpoint
        response = self.app.get('/health')
        data = json.loads(response.data)
        
        # Verify response
        self.assertEqual(response.status_code, 500)
        self.assertEqual(data['status'], 'unhealthy')
        self.assertEqual(data['message'], 'Connection error')
    
    @patch('server.get_snowflake_connection')
    def test_execute_query_success(self, mock_get_connection):
        # Mock cursor and connection
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_connection
        
        # Mock query results
        mock_cursor.description = [('col1',), ('col2',)]
        mock_cursor.fetchall.return_value = [(1, 'a'), (2, 'b')]
        
        # Call query endpoint
        response = self.app.post('/execute_query', 
                                json={'query': 'SELECT * FROM test'},
                                content_type='application/json')
        data = json.loads(response.data)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['row_count'], 2)
        self.assertEqual(data['results'], [
            {'col1': 1, 'col2': 'a'},
            {'col1': 2, 'col2': 'b'}
        ])
        
        # Verify query was executed
        mock_cursor.execute.assert_called_once_with('SELECT * FROM test')
    
    def test_execute_query_no_query(self):
        # Call query endpoint without query
        response = self.app.post('/execute_query', 
                                json={},
                                content_type='application/json')
        data = json.loads(response.data)
        
        # Verify response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'No query provided')

if __name__ == '__main__':
    unittest.main()
