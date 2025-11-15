# Verbix AI - Stock & Crypto Analysis MVP

A full-stack Django + React application that analyzes stocks & cryptocurrencies, fetches news, and provides AI-powered recommendations based on user budget.

## Tech Stack

- **Backend**: Django 5, Django REST Framework, PostgreSQL
- **Frontend**: React 18, Vite, Tailwind CSS
- **AI**: OpenAI API (GPT-3.5-turbo)
- **Authentication**: JWT (Simple JWT)
- **Database**: PostgreSQL

## Features

- ✅ User registration and JWT authentication
- ✅ Track stocks and cryptocurrencies
- ✅ AI-powered analysis with sentiment and risk ratings
- ✅ Interactive chatbot for asset questions
- ✅ Budget-based investment recommendations
- ✅ News feed integration
- ✅ Clean, modern UI with Tailwind CSS

## Quick Start with Docker

1. **Clone and navigate to the project**:
   ```bash
   cd hackathon
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your `OPENAI_API_KEY`:
   ```
   OPENAI_API_KEY=sk-your-key-here
   RAPIDAPI_KEY=your-rapidapi-key-here
   ```

3. **Start all services** (includes Redis, Celery worker, and Celery beat):
   ```bash
   docker compose up --build
   ```
   
   **Note**: Use `docker compose` (v2) instead of `docker compose` (v1) to avoid compatibility issues.

4. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin (create superuser first)
   - Redis: localhost:6379

5. **Create a superuser** (optional, for admin access):
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

6. **Stock prices update automatically** every 5 seconds via Celery!

## Manual Setup (Without Docker)

### Backend Setup

1. **Navigate to backend**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**:
   - Create a database named `verbix_ai`
   - Update `.env` with your database credentials

5. **Start Redis** (required for Celery):
   ```bash
   # Install Redis (Ubuntu/Debian)
   sudo apt-get install redis-server
   
   # Start Redis
   redis-server
   ```

6. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

7. **Create superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

8. **Start services** (in separate terminals):
   
   **Terminal 1 - Django Server**:
   ```bash
   python manage.py runserver
   ```
   
   **Terminal 2 - Celery Worker**:
   ```bash
   celery -A verbix_ai worker --loglevel=info
   ```
   
   **Terminal 3 - Celery Beat (Scheduler)**:
   ```bash
   celery -A verbix_ai beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
   ```

   Or use the helper script:
   ```bash
   ./start_celery.sh
   ```

### Frontend Setup

1. **Navigate to frontend**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

## API Endpoints

### Authentication
- `POST /api/auth/signup/` - Register new user
- `POST /api/auth/login/` - Login and get JWT tokens
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile (budget, risk profile)

### Assets
- `GET /api/assets/` - List all assets
- `GET /api/assets/my/` - Get user's tracked assets
- `POST /api/assets/add/` - Add asset to tracking
- `GET /api/assets/{id}/` - Get asset details
- `DELETE /api/assets/{id}/remove/` - Remove asset from tracking

### Analysis
- `POST /api/analysis/run/` - Run AI analysis on asset
- `GET /api/analysis/{asset_id}/` - Get latest analysis for asset

### Chat
- `POST /api/chat/` - Send question to AI chatbot

### Recommendations
- `POST /api/recommendations/generate/` - Generate AI recommendations
- `GET /api/recommendations/my/` - Get user's recommendations

### News
- `GET /api/news/` - Get latest news items

## Usage

1. **Register/Login**: Create an account or sign in
2. **Set Profile**: Update your budget and risk profile in the dashboard
3. **Add Assets**: Add stocks (e.g., AAPL, TSLA) or cryptocurrencies (e.g., bitcoin, ethereum)
4. **Run Analysis**: Click "Run Analysis" on any asset to get AI-powered insights
5. **Chat**: Ask questions about your portfolio in the Chat page
6. **Get Recommendations**: Generate personalized investment recommendations based on your budget

## Project Structure

```
hackathon/
├── backend/
│   ├── accounts/          # User authentication & profiles
│   ├── market/            # Assets & price tracking
│   ├── analysis/          # AI analysis results
│   ├── chat/              # Chatbot endpoint
│   ├── recommendations/   # AI recommendations
│   ├── news/              # News fetching
│   └── verbix_ai/         # Django settings
├── frontend/
│   ├── src/
│   │   ├── pages/         # React pages
│   │   ├── components/    # React components
│   │   └── utils/         # API utilities
│   └── package.json
├── docker compose.yml
├── .env.example
└── README.md
```

## Environment Variables

Required environment variables (see `.env.example`):

- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: Database config
- `OPENAI_API_KEY`: Your OpenAI API key (required for AI features)

## Notes

- This is an MVP - production-ready features like error handling, rate limiting, and comprehensive testing should be added
- Price data uses mock/simple APIs for MVP - integrate real APIs (Yahoo Finance, CoinGecko) for production
- AI features require a valid OpenAI API key
- All financial advice is AI-generated and should not be considered real financial advice

## Troubleshooting

- **Database connection errors**: Ensure PostgreSQL is running and credentials are correct
- **OpenAI API errors**: Verify your API key is set correctly in `.env`
- **CORS errors**: Check that frontend is running on port 5173 and backend on 8000
- **Migration errors**: Run `python manage.py makemigrations` then `python manage.py migrate`

## License

MIT

