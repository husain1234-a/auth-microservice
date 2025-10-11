#!/bin/bash

echo "Starting all microservices..."

# Function to start a service in a new terminal
start_service() {
    local service_name=$1
    local command=$2
    echo "Starting $service_name..."
    
    # For different terminal emulators, adjust as needed
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal --title="$service_name" -- bash -c "$command; exec bash"
    elif command -v xterm &> /dev/null; then
        xterm -title "$service_name" -e bash -c "$command; exec bash" &
    elif command -v osascript &> /dev/null; then
        # macOS Terminal
        osascript -e "tell application \"Terminal\" to do script \"cd $(pwd) && $command\""
    else
        echo "No suitable terminal found. Please run manually: $command"
    fi
    
    sleep 2
}

# Start each service
start_service "Auth Service" "cd backend/auth_service && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload"
start_service "Product Service" "cd backend/product_service && python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload"
start_service "Cart Service" "cd backend/cart_service && python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload"
start_service "Order Service" "cd backend/order_service && python init_db.py && python -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload"
start_service "API Gateway" "cd backend/gateway && python main.py"
start_service "Frontend" "cd frontend && npm run dev"

echo ""
echo "All services started!"
echo ""
echo "Services running on:"
echo "- Auth Service: http://localhost:8001"
echo "- Product Service: http://localhost:8002"
echo "- Cart Service: http://localhost:8003"
echo "- Order Service: http://localhost:8004"
echo "- API Gateway: http://localhost:8000"
echo "- Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop this script (services will continue running)"

# Keep the script running
while true; do
    sleep 1
done