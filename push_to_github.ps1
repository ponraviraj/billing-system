# PowerShell script to push to GitHub
# Replace YOUR_REPO_NAME with your actual repository name

$repoName = "billing-system"  # Change this to your repository name
$username = "ponraviraj"       # Your GitHub username

Write-Host "Setting up remote and pushing to GitHub..." -ForegroundColor Green

# Add remote (if not already added)
git remote remove origin 2>$null
git remote add origin "https://github.com/$username/$repoName.git"

# Rename branch to main (GitHub's default)
git branch -M main

# Push to GitHub
Write-Host "`nPushing code to GitHub..." -ForegroundColor Yellow
git push -u origin main

Write-Host "`nDone! Check your GitHub repository: https://github.com/$username/$repoName" -ForegroundColor Green

