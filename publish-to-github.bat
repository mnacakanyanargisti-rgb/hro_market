@echo off
setlocal
cd /d "%~dp0"
where git >nul 2>&1
if errorlevel 1 (
  echo Git is not installed. Install Git for Windows from https://git-scm.com/download/win
  pause
  exit /b 1
)
echo This will upload the restored Hro Market to:
echo https://github.com/mnacakanyanargisti-rgb/hro_market
choice /M "Continue only if you have already created this repository on GitHub"
if errorlevel 2 exit /b 0
if not exist .git git init
git branch -M main
git remote remove origin >nul 2>&1
git remote add origin https://github.com/mnacakanyanargisti-rgb/hro_market.git
git add .
git commit -m "Restore original Emergent Hro Market frontend"
git push -u origin main
if errorlevel 1 (
  echo The push failed. Confirm the repository exists and sign in to GitHub.
  pause
  exit /b 1
)
echo Done. GitHub may require enabling Pages or linking Netlify/Cloudflare Pages.
pause
