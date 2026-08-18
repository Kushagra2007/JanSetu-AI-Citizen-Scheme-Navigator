<#
Publish the current source tree to an already-created empty Git repository.
Usage: .\scripts\push-new-repo.ps1 https://github.com/your-name/jansetu.git
#>
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$RepositoryUrl
)

$ErrorActionPreference = 'Stop'

git rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -ne 0) {
    throw 'Run this script from inside the JanSetu Git repository.'
}

git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    throw 'There are already staged changes. Review or commit them before running this script.'
}

# Add source changes, then remove previously tracked generated files from the
# new repository's index. --cached keeps every local file on disk.
git add -A
git ls-files | Where-Object {
    $_ -match '(^|/)__pycache__/|^\.pytest_cache/|^venv/|^\.venv/|^env/|\.(pyc|pyo|pyd|db|sqlite|sqlite3)$|^\.env$'
} | ForEach-Object {
    git rm --cached --ignore-unmatch -- $_
}

git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m 'Prepare JanSetu for publication'
}

git branch -M main
git remote get-url origin *> $null
if ($LASTEXITCODE -eq 0) {
    git remote set-url origin $RepositoryUrl
} else {
    git remote add origin $RepositoryUrl
}
git push -u origin main
