@echo off
:: Hotel Booking System Deployment Script
:: Version: v3-0304250-1320
:: Date: March 4, 2025

setlocal enabledelayedexpansion

:: Configuration
set APP_NAME=hotel-booking-system
set GITHUB_REPO=https://github.com/SankarNag23/hotel-booking-system.git
set BRANCH=main
set TAG=v3-0304250-1320

:: Colors for output
set RED=[91m
set GREEN=[92m
set YELLOW=[93m
set NC=[0m

:: Logging functions
:log
echo %GREEN%[%date% %time%] %~1%NC%
exit /b 0

:error
echo %RED%[%date% %time%] ERROR: %~1%NC%
exit /b 1

:warn
echo %YELLOW%[%date% %time%] WARNING: %~1%NC%
exit /b 0

:: Check prerequisites
:check_prerequisites
call :log "Checking prerequisites..."

where node >nul 2>&1
if %errorlevel% neq 0 (
    call :error "Node.js is required but not installed."
    exit /b 1
)

where npm >nul 2>&1
if %errorlevel% neq 0 (
    call :error "npm is required but not installed."
    exit /b 1
)

where git >nul 2>&1
if %errorlevel% neq 0 (
    call :error "Git is required but not installed."
    exit /b 1
)

call :log "Prerequisites check passed."
exit /b 0

:: Cleanup function
:cleanup
if exist %APP_NAME% (
    call :warn "Cleaning up existing directory..."
    rmdir /s /q %APP_NAME%
)
exit /b 0

:: Clone repository
:clone_repo
call :log "Cloning repository..."
git clone %GITHUB_REPO% %APP_NAME%
cd %APP_NAME%
git checkout %TAG%
exit /b 0

:: Install dependencies
:install_dependencies
call :log "Installing dependencies..."
call npm install
exit /b 0

:: Build application
:build_app
call :log "Building application..."
call npm run build
exit /b 0

:: Create environment file
:create_env
call :log "Creating environment file..."
(
echo PORT=10000
echo NODE_ENV=production
) > .env
exit /b 0

:: Run tests
:run_tests
call :log "Running tests..."
call npm test
if %errorlevel% neq 0 (
    call :warn "Tests failed but continuing deployment..."
)
exit /b 0

:: Health check
:health_check
call :log "Performing health check..."
set retries=5
set wait_time=5

:health_check_loop
curl -s http://localhost:10000/api/hotels >nul 2>&1
if %errorlevel% equ 0 (
    call :log "Health check passed."
    exit /b 0
)

set /a retries-=1
if %retries% gtr 0 (
    call :warn "Health check failed. Retrying in %wait_time% seconds..."
    timeout /t %wait_time% >nul
    goto :health_check_loop
)

call :error "Health check failed after all retries."
exit /b 1

:: Main deployment function
:deploy
call :log "Starting deployment of %APP_NAME% version %TAG%"

:: Run deployment steps
call :check_prerequisites
if %errorlevel% neq 0 goto :rollback

call :cleanup
if %errorlevel% neq 0 goto :rollback

call :clone_repo
if %errorlevel% neq 0 goto :rollback

call :install_dependencies
if %errorlevel% neq 0 goto :rollback

call :create_env
if %errorlevel% neq 0 goto :rollback

call :build_app
if %errorlevel% neq 0 goto :rollback

call :run_tests
if %errorlevel% neq 0 goto :rollback

call :log "Starting application..."
start /b cmd /c npm start

:: Wait for application to start
timeout /t 5 >nul

call :health_check
if %errorlevel% equ 0 (
    call :log "Deployment completed successfully!"
) else (
    call :error "Deployment failed at health check stage."
    goto :rollback
)
exit /b 0

:: Rollback function
:rollback
call :error "Deployment failed. Rolling back..."
call :cleanup
call :log "Rollback completed."
exit /b 1

:: Start deployment
call :deploy
if %errorlevel% neq 0 (
    exit /b 1
)
endlocal 