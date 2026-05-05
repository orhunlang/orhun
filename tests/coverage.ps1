param(
    [string]$Compiler = "g++",
    [string]$Output = "build/orhun_cov.exe",
    [string]$ReportDir = "coverage"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$outputDir = Split-Path -Parent $Output
if ($outputDir -and !(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}
if (!(Test-Path $ReportDir)) {
    New-Item -ItemType Directory -Path $ReportDir | Out-Null
}

Write-Host "[coverage] Building with instrumentation..."
& $Compiler -std=c++17 -O0 -g --coverage -Wall -Wextra -pedantic `
    main.cpp Lexer.cpp Parser.cpp Interpreter.cpp Chunk.cpp Compiler.cpp VM.cpp `
    -o $Output

Write-Host "[coverage] Running test suite..."
./tests/run_tests.ps1 -Compiler $Compiler -Output $Output

$gcovr = Get-Command gcovr -ErrorAction SilentlyContinue
if ($gcovr) {
    Write-Host "[coverage] Generating gcovr reports..."
    gcovr -r . --txt | Tee-Object -FilePath "$ReportDir/summary.txt" | Out-Null
    gcovr -r . --xml-pretty -o "$ReportDir/coverage.xml" | Out-Null
    gcovr -r . --html --html-details -o "$ReportDir/index.html" | Out-Null
    Get-Content "$ReportDir/summary.txt"
    $summary = Get-Content "$ReportDir/summary.txt" | Where-Object { $_ -match '^lines:' } | Select-Object -First 1
    if ($summary) {
        Write-Host "[coverage] summary $summary"
    }
}
else {
    Write-Host "[coverage] gcovr not found; falling back to gcov summary."
    gcov -o . main.cpp Lexer.cpp Parser.cpp Interpreter.cpp Chunk.cpp Compiler.cpp VM.cpp `
        | Tee-Object -FilePath "$ReportDir/gcov.txt" | Out-Null
    Get-Content "$ReportDir/gcov.txt" -Tail 20
    $summary = Get-Content "$ReportDir/gcov.txt" | Where-Object { $_ -match 'Lines executed' } | Select-Object -First 1
    if ($summary) {
        Write-Host "[coverage] summary $summary"
    }
}
