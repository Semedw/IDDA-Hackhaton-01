# Verbix AI - Complete URL Reference

## Frontend URLs (React App)
**Base URL:** `http://localhost:5173`

### Public Routes (No Authentication Required)
- **`/`** - Homepage/Landing page
  - Shows app features and call-to-action
  - Redirects to `/dashboard` if already logged in

- **`/login`** - Login page
  - User authentication form
  - Redirects to `/dashboard` if already logged in

- **`/register`** - Registration page
  - User signup form
  - Redirects to `/dashboard` if already logged in

### Protected Routes (Authentication Required)
- **`/dashboard`** - Main dashboard
  - View tracked assets
  - View latest news
  - Add/remove assets
  - Update profile (budget, risk profile)

- **`/asset/:id`** - Asset detail page
  - View asset information
  - Price history chart
  - Run AI analysis
  - View analysis results

- **`/chat`** - AI Chat Assistant
  - Interactive chatbot
  - Ask questions about assets and portfolio

- **`/recommendations`** - AI Recommendations
  - Generate investment recommendations
  - View personalized suggestions based on budget

---

## Backend API URLs (Django REST Framework)
**Base URL:** `http://localhost:8000`

### API Root
- **`GET /api/`** - API information endpoint
  - Returns list of all available endpoints
  - No authentication required

### Authentication Endpoints (`/api/auth/`)
- **`POST /api/auth/signup/`** - Register new user
  - Body: `{ "username": "...", "email": "...", "password": "..." }`
  - Returns: User data
  - No authentication required

- **`POST /api/auth/login/`** - Login and get JWT tokens
  - Body: `{ "username": "...", "password": "..." }`
  - Returns: `{ "access": "...", "refresh": "..." }`
  - No authentication required

- **`GET /api/auth/profile/`** - Get user profile
  - Returns: User profile (budget, risk_profile, etc.)
  - **Requires authentication**

- **`PUT /api/auth/profile/`** - Update user profile
  - Body: `{ "budget": 10000, "risk_profile": "moderate" }`
  - Returns: Updated profile
  - **Requires authentication**

### Assets Endpoints (`/api/assets/`)
- **`GET /api/assets/`** - List all available assets
  - Returns: List of all assets
  - **Requires authentication**

- **`GET /api/assets/my/`** - Get user's tracked assets
  - Returns: List of assets user is tracking
  - **Requires authentication**

- **`POST /api/assets/add/`** - Add asset to tracking
  - Body: `{ "symbol": "AAPL", "type": "stock", "name": "Apple Inc." }`
  - Returns: Asset data
  - **Requires authentication**

- **`GET /api/assets/{asset_id}/`** - Get asset details
  - Returns: Asset details with price history
  - **Requires authentication**

- **`DELETE /api/assets/{asset_id}/remove/`** - Remove asset from tracking
  - Returns: Success message
  - **Requires authentication**

### Analysis Endpoints (`/api/analysis/`)
- **`POST /api/analysis/run/`** - Run AI analysis on asset
  - Body: `{ "asset_id": 1 }` or `{ "symbol": "AAPL" }`
  - Returns: Analysis result (summary, sentiment, risk_rating)
  - **Requires authentication**

- **`GET /api/analysis/{asset_id}/`** - Get latest analysis for asset
  - Returns: Most recent analysis result
  - **Requires authentication**

### Chat Endpoints (`/api/chat/`)
- **`POST /api/chat/`** - Send message to AI chatbot
  - Body: `{ "question": "What should I know about my portfolio?" }`
  - Returns: `{ "question": "...", "response": "..." }`
  - **Requires authentication**

### Recommendations Endpoints (`/api/recommendations/`)
- **`POST /api/recommendations/generate/`** - Generate AI recommendations
  - Body: None (uses user's profile and tracked assets)
  - Returns: List of recommendations with actions (BUY/HOLD/SELL)
  - **Requires authentication**

- **`GET /api/recommendations/my/`** - Get user's recommendations
  - Returns: List of all recommendations for the user
  - **Requires authentication**

### News Endpoints (`/api/news/`)
- **`GET /api/news/`** - Get latest news
  - Query params: `?limit=10` (optional, default: 10)
  - Returns: List of news items
  - **Requires authentication**

### Admin Panel
- **`GET /admin/`** - Django admin interface
  - Requires superuser login
  - Access to all models and data

---

## Example API Calls

### Register a new user
```bash
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

### Get tracked assets (with authentication)
```bash
curl -X GET http://localhost:8000/api/assets/my/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Add an asset
```bash
curl -X POST http://localhost:8000/api/assets/add/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "type": "stock", "name": "Apple Inc."}'
```

### Run AI analysis
```bash
curl -X POST http://localhost:8000/api/analysis/run/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"asset_id": 1}'
```

### Chat with AI
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "What should I know about my portfolio?"}'
```

### Generate recommendations
```bash
curl -X POST http://localhost:8000/api/recommendations/generate/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get news
```bash
curl -X GET "http://localhost:8000/api/news/?limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## URL Flow Examples

### New User Journey
1. Visit `http://localhost:5173/` → Homepage
2. Click "Sign Up" → `http://localhost:5173/register`
3. After registration → Auto-login → `http://localhost:5173/dashboard`
4. Add assets → `http://localhost:5173/dashboard`
5. View asset → `http://localhost:5173/asset/1`
6. Get recommendations → `http://localhost:5173/recommendations`

### Returning User Journey
1. Visit `http://localhost:5173/` → Redirects to `/dashboard` (if logged in)
2. Or visit `http://localhost:5173/login` → Login → `/dashboard`

---

## Notes

- All API endpoints (except `/api/`, `/api/auth/signup/`, `/api/auth/login/`) require JWT authentication
- JWT token should be included in headers: `Authorization: Bearer <token>`
- Frontend automatically handles authentication and redirects
- All protected frontend routes redirect to `/login` if not authenticated
- All protected routes require valid JWT token

