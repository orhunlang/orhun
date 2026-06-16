param(
    [string]$Compiler = "g++",
    [string]$Output = "build/orhun_test.exe",
    [int]$TimeoutSeconds = 10,
    [switch]$SkipBuild
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$outputDir = Split-Path -Parent $Output
if ($outputDir -and !(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

if ($SkipBuild) {
    Write-Host "[1/3] Mevcut binary kullaniliyor..."
    if (!(Test-Path $Output)) {
        throw "Mevcut test binary bulunamadi: $Output"
    }
}
else {
    Write-Host "[1/3] Derleniyor..."
    & $Compiler -std=c++17 -Wall -Wextra -pedantic `
        main.cpp Lexer.cpp Parser.cpp Interpreter.cpp Chunk.cpp Compiler.cpp VM.cpp `
        -o $Output
    if ($LASTEXITCODE -ne 0) {
        throw "Derleme basarisiz."
    }
}

$RepoRoot = (Resolve-Path ".").Path
$ResolvedOutput = (Resolve-Path $Output).Path
$StdLibPath = (Resolve-Path "StdLib").Path
$StdLibSearchPath = "$StdLibPath;$RepoRoot"
$WorkRoot = Join-Path $RepoRoot "build/test-work/run-tests-$PID"
if (!(Test-Path $WorkRoot)) {
    New-Item -ItemType Directory -Path $WorkRoot -Force | Out-Null
}

function Case-WorkDir($case) {
    $name = Split-Path -Leaf $case
    $path = Join-Path $WorkRoot $name
    if (!(Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
    return $path
}

function Run-Orhun($exe, $argsList, [hashtable]$EnvVars = @{}, [string]$WorkDir = $RepoRoot) {
    $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    $pinfo.FileName = $exe
    $pinfo.Arguments = $argsList
    $pinfo.WorkingDirectory = $WorkDir
    $pinfo.RedirectStandardOutput = $true
    $pinfo.RedirectStandardError = $true
    $pinfo.UseShellExecute = $false
    $pinfo.StandardOutputEncoding = [System.Text.Encoding]::UTF8
    $pinfo.StandardErrorEncoding = [System.Text.Encoding]::UTF8
    $pinfo.Environment["ORHUN_STDLIB_PATH"] = $StdLibSearchPath
    foreach ($entry in $EnvVars.GetEnumerator()) {
        $pinfo.Environment[$entry.Key] = [string]$entry.Value
    }
    
    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $pinfo
    $p.Start() | Out-Null
    $stdoutTask = $p.StandardOutput.ReadToEndAsync()
    $stderrTask = $p.StandardError.ReadToEndAsync()

    $timeoutMs = [Math]::Max(1, $TimeoutSeconds) * 1000
    if (-not $p.WaitForExit($timeoutMs)) {
        try {
            $p.Kill()
            $p.WaitForExit()
        }
        catch {
        }
        $stdout = $stdoutTask.GetAwaiter().GetResult()
        $stderr = $stderrTask.GetAwaiter().GetResult()
        return ($stdout + $stderr + "Hata: test zaman asimi (${TimeoutSeconds}s)")
    }

    $stdout = $stdoutTask.GetAwaiter().GetResult()
    $stderr = $stderrTask.GetAwaiter().GetResult()

    $combined = $stdout + $stderr
    if ($p.ExitCode -ne 0 -and $p.ExitCode -ne 1) {
        if ($combined.Length -gt 0 -and -not $combined.EndsWith("`n")) {
            $combined += "`n"
        }
        $combined += "Hata: beklenmeyen cikis kodu ($($p.ExitCode))"
    }

    return $combined
}

$cases = Get-ChildItem "tests/cases" -Filter "*.expected.txt" |
    ForEach-Object { $_.FullName -replace "\.expected\.txt$", "" } |
    ForEach-Object { $_ -replace "\\", "/" } |
    Sort-Object |
    Where-Object { Test-Path "$_.oh" }

$strictCase = (Join-Path (Resolve-Path "tests/cases").Path "turkce_kati_alias") -replace "\\", "/"
$cases = $cases | Where-Object { $_ -ne $strictCase }

if ($env:OS -ne "Windows_NT") {
    $cases = $cases | Where-Object {
        $_ -ne "tests/cases/ffi_kernel32" -and
        $_ -ne "tests/cases/ffi_text" -and
        $_ -ne "tests/cases/ffi_symbol" -and
        $_ -ne "tests/cases/ffi_tanimli_kernel32" -and
        $_ -ne "tests/cases/ffi_dis_islev"
    }
}

$failed = $false

Write-Host "[2/3] Testler calisiyor..."
foreach ($case in $cases) {
    $src = "$case.oh"
    $expectedPath = "$case.expected.txt"
    $srcPath = (Resolve-Path $src).Path
    $caseWorkDir = Case-WorkDir $case

    $actual = Run-Orhun $ResolvedOutput "`"$srcPath`"" @{} $caseWorkDir
    $actual = $actual -replace "`r`n", "`n"
    $actual = $actual.TrimEnd("`n")

    $expected = Get-Content $expectedPath -Raw -Encoding utf8
    $expected = $expected -replace "`r`n", "`n"
    $expected = $expected.TrimEnd("`n")

    if ($actual -ne $expected) {
        Write-Host ""
        Write-Host "[HATA] $src"
        Write-Host "Beklenen:"
        Write-Host $expected
        Write-Host "Alinan:"
        Write-Host $actual
        $failed = $true
    }
    else {
        Write-Host "[OK] $src"
    }
}

if ((Test-Path "$strictCase.oh") -and (Test-Path "$strictCase.expected.txt")) {
    $src = "$strictCase.oh"
    $expectedPath = "$strictCase.expected.txt"
    $srcPath = (Resolve-Path $src).Path
    $caseWorkDir = Case-WorkDir $strictCase

    $actual = Run-Orhun $ResolvedOutput "`"$srcPath`"" @{ ORHUN_TURKCE_KATI = "1" } $caseWorkDir
    $actual = $actual -replace "`r`n", "`n"
    $actual = $actual.TrimEnd("`n")

    $expected = Get-Content $expectedPath -Raw -Encoding utf8
    $expected = $expected -replace "`r`n", "`n"
    $expected = $expected.TrimEnd("`n")

    if ($actual -ne $expected) {
        Write-Host ""
        Write-Host "[HATA] $src (ORHUN_TURKCE_KATI=1)"
        Write-Host "Beklenen:"
        Write-Host $expected
        Write-Host "Alinan:"
        Write-Host $actual
        $failed = $true
    }
    else {
        Write-Host "[OK] $src (ORHUN_TURKCE_KATI=1)"
    }
}

Write-Host "[3/3] Sonuc..."
if ($failed) {
    throw "Bazi testler basarisiz."
}

Write-Host "Tum testler basarili."
