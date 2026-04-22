# GitHub Account Check Script

Write-Host "=== Git User Configuration ===" -ForegroundColor Cyan
Write-Host "Name: " -NoNewline
git config user.name
Write-Host "Email: " -NoNewline
git config user.email

Write-Host "`n=== Remote Repository ===" -ForegroundColor Cyan
git remote -v

Write-Host "`n=== GitHub CLI Authentication ===" -ForegroundColor Cyan
try {
    gh auth status
} catch {
    Write-Host "GitHub CLI (gh) is not installed or not in PATH" -ForegroundColor Yellow
}
