param(
    [string]$JsonL = "benchmark_results.jsonl",
    [double]$MinP50 = 2.0,
    [double]$MinP90 = 1.5,
    [ValidateSet("suite", "per_case")]
    [string]$Mode = "suite"
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $JsonL)) {
    throw "Benchmark dosyasi bulunamadi: $JsonL"
}

$failed = $false
$lineNo = 0
$p50Liste = New-Object System.Collections.Generic.List[double]
$p90Liste = New-Object System.Collections.Generic.List[double]

function Get-Median([System.Collections.Generic.List[double]]$values) {
    if ($values.Count -eq 0) {
        return 0.0
    }
    $arr = $values.ToArray()
    [Array]::Sort($arr)
    $mid = [int]([Math]::Floor($arr.Length / 2))
    if (($arr.Length % 2) -eq 1) {
        return $arr[$mid]
    }
    return ($arr[$mid - 1] + $arr[$mid]) / 2.0
}

Get-Content $JsonL -Encoding utf8 | ForEach-Object {
    $lineNo++
    $line = $_.Trim()
    if ($line.Length -eq 0) { return }
    $obj = $line | ConvertFrom-Json

    $dosya = $obj.dosya
    $p50 = $null
    $p90 = $null

    $gateHasP50 = $obj.gate -and ($obj.gate.PSObject.Properties.Name -contains "p50_oran")
    $gateHasP90 = $obj.gate -and ($obj.gate.PSObject.Properties.Name -contains "p90_oran")
    if ($gateHasP50 -and $gateHasP90) {
        $p50 = [double]$obj.gate.p50_oran
        $p90 = [double]$obj.gate.p90_oran
    } else {
        $p50 = [double]$obj.hizlanma.p50_x
        $p90 = [double]$obj.hizlanma.p90_x
    }

    $p50Liste.Add($p50)
    $p90Liste.Add($p90)

    if ($Mode -eq "per_case") {
        if ($p50 -lt $MinP50 -or $p90 -lt $MinP90) {
            Write-Host "[FAIL] $dosya P50=$p50 P90=$p90 (hedef: $MinP50 / $MinP90)"
            $failed = $true
        } else {
            Write-Host "[OK] $dosya P50=$p50 P90=$p90"
        }
    } else {
        Write-Host "[INFO] $dosya P50=$p50 P90=$p90"
    }
}

if ($Mode -eq "suite") {
    $suiteP50 = Get-Median $p50Liste
    $suiteP90 = Get-Median $p90Liste
    Write-Host "[SUITE] median P50=$suiteP50 P90=$suiteP90 (hedef: $MinP50 / $MinP90)"
    if ($suiteP50 -lt $MinP50 -or $suiteP90 -lt $MinP90) {
        $failed = $true
    }
}

if ($failed) {
    throw "Benchmark gate basarisiz."
}

Write-Host "Benchmark gate gecti."
