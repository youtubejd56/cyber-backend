@echo off
echo ============================================
echo  CyberTraining Platform - Setup Script
echo ============================================

echo.
echo [1/4] Installing Python dependencies...
cd backend
pip install -r requirements.txt

echo.
echo [2/4] Running Django migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo [3/4] Seeding database with rooms, machines, and demo users...
python manage.py seed_data

echo.
echo [4/4] Installing Next.js frontend dependencies...
cd ..\frontend
npm install

echo.
echo ============================================
echo  SETUP COMPLETE!
echo ============================================
echo.
echo To start the BACKEND (Django):
echo   cd backend
echo   python manage.py runserver
echo   ^> http://localhost:8000
echo   ^> http://localhost:8000/admin  (admin/admin123)
echo.
echo To start the FRONTEND (Next.js):
echo   cd frontend
echo   npm run dev
echo   ^> http://localhost:3000
echo.
echo Demo accounts:
echo   admin / admin123  (superuser)
echo   h4cker / hacker123
echo   darkwolf / dark123
echo.
pause
