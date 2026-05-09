# OMNI Framework Publisher Script (PowerShell)
# Updates repository navigation links and package release information

Write-Host "🚀 OMNI Framework Publisher v2.1.0" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Check if git is installed
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git is not installed. Please install git first." -ForegroundColor Red
    exit 1
}

# Check if we're in a git repository
try {
    $null = git rev-parse --git-dir
} catch {
    Write-Host "❌ Not in a git repository. Initializing..." -ForegroundColor Yellow
    git init
} finally {
    Write-Host "✅ Git repository detected" -ForegroundColor Green
}

# Fetch the latest changes from remote
Write-Host "🔄 Fetching latest changes..." -ForegroundColor Cyan
git fetch origin

# Get current branch
$CURRENT_BRANCH = $(git branch --show-current)
if ([string]::IsNullOrEmpty($CURRENT_BRANCH)) {
    # If we're in detached HEAD state or no branch, default to main
    $CURRENT_BRANCH = "main"
}

Write-Host "📋 Current branch: $CURRENT_BRANCH" -ForegroundColor White

# Update the repository
Write-Host "📥 Pulling latest changes..." -ForegroundColor Cyan
$pullResult = git pull origin $CURRENT_BRANCH
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  No remote to pull from or error occurred, continuing..." -ForegroundColor Yellow
}

# Show status
Write-Host "📊 Repository status:" -ForegroundColor Cyan
git status

# Add all changes
Write-Host "📝 Adding all changes..." -ForegroundColor Cyan
git add .

# Check if there are changes to commit
$diffResult = git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    # No changes staged
    $diffResult2 = git diff --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Repository is already up to date" -ForegroundColor Green
        return
    }
}

Write-Host "📦 Creating new commit with updates..." -ForegroundColor Cyan

# Get timestamp for commit message
$TIMESTAMP = $(Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
$COMMIT_MSG = @"
Publish: Update repository navigation links and package release info

- Update version to 2.1.0
- Update repository URLs
- Update package release information
- Update documentation links
- Update registry information

Timestamp: $TIMESTAMP
"@

# Create the commit
git commit -m $COMMIT_MSG

# Push to remote
Write-Host "📤 Pushing changes to remote repository..." -ForegroundColor Cyan
git push origin $CURRENT_BRANCH

if ($LASTEXITCODE -eq 0) {
    Write-Host "🎉 Successfully published updates!" -ForegroundColor Green
    Write-Host "🔗 Main Repository: https://github.com/omni-framework/omni" -ForegroundColor Cyan
    Write-Host "📦 Package Registry: https://nexus.omniframework.dev" -ForegroundColor Cyan
    Write-Host "📚 Documentation: https://docs.omniframework.dev" -ForegroundColor Cyan
} else {
    Write-Host "❌ Failed to push changes" -ForegroundColor Red
    exit 1
}

Write-Host "✨ Publishing process completed!" -ForegroundColor Green