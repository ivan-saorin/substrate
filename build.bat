@echo off
REM Build script for substrate MCP Docker image

echo Building substrate MCP Docker image...

REM Build the Docker image
docker build -t substrate-mcp:latest .

if %ERRORLEVEL% == 0 (
    echo.
    echo Build successful!
    echo.
    echo To test the image:
    echo docker run --rm -it -v %cd%\docs:/app/docs:ro substrate-mcp:latest
    echo.
    echo To use in Claude Desktop, add the configuration to cline_mcp_settings.json
) else (
    echo.
    echo Build failed!
    exit /b 1
)
