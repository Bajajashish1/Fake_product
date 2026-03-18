@echo off
title Mobile App Launcher - Product Authentication System
color 0A

echo ================================================
echo    🚀 Mobile App Launcher
echo    Product Authentication System
echo ================================================
echo.

echo 📱 Starting mobile development environment...
echo.

cd /d "d:\newww\mobile-app"

echo 📂 Current directory: %CD%
echo.

echo 🔧 Checking if node_modules exists...
if not exist "node_modules" (
    echo ⚠️  Dependencies not found. Installing...
    echo.
    npm install
    echo.
    echo ✅ Dependencies installed successfully!
    echo.
) else (
    echo ✅ Dependencies already installed.
    echo.
)

echo 🚀 Starting Expo development server...
echo.
echo 📱 Instructions:
echo    1. Wait for QR code to appear
echo    2. Install 'Expo Go' on your mobile device
echo    3. Scan the QR code with Expo Go
echo    4. App will load on your device
echo.
echo 🌐 Web version will be available at: http://localhost:19006
echo.

npx expo start

echo.
echo 👋 Mobile app development server stopped.
pause