param(
    [string]$Compiler = "g++",
    [string]$Output = "build/orhun_test.exe"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$outputDir = Split-Path -Parent $Output
if ($outputDir -and !(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

if (!(Test-Path $Output)) {
    Write-Host "[vm-parity] Binary not found, building: $Output"
    & $Compiler -std=c++17 -Wall -Wextra -pedantic `
        main.cpp Lexer.cpp Parser.cpp Interpreter.cpp Chunk.cpp Compiler.cpp VM.cpp `
        -o $Output
}

function Run-Orhun($exe, $argsList) {
    $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    $pinfo.FileName = $exe
    $pinfo.Arguments = $argsList
    $pinfo.RedirectStandardOutput = $true
    $pinfo.RedirectStandardError = $true
    $pinfo.UseShellExecute = $false
    $pinfo.StandardOutputEncoding = [System.Text.Encoding]::UTF8
    $pinfo.StandardErrorEncoding = [System.Text.Encoding]::UTF8

    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $pinfo
    $p.Start() | Out-Null

    $stdout = $p.StandardOutput.ReadToEnd()
    $stderr = $p.StandardError.ReadToEnd()
    $p.WaitForExit()

    return $stdout + $stderr
}

$cases = Get-ChildItem "tests/cases" -Filter "*.expected.txt" |
    ForEach-Object { $_.FullName -replace "\.expected\.txt$", "" } |
    ForEach-Object { $_ -replace "\\", "/" } |
    Sort-Object |
    Where-Object { Test-Path "$_.oh" }

if ($env:OS -ne "Windows_NT") {
    $cases = $cases | Where-Object {
        $_ -ne "tests/cases/ffi_kernel32" -and
        $_ -ne "tests/cases/ffi_text" -and
        $_ -ne "tests/cases/ffi_symbol" -and
        $_ -ne "tests/cases/ffi_tanimli_kernel32" -and
        $_ -ne "tests/cases/ffi_dis_islev"
    }
}

$ok = 0
$fail = 0
foreach ($case in $cases) {
    $src = "$case.oh"
    $expectedPath = "$case.expected.txt"

    $actual = Run-Orhun ".\$Output" "vm-kati $src"
    $actual = $actual -replace "`r`n", "`n"
    $actual = $actual.TrimEnd("`n")

    $expected = Get-Content $expectedPath -Raw -Encoding utf8
    $expected = $expected -replace "`r`n", "`n"
    $expected = $expected.TrimEnd("`n")

    if ($actual -ne $expected) {
        Write-Host "[VM-FAIL] $src"
        Write-Host "Beklenen:"
        Write-Host $expected
        Write-Host "Alinan:"
        Write-Host $actual
        $fail++
    }
    else {
        Write-Host "[VM-OK] $src"
        $ok++
    }
}

Write-Host "vm_parity_ok=$ok"
Write-Host "vm_parity_fail=$fail"
if ($fail -gt 0) {
    throw "VM parity basarisiz."
}
