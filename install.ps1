# Orhun one-line installer (Windows)
#
#   irm https://raw.githubusercontent.com/orhunlang/orhun/v1.0.0/install.ps1 | iex
#
# Downloads the matching GitHub Release runtime archive, verifies SHA-256,
# installs under %LOCALAPPDATA%\orhun, and prepends that directory to PATH.

[CmdletBinding()]
param(
    [string]$Version = $(if ($env:ORHUN_VERSION) { $env:ORHUN_VERSION } else { "1.0.0" }),
    [string]$Repo = $(if ($env:ORHUN_REPO) { $env:ORHUN_REPO } else { "orhunlang/orhun" }),
    [string]$Prefix = $(if ($env:ORHUN_PREFIX) { $env:ORHUN_PREFIX } else { Join-Path $env:LOCALAPPDATA "orhun" }),
    [ValidateSet("runtime", "compiler")]
    [string]$Artifact = $(if ($env:ORHUN_ARTIFACT) { $env:ORHUN_ARTIFACT } else { "runtime" })
)

$ErrorActionPreference = "Stop"

function Write-Info([string]$Message) {
    Write-Host "==> $Message"
}

function Get-PlatformName {
    $arch = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString().ToLowerInvariant()
    switch ($arch) {
        "x64" { return "windows-x64" }
        "arm64" { return "windows-arm64" }
        "x86" { return "windows-x86" }
        default { throw "unsupported arch: $arch" }
    }
}

$platform = Get-PlatformName
$archive = "orhun-$Artifact-$Version-$platform.zip"
$base = "https://github.com/$Repo/releases/download/v$Version"
$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("orhun-install-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tmp | Out-Null

try {
    Write-Info "Downloading $archive"
    $archivePath = Join-Path $tmp $archive
    Invoke-WebRequest -Uri "$base/$archive" -OutFile $archivePath

    $sumsPath = Join-Path $tmp "SHA256SUMS"
    $haveSums = $false
    try {
        Invoke-WebRequest -Uri "$base/SHA256SUMS" -OutFile $sumsPath
        $haveSums = Test-Path $sumsPath
    } catch {
        Write-Info "SHA256SUMS unavailable; skipping checksum verification"
    }

    if ($haveSums) {
        Write-Info "Verifying SHA-256"
        $expected = $null
        foreach ($line in Get-Content $sumsPath) {
            $parts = $line.Trim() -split "\s+"
            if ($parts.Count -ge 2) {
                $name = $parts[-1].TrimStart("*")
                if ($name -eq $archive) {
                    $expected = $parts[0].ToLowerInvariant()
                }
            }
        }
        if (-not $expected) {
            throw "SHA256SUMS entry not found for $archive"
        }
        $actual = (Get-FileHash -Path $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actual -ne $expected) {
            throw "SHA-256 mismatch for $archive"
        }
    }

    Write-Info "Extracting to $Prefix"
    if (Test-Path $Prefix) {
        Remove-Item -Recurse -Force $Prefix
    }
    New-Item -ItemType Directory -Path $Prefix | Out-Null
    Expand-Archive -Path $archivePath -DestinationPath $Prefix -Force

    $exe = Join-Path $Prefix "orhun.exe"
    if (-not (Test-Path $exe)) {
        $candidate = Get-ChildItem -Path $Prefix -Recurse -Filter orhun.exe | Select-Object -First 1
        if (-not $candidate) {
            throw "orhun.exe not found in archive"
        }
        $exe = $candidate.FullName
    }

    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if (-not $userPath) {
        $userPath = ""
    }
    $parts = $userPath -split ";" | Where-Object { $_ -and $_.Trim() }
    if ($parts -notcontains $Prefix) {
        $newPath = (@($Prefix) + $parts) -join ";"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        $env:Path = "$Prefix;$env:Path"
        Write-Info "Prepended $Prefix to user PATH"
    } else {
        Write-Info "$Prefix already on user PATH"
    }

    Write-Info "Installed: $exe"
    & $exe surum
    Write-Info "Done. Run: orhun yardim"
} finally {
    if (Test-Path $tmp) {
        Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
    }
}
