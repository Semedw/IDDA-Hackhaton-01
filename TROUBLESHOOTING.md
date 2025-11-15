# Troubleshooting 404 Errors

## Common 404 Issues and Solutions

### 1. Backend Server Not Running
**Symptom**: 404 on all API endpoints

**Solution**:
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

Or with Docker:
```bash
docker-compose up
```

### 2. Frontend Server Not Running
**Symptom**: 404 on frontend routes

**Solution**:
```bash
cd frontend
npm install
npm run dev
```

### 3. API Endpoint Not Found
**Symptom**: 404 on specific API calls

**Check available endpoints**:
- `GET http://localhost:8000/api/` - API root (lists all endpoints)
- `POST http://localhost:8000/api/auth/signup/` - User registration
- `POST http://localhost:8000/api/auth/login/` - User login
- `GET http://localhost:8000/api/assets/` - List assets
- `GET http://localhost:8000/api/assets/my/` - User's tracked assets
- `POST http://localhost:8000/api/assets/add/` - Add asset
- `POST http://localhost:8000/api/analysis/run/` - Run analysis
- `POST http://localhost:8000/api/chat/` - Chat endpoint
- `POST http://localhost:8000/api/recommendations/generate/` - Generate recommendations
- `GET http://localhost:8000/api/news/` - Get news

### 4. CORS Issues
**Symptom**: 404 or CORS errors in browser console

**Solution**: Ensure backend CORS settings allow frontend origin:
- Frontend runs on: http://localhost:5173
- Backend runs on: http://localhost:8000

### 5. Authentication Required
**Symptom**: 401 Unauthorized (not 404, but related)

**Solution**: 
- Make sure you're logged in
- Check that JWT token is in localStorage
- Token might be expired - try logging in again

### 6. Database Not Migrated
**Symptom**: 500 errors or missing tables

**Solution**:
```bash
cd backend
source venv/bin/activate
python manage.py migrate
```

### Quick Test
Test if backend is running:
```bash
curl http://localhost:8000/api/
```

Should return JSON with API information.

Test if frontend is running:
Open http://localhost:5173 in browser

