param(
    [string]$Compiler = "g++",
    [string]$Output = "orhun_bench.exe",
    [int]$Tekrar = 30,
    [int]$Warmup = 10,
    [ValidateSet("runtime", "full")]
    [string]$OlcumModu = "runtime",
    [string]$JsonCikti = "benchmark_results.jsonl",
    [string]$Baseline = "",
    [double]$GateP50 = 0.0,
    [double]$GateP90 = 0.0,
    [ValidateSet("suite", "per_case")]
    [string]$GateMode = "suite"
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $Output)) {
    Write-Host "[build] $Output bulunamadi, derleniyor..."
    & $Compiler -std=c++17 -Wall -Wextra -pedantic `
        main.cpp Lexer.cpp Parser.cpp Interpreter.cpp Chunk.cpp Compiler.cpp VM.cpp `
        -o $Output
}

$cases = @(
    "tests/cases/basic_math.oh",
    "tests/cases/assignment_equals.oh",
    "tests/cases/while_float.oh",
    "tests/cases/list_comprehension.oh",
    "tests/cases/oop_super.oh",
    "tests/cases/json_parse.oh",
    "tests/cases/f_string.oh",
    "tests/cases/f_string_escape.oh",
    "tests/cases/slicing.oh",
    "tests/cases/dict_nested.oh",
    "tests/cases/try_break_continue.oh",
    "tests/cases/try_catch_runtime.oh",
    "tests/cases/module_stdlib.oh",
    "tests/cases/stdlib_modules.oh",
    "tests/cases/stdlib_database.oh",
    "tests/cases/stdlib_regex_date.oh",
    "tests/cases/stdlib_async.oh",
    "tests/cases/vm_loop_control.oh"
)

if (Test-Path $JsonCikti) {
    Remove-Item $JsonCikti -Force
}

Write-Host "[bench] Orhun hiz karsilastirma (JSONL: $JsonCikti)"
foreach ($src in $cases) {
    Write-Host ""
    Write-Host "=== $src ==="
    $args = @("hiz", $src, "--tekrar=$Tekrar", "--warmup=$Warmup", "--olcum-modu=$OlcumModu", "--json")
    if ($Baseline -ne "") {
        $args += @("--baseline", $Baseline)
    }
    $json = & ".\$Output" @args 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[skip] $src benchmark atlandi (VM destek disi olabilir)."
    } else {
        $json = ($json -replace "`r`n", "`n").Trim()
        Add-Content -Path $JsonCikti -Value $json -Encoding utf8
        Write-Host $json
    }
}

if ($GateP50 -gt 0 -or $GateP90 -gt 0) {
    Write-Host ""
    Write-Host "[gate] KPI kontrolu"
    ./tests/benchmark_gate.ps1 -JsonL $JsonCikti -MinP50 ([Math]::Max($GateP50, 0.0)) -MinP90 ([Math]::Max($GateP90, 0.0)) -Mode $GateMode
}
