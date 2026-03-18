# Mobile App Launcher - Product Authentication System
# PowerShell script to launch the mobile development environment

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   🚀 Mobile App Launcher" -ForegroundColor Green
Write-Host "   Product Authentication System" -ForegroundColor Green  
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📱 Starting mobile development environment..." -ForegroundColor Yellow
Write-Host ""

# Change to mobile app directory
Set-Location "d:\newww\mobile-app"

Write-Host "📂 Current directory: $(Get-Location)" -ForegroundColor Blue
Write-Host ""

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "⚠️  Dependencies not found. Installing..." -ForegroundColor Yellow
    Write-Host ""
    npm install
    Write-Host ""
    Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "✅ Dependencies already installed." -ForegroundColor Green
    Write-Host ""
}

Write-Host "🚀 Starting Expo development server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "📱 Instructions:" -ForegroundColor Cyan
Write-Host "   1. Wait for QR code to appear" -ForegroundColor White
Write-Host "   2. Install 'Expo Go' on your mobile device" -ForegroundColor White
Write-Host "   3. Scan the QR code with Expo Go" -ForegroundColor White
Write-Host "   4. App will load on your device" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Web version will be available at: http://localhost:19006" -ForegroundColor Magenta
Write-Host ""

# Start Expo
npx expo start

Write-Host ""
Write-Host "👋 Mobile app development server stopped." -ForegroundColor Yellow
Read-Host "Press Enter to continue..."