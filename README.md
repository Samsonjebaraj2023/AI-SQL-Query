# MySQL Query Assistant

A web-based interface that converts natural language questions into SQL queries and executes them against MySQL databases, with support for multiple tenants.

## Features

- Natural language to SQL conversion using OpenAI
- Multi-tenant support (different databases)
- Visual display of query results
- Secure connection handling
- Error handling and validation

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8+
- Node.js (for optional frontend development)
- MySQL server (version 5.7+)
- MySQL client and development libraries

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Samsonjebaraj2023/AI-SQL-Query.git
cd AI-SQL-Query
```

### 2. Backend Setup
#### Install Python Dependencies

```bash
pip install -r requirements.txt
```
#### Create `.env` File

Create a `.env` file in the root directory with the following content:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Replace `your_openai_api_key_here` with your actual OpenAI API key.

#### Database Configuration

1. Ensure your MySQL server is running
2. Create a user with appropriate permissions or use existing credentials
3. Update the connection details in the frontend JavaScript or create a configuration file

### 3. Frontend Setup

The frontend is a simple HTML file that can be served directly. No build step is required.

### 4. Run the Application

#### Start the FastAPI Backend

```bash
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

#### Serve the Frontend

 Open the `index.html` file directly in a browser


Then access the frontend at `http://localhost:8080`

## Configuration

### Backend Configuration

Modify these in the Python code (`main.py`) as needed:
- Database connection pool settings
- OpenAI model selection (default: gpt-4)
- API timeout settings
- CORS allowed origins

### Frontend Configuration

Modify these in the JavaScript section of `index.html`:
- Default connection parameters (host, port, user, password)
- API endpoint URL
- UI styling and behavior

## Usage

1. Open the web interface in your browser
2. Enter:
   - Database name (tenant identifier)
   - Your question in natural language
3. Click "Run Query"
4. View the generated SQL and results

