@echo off
echo Starting all microservices...

REM Start Auth Service
start "Auth Service" cmd /k "cd backend/auth_service && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload"

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Start Product Service
start "Product Service" cmd /k "cd backend/product_service && python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload"

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Start Cart Service
start "Cart Service" cmd /k "cd backend/cart_service && python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload"

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Start Order Service
start "Order Service" cmd /k "cd backend/order_service && python init_db.py && python -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload"

REM Wait a moment
timeout /t 3 /nobreak >nul

REM Start Gateway
start "API Gateway" cmd /k "cd backend/gateway && python main.py"

REM Wait a moment
timeout /t 3 /nobreak >nul

REM Start Frontend
start "Frontend" cmd /k "cd frontend && npm run dev"

echo All services started!
echo.
echo Services running on:
echo - Auth Service: http://localhost:8001
echo - Product Service: http://localhost:8002
echo - Cart Service: http://localhost:8003
echo - Order Service: http://localhost:8004
echo - API Gateway: http://localhost:8000
echo - Frontend: http://localhost:3000
echo.
pause