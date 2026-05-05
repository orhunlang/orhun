param(
    [string]$Destination = "artifacts/local"
)

$ErrorActionPreference = "Stop"

$root = (Get-Location).Path
$dest = Join-Path $root $Destination
New-Item -ItemType Directory -Path $dest -Force | Out-Null

$patterns = @("*.exe", "*.o", "*.obj", "*.pdb", "*.ilk", "*.log", "*.txt")
$excludePrefix = @(
    "tests\\cases\\",
    "docs\\",
    ".github\\",
    "tools\\",
    "build\\",
    "coverage\\",
    "artifacts\\"
)

function Is-Excluded([string]$relativePath) {
    foreach ($prefix in $excludePrefix) {
        if ($relativePath.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }
    return $false
}

$moved = 0
foreach ($pattern in $patterns) {
    Get-ChildItem -Path $root -Recurse -File -Filter $pattern | ForEach-Object {
        $full = $_.FullName
        $rel = $full.Substring($root.Length).TrimStart('\')
        if (Is-Excluded $rel) {
            return
        }
        $target = Join-Path $dest $rel
        $targetDir = Split-Path -Parent $target
        if (!(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path $full -Destination $target -Force
        $moved++
    }
}

Write-Host "moved_artifacts=$moved"

