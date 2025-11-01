# GitHub Setup Instructions

Your code has been committed locally. Follow these steps to push to GitHub:

## Step 1: Create a New Repository on GitHub

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Fill in the details:
   - **Repository name**: `billing-system` (or any name you prefer)
   - **Description**: "Flask-based billing system with product management, invoice generation, and purchase history"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click "Create repository"

## Step 2: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these commands:

### Option A: If you haven't set up remote yet
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
git branch -M main
git push -u origin main
```

### Option B: If the default branch is "master" (as in your case)
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
git branch -M main
git push -u origin main
```

**OR** if your GitHub repo uses "master":
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
git push -u origin master
```

## Step 3: Replace Placeholders

Replace:
- `YOUR_USERNAME` with your GitHub username
- `YOUR_REPOSITORY_NAME` with the repository name you created

## Example Commands:

If your GitHub username is `john` and repository name is `billing-system`:
```bash
git remote add origin https://github.com/john/billing-system.git
git branch -M main
git push -u origin main
```

## Authentication

If prompted for authentication:
- **Username**: Your GitHub username
- **Password**: Use a Personal Access Token (not your GitHub password)
  - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
  - Generate new token with `repo` scope
  - Copy and use it as password

## Files Included:

✅ app.py - Main Flask application  
✅ README.md - Complete documentation  
✅ requirements.txt - Dependencies  
✅ templates/ - All HTML templates  
✅ .gitignore - Excludes database and unnecessary files  

## Files Excluded (by .gitignore):

❌ billing.db - Database file (will be created on first run)  
❌ __pycache__/ - Python cache  
❌ Other temporary files  

---

**Note**: The database file (billing.db) is excluded from Git because:
1. It contains local data that will be different for each installation
2. It will be automatically created when the app runs for the first time
3. It's listed in .gitignore to prevent accidental commits

