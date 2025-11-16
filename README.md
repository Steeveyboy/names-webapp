# Names Analytics Webapp

A full-stack web application for visualizing and analyzing newborn names data from the Social Security Administration (SSA). Explore naming trends, popularity changes, and demographic patterns from 1898 to 2021.

## 🏗️ Project Structure

```
names-webapp/
├── rest/                   # Python Flask backend
│   ├── app.py             # Flask application
│   └── dbWrapper.py       # Database connection wrapper
├── web/                   # Frontend (HTML, CSS, JavaScript)
├── data/                  # SSA data files
├── names_database.db      # SQLite database
├── query_maker.ipynb      # Data exploration notebook
└── requirements.txt       # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ (Python 3.12 recommended)
- Node.js 16+ (for frontend development)
- Git

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd names-webapp
```

## 🐍 Backend Setup (Flask API)

### 1. Create Virtual Environment

```bash
# Create virtual environment
python3.12 -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# For development (includes Jupyter, pandas, seaborn)
pip install -r requirements-dev.txt
```

### 3. Verify Database

```bash
# Check if database exists and has data
python3 -c "
import sqlite3
conn = sqlite3.connect('names_database.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM ssa_names')
print(f'Database contains {cursor.fetchone()[0]} records')
conn.close()
"
```

### 4. Run Backend Server

```bash
cd rest
flask run --debug
# Or
python app.py
```

The API will be available at `http://localhost:5000`

### 5. Test API Endpoints

```bash
# Test name search
curl http://localhost:5000/searchName/John

# Expected response: JSON array with name data
```

## 🌐 Frontend Setup

### 1. Basic HTML/CSS/JavaScript Setup

The frontend will be served from the `web/` directory. For development:

```bash
cd web

# Install a simple HTTP server for development
npm install -g live-server
# Or use Python's built-in server
python -m http.server 8080

# Access at http://localhost:8080
```

### 2. Frontend Structure (To Be Created)

```
web/
├── index.html              # Main application page
├── css/
│   ├── styles.css         # Custom styles
│   └── bootstrap.min.css  # CSS framework (optional)
├── js/
│   ├── app.js            # Main application logic
│   ├── charts.js         # Data visualization
│   └── api.js            # API communication
└── assets/
    └── images/           # Static images
```

### 3. Recommended Frontend Libraries

Add these to your HTML for quick development:

```html
<!-- CSS Framework -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

<!-- Charts and Visualization -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<!-- OR -->
<script src="https://d3js.org/d3.v7.min.js"></script>

<!-- HTTP Requests -->
<script src="https://axios-http.com/axios.min.js"></script>
```

## 🛠️ Development Workflow

### Backend Development

1. **Run Flask in debug mode:**
   ```bash
   cd rest
   export FLASK_DEBUG=1
   flask run
   ```

2. **Data exploration:**
   ```bash
   jupyter lab query_maker.ipynb
   ```

3. **Database queries:**
   ```python
   from dbWrapper import dbManager
   dbm = dbManager()
   results = dbm.get_name("John")
   ```

### Frontend Development

1. **Live reload development:**
   ```bash
   cd web
   live-server --port=8080
   ```

2. **API integration:**
   ```javascript
   // Example API call
   fetch('http://localhost:5000/searchName/John')
     .then(response => response.json())
     .then(data => console.log(data));
   ```

## 📊 Available Data & Analytics

The database contains SSA names data with the following schema:

```sql
CREATE TABLE ssa_names(
    name TEXT,      -- First name
    gender CHAR,    -- 'M' or 'F'
    count INTEGER,  -- Number of babies with this name
    year INTEGER    -- Year (1898-2021)
);
```

### Possible Analytics Features

- **Trend Analysis**: Name popularity over time
- **Gender Distribution**: Male vs Female usage
- **Decade Comparisons**: Popular names by decade
- **Name Rankings**: Top names by year
- **Statistical Insights**: Rare vs common names
- **Search & Discovery**: Name variations and suggestions

## 🚀 Deployment

### Backend Deployment Options

1. **Heroku**
2. **Railway**
3. **PythonAnywhere**
4. **DigitalOcean App Platform**

### Frontend Deployment Options

1. **Netlify**
2. **Vercel**
3. **GitHub Pages**
4. **Firebase Hosting**

## 🐛 Troubleshooting

### Common Issues

1. **Database not found**: Ensure `names_database.db` exists in the root directory
2. **Import errors**: Activate virtual environment and install requirements
3. **CORS errors**: Configure Flask-CORS for cross-origin requests
4. **Port conflicts**: Change Flask port with `flask run --port=5001`

### Development Tips

- Use `flask run --debug` for auto-reload during development
- Check browser developer tools for frontend errors
- Test API endpoints with curl or Postman
- Use SQLite browser to inspect database contents

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

[Add your license here]

---

**Happy Hacking! 🎯**