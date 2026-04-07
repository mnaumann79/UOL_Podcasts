@echo off
:: Scaffold a new podcast course folder
:: Usage: start_podcast.bat <course_code> "<title>" <source_folder>
:: Example: start_podcast.bat cm3035 "CM3035: Advanced Web Development" d:\audio\cm3035

if "%~1"=="" goto usage
if "%~2"=="" goto usage
if "%~3"=="" goto usage

set COURSE=%~1
set TITLE=%~2
set SOURCE=%~3
set REPO=mnaumann79/UOL_Podcasts

echo === Podcast Scaffolder ===
echo Course: %COURSE%
echo Title:  %TITLE%
echo Source: %SOURCE%
echo.

if not exist "%SOURCE%" (
    echo Error: Source folder not found: %SOURCE%
    exit /b 1
)

:: Create course folder
mkdir %COURSE% 2>nul
echo Created folder: %COURSE%\

:: Copy audio files
for %%f in ("%SOURCE%\*.mp3") do copy "%%f" "%COURSE%\" >nul
for %%f in ("%SOURCE%\*.m4a") do copy "%%f" "%COURSE%\" >nul
echo Copied audio files to %COURSE%\

:: Copy artwork if present
for %%e in (png jpg jpeg) do (
    if exist "%SOURCE%\artwork.%%e" copy "%SOURCE%\artwork.%%e" "%COURSE%\" >nul && echo Copied artwork to %COURSE%\ && goto :artwork_done
)
:artwork_done

:: Scaffold episodes.json
python generate_episodes_json.py --folder %COURSE% --course %COURSE%

echo.
echo === Next Steps ===
echo 1. Edit %COURSE%\episodes.json to add titles, descriptions, and durations
echo.
echo 2. Commit and push:
echo    git add %COURSE%\
echo    git commit -m "Add %COURSE%"
echo    git tag %COURSE%\v1
echo    git push origin main %COURSE%\v1
echo.
echo 3. Create GitHub release:
echo    gh release create %COURSE%\v1 --title "%TITLE% v1"
echo.
echo 4. Generate RSS feed:
echo    python generate_podcast_rss.py ---
echo     --folder "%%COURSE%%" ---
echo     --repo "%REPO%" ---
echo     --tag "%COURSE%\v1" ---
echo     --title "%TITLE%" ---
echo     --output "%%COURSE%%\podcast.rss"
echo.
echo 5. Subscribe at:
echo    https://github.com/%REPO%/releases/download/%COURSE%/v1/podcast.rss
goto :end

:usage
echo Usage: start_podcast.bat ^<course_code^> "^<title^>" ^<source_folder^>
echo Example: start_podcast.bat cm3035 "CM3035: Advanced Web Development" d:\audio\cm3035

:end
