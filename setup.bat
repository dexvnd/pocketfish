@echo off
echo Running Pocketfish setup...
echo.

python setup.py

echo.
echo Creating start.bat...

(
    echo @echo off
    echo del "%~dp0setup.bat"
    echo python "%~dp0main.py"
) > start.bat

echo.
echo Setup complete! Run start.bat to launch Pocketfish.
pause