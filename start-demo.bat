@echo off
echo.
echo ============================================
echo 🔌 IoT Dashboard - Complete Demo Setup
echo ============================================
echo.
echo This will start:
echo   ✓ Backend Server (Node.js + WebSocket)
echo   ✓ Frontend Dashboard (React)
echo   ✓ Demo Device Simulator (3 virtual devices)
echo.
echo 🌐 Dashboard: http://localhost:3000
echo 📊 API Server: http://localhost:5000
echo.
echo Press any key to start...
pause >nul

echo.
echo 📦 Installing dependencies...
call npm install

echo.
echo 📦 Installing client dependencies...
cd client
call npm install
cd ..

echo.
echo 🚀 Starting servers...
echo.

:: Start all services in background
start "Backend Server" cmd /k "npm run server"
timeout /t 3 >nul
start "Frontend Dashboard" cmd /k "npm run client"
timeout /t 5 >nul
start "Demo Simulator" cmd /k "node demo-simulator.js"

echo.
echo ✅ All services started!
echo.
echo 🌐 Opening dashboard in browser...
timeout /t 3 >nul
start http://localhost:3000

echo.
echo 📖 Instructions:
echo   • Dashboard: http://localhost:3000
echo   • You should see 3 demo devices connecting
echo   • Try the device controls and visualizations
echo   • Check the historical data section
echo   • Export data as CSV
echo.
echo ⏹️  To stop all services, close the command windows
echo.
pause
