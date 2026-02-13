param(
    [string]$JsonL = "benchmark_results.jsonl",
    [double]$MinP50 = 2.0,
    [double]$MinP90 = 1.5
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $JsonL)) {
    throw "Benchmark dosyasi bulunamadi: $JsonL"
}

$failed = $false
$lineNo = 0
Get-Content $JsonL -Encoding utf8 | ForEach-Object {
    $lineNo++
    $line = $_.Trim()
    if ($line.Length -eq 0) { return }
    $obj = $line | ConvertFrom-Json

    $dosya = $obj.dosya
    $p50 = $null
    $p90 = $null

    if ($obj.gate -and $obj.gate.p50_oran -and $obj.gate.p90_oran) {
        $p50 = [double]$obj.gate.p50_oran
        $p90 = [double]$obj.gate.p90_oran
    } else {
        $p50 = [double]$obj.hizlanma.p50_x
        $p90 = [double]$obj.hizlanma.p90_x
    }

    if ($p50 -lt $MinP50 -or $p90 -lt $MinP90) {
        Write-Host "[FAIL] $dosya P50=$p50 P90=$p90 (hedef: $MinP50 / $MinP90)"
        $failed = $true
    } else {
        Write-Host "[OK] $dosya P50=$p50 P90=$p90"
    }
}

if ($failed) {
    throw "Benchmark gate basarisiz."
}

Write-Host "Benchmark gate gecti."
