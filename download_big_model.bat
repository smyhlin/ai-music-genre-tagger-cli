@echo off
setlocal enabledelayedexpansion

:: Configuration Variables
set "GITHUB_URL=https://github.com/jordipons/musicnn/tree/master/musicnn/MSD_musicnn_big"
set "RAW_BASE_URL=https://raw.githubusercontent.com/jordipons/musicnn/master"
set "API_URL=https://api.github.com/repos/jordipons/musicnn/contents/musicnn/MSD_musicnn_big"
set "FOLDER_NAME=musicnn_tagger/MSD_musicnn_big"

:: Define base directory
set "BASE_DIR=%CD%"
set "DEST_DIR=%BASE_DIR%\%FOLDER_NAME%"

:: Create target directory
if not exist "!DEST_DIR!" (
    echo Creating directory: !DEST_DIR!
    mkdir "!DEST_DIR!" 2>nul || (
        echo Error: Failed to create directory.
        exit /b 1
    )
)

:: Create PowerShell script with enhanced progress tracking
echo $ProgressPreference = 'Continue' > "%TEMP%\download_github.ps1"
echo $apiUrl = '%API_URL%' >> "%TEMP%\download_github.ps1"
echo $rawBaseUrl = '%RAW_BASE_URL%' >> "%TEMP%\download_github.ps1"
echo $destPath = '%DEST_DIR%' >> "%TEMP%\download_github.ps1"
echo. >> "%TEMP%\download_github.ps1"

:: Add Progress Bar Function
echo function Show-ProgressBar { >> "%TEMP%\download_github.ps1"
echo     param ( >> "%TEMP%\download_github.ps1"
echo         [int]$PercentComplete, >> "%TEMP%\download_github.ps1"
echo         [string]$Status, >> "%TEMP%\download_github.ps1"
echo         [string]$CurrentOperation >> "%TEMP%\download_github.ps1"
echo     ) >> "%TEMP%\download_github.ps1"
echo     Write-Progress -Activity $Status -Status $CurrentOperation -PercentComplete $PercentComplete >> "%TEMP%\download_github.ps1"
echo } >> "%TEMP%\download_github.ps1"
echo. >> "%TEMP%\download_github.ps1"

:: Enhanced Download Function with Progress
echo function Download-GithubFile { >> "%TEMP%\download_github.ps1"
echo     param( >> "%TEMP%\download_github.ps1"
echo         [string]$url, >> "%TEMP%\download_github.ps1"
echo         [string]$path, >> "%TEMP%\download_github.ps1"
echo         [int]$currentFile, >> "%TEMP%\download_github.ps1"
echo         [int]$totalFiles >> "%TEMP%\download_github.ps1"
echo     ) >> "%TEMP%\download_github.ps1"
echo     try { >> "%TEMP%\download_github.ps1"
echo         $directory = Split-Path -Parent $path >> "%TEMP%\download_github.ps1"
echo         if (-not (Test-Path $directory)) { >> "%TEMP%\download_github.ps1"
echo             New-Item -ItemType Directory -Force -Path $directory ^| Out-Null >> "%TEMP%\download_github.ps1"
echo         } >> "%TEMP%\download_github.ps1"
echo         $filename = Split-Path $path -Leaf >> "%TEMP%\download_github.ps1"
echo         $percentComplete = [math]::Round(($currentFile / $totalFiles) * 100) >> "%TEMP%\download_github.ps1"
echo         $webClient = New-Object System.Net.WebClient >> "%TEMP%\download_github.ps1"
echo         $webClient.Headers.Add("User-Agent", "PowerShell Script") >> "%TEMP%\download_github.ps1"
echo         Show-ProgressBar -PercentComplete $percentComplete -Status "Downloading Files" -CurrentOperation "File $currentFile of $totalFiles : $filename" >> "%TEMP%\download_github.ps1"
echo         $webClient.DownloadFile($url, $path) >> "%TEMP%\download_github.ps1"
echo         Write-Host "[OK] Downloaded: $filename" -ForegroundColor Green >> "%TEMP%\download_github.ps1"
echo     } catch { >> "%TEMP%\download_github.ps1"
echo         Write-Host "[ERROR] Failed to download: $filename" -ForegroundColor Red >> "%TEMP%\download_github.ps1"
echo         Write-Host $_.Exception.Message -ForegroundColor Red >> "%TEMP%\download_github.ps1"
echo     } >> "%TEMP%\download_github.ps1"
echo } >> "%TEMP%\download_github.ps1"

:: Main Execution Block with Enhanced Error Handling
echo try { >> "%TEMP%\download_github.ps1"
echo     Write-Host "Initializing download process..." -ForegroundColor Cyan >> "%TEMP%\download_github.ps1"
echo     $response = Invoke-RestMethod -Uri $apiUrl -UseBasicParsing >> "%TEMP%\download_github.ps1"
echo     $files = $response ^| Where-Object { $_.type -eq "file" } >> "%TEMP%\download_github.ps1"
echo     $totalFiles = $files.Count >> "%TEMP%\download_github.ps1"
echo     Write-Host "Found $totalFiles files to download." -ForegroundColor Cyan >> "%TEMP%\download_github.ps1"
echo     $currentFile = 0 >> "%TEMP%\download_github.ps1"
echo     foreach ($item in $files) { >> "%TEMP%\download_github.ps1"
echo         $currentFile++ >> "%TEMP%\download_github.ps1"
echo         $downloadUrl = $item.download_url >> "%TEMP%\download_github.ps1"
echo         $localPath = Join-Path $destPath $item.name >> "%TEMP%\download_github.ps1"
echo         Download-GithubFile -url $downloadUrl -path $localPath -currentFile $currentFile -totalFiles $totalFiles >> "%TEMP%\download_github.ps1"
echo     } >> "%TEMP%\download_github.ps1"
echo     Write-Progress -Activity "Downloading Files" -Completed >> "%TEMP%\download_github.ps1"
echo     Write-Host "`nDownload process completed successfully." -ForegroundColor Green >> "%TEMP%\download_github.ps1"
echo } catch { >> "%TEMP%\download_github.ps1"
echo     Write-Host "Critical Error: Failed to process GitHub directory contents." -ForegroundColor Red >> "%TEMP%\download_github.ps1"
echo     Write-Host $_.Exception.Message -ForegroundColor Red >> "%TEMP%\download_github.ps1"
echo     exit 1 >> "%TEMP%\download_github.ps1"
echo } >> "%TEMP%\download_github.ps1"

:: Execute PowerShell script
powershell -ExecutionPolicy Bypass -File "%TEMP%\download_github.ps1"
if %errorlevel% neq 0 (
    echo Error: Download process failed.
    del "%TEMP%\download_github.ps1"
    exit /b 1
)

:: Cleanup
del "%TEMP%\download_github.ps1"

echo.
echo Operation completed successfully.
echo Files downloaded to: !DEST_DIR!
endlocal