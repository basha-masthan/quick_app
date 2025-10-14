@echo off

REM Set API environment variables for Windows
set GOOGLE_MAPS_API_KEY=AIzaSyDicdx-eDzQ0MeWEmdN_IjLSiXo16HZ2-M
set ANTHROPIC_BASE_URL=https://agentrouter.org/
set ANTHROPIC_AUTH_TOKEN=sk-W0eGY5tZp8XFLxycNNxrgMRNc1jNwR2OAKGe7eXhe3mx05np
set ANTHROPIC_API_KEY=sk-W0eGY5tZp8XFLxycNNxrgMRNc1jNwR2OAKGe7eXhe3mx05np

echo Environment variables set for API integration
echo GOOGLE_MAPS_API_KEY: [SET]
echo ANTHROPIC_API_KEY: [SET]
echo.
echo To run the Django server with these variables:
echo call set_env.bat && python manage.py runserver

pause