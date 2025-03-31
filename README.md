# Snowflake MCP (Microservice Control Plane)

A Flask-based microservice for interacting with Snowflake data warehouse.

## Features

- REST API for executing SQL queries on Snowflake
- Health check endpoint to verify Snowflake connectivity
- Environment-based configuration

## Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd snowflake-mcp
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a .env file with your Snowflake credentials:
   ```
   cp .env.template .env
   ```
   Then edit the .env file with your actual Snowflake credentials.

## Usage

### Start the server

```
python server.py
```

The server will start on port 5000 by default (configurable in .env).

### API Endpoints

#### Execute Query

```
POST /execute_query
```

Request body:
```json
{
  "query": "SELECT * FROM your_table LIMIT 10"
}
```

Response:
```json
{
  "status": "success",
  "results": [
    {
      "column1": "value1",
      "column2": "value2"
    },
    ...
  ],
  "row_count": 10
}
```

#### Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "message": "Connected to Snowflake successfully"
}
```

## Development

- Formatting: `codemcp format`
- Testing: `codemcp test`
