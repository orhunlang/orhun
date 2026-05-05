param(
    [string]$JsonL = "build/benchmark_results.jsonl",
    [double]$MinP50 = 2.0,
    [double]$MinP90 = 1.5,
    [ValidateSet("suite", "per_case")]
    [string]$Mode = "suite",
    [string]$BaselineJsonL = "",
    [double]$MinBaselineP50Ratio = 0.0,
    [double]$MinBaselineP90Ratio = 0.0
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $JsonL)) {
    Write-Host "Benchmark dosyasi bulunamadi: $JsonL"
    exit 3
}

$failed = $false
$infrastructureFailed = $false
$lineNo = 0
$parsedLineCount = 0
$p50Liste = New-Object System.Collections.Generic.List[double]
$p90Liste = New-Object System.Collections.Generic.List[double]
$p50OranListe = New-Object System.Collections.Generic.List[double]
$p90OranListe = New-Object System.Collections.Generic.List[double]
$baselineMap = @{}
$budgetEtkin = $false

if ($BaselineJsonL -and ($MinBaselineP50Ratio -gt 0 -or $MinBaselineP90Ratio -gt 0)) {
    if (!(Test-Path $BaselineJsonL)) {
        Write-Host "Benchmark baseline dosyasi bulunamadi: $BaselineJsonL"
        exit 3
    }
    $baseLineNo = 0
    $baseSayisi = 0
    Get-Content $BaselineJsonL -Encoding utf8 | ForEach-Object {
        $baseLineNo++
        $line = $_.Trim()
        if ($line.Length -eq 0) { return }
        try {
            $obj = $line | ConvertFrom-Json
        } catch {
            Write-Host "[FAIL] Baseline satiri $baseLineNo JSON parse edilemedi."
            $infrastructureFailed = $true
            return
        }

        if (!($obj.PSObject.Properties.Name -contains "dosya") -or
            !($obj.PSObject.Properties.Name -contains "hizlanma") -or
            !($obj.hizlanma.PSObject.Properties.Name -contains "p50_x") -or
            !($obj.hizlanma.PSObject.Properties.Name -contains "p90_x")) {
            Write-Host "[FAIL] Baseline satiri $baseLineNo gerekli alanlari icermiyor."
            $infrastructureFailed = $true
            return
        }

        $dosya = [string]$obj.dosya
        if ([string]::IsNullOrWhiteSpace($dosya)) {
            Write-Host "[FAIL] Baseline satiri $baseLineNo dosya alani bos."
            $infrastructureFailed = $true
            return
        }

        $baselineMap[$dosya] = @{
            p50 = [double]$obj.hizlanma.p50_x
            p90 = [double]$obj.hizlanma.p90_x
        }
        $baseSayisi++
    }
    if ($baseSayisi -eq 0) {
        Write-Host "Benchmark baseline dosyasi bos veya gecersiz: $BaselineJsonL"
        exit 3
    }
    if (!$infrastructureFailed) {
        $budgetEtkin = $true
        Write-Host "[BUDGET] Baseline aktif: $BaselineJsonL (P50>=$MinBaselineP50Ratio, P90>=$MinBaselineP90Ratio)"
    }
}

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
    try {
        $obj = $line | ConvertFrom-Json
    } catch {
        Write-Host "[FAIL] Satir $lineNo JSON parse edilemedi."
        $infrastructureFailed = $true
        return
    }
    $parsedLineCount++

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

    $hasAbsP50 = $obj.hizlanma -and ($obj.hizlanma.PSObject.Properties.Name -contains "p50_x")
    $hasAbsP90 = $obj.hizlanma -and ($obj.hizlanma.PSObject.Properties.Name -contains "p90_x")
    if (!($hasAbsP50 -and $hasAbsP90)) {
        Write-Host "[FAIL] $dosya hizlanma.p50_x / hizlanma.p90_x alanlari eksik."
        $infrastructureFailed = $true
        return
    }
    $absP50 = [double]$obj.hizlanma.p50_x
    $absP90 = [double]$obj.hizlanma.p90_x

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

    if ($budgetEtkin) {
        if (!($baselineMap.ContainsKey($dosya))) {
            Write-Host "[FAIL] Baseline'da case bulunamadi: $dosya"
            $infrastructureFailed = $true
            return
        }
        $baseP50 = [double]$baselineMap[$dosya].p50
        $baseP90 = [double]$baselineMap[$dosya].p90
        if ($baseP50 -le 0 -or $baseP90 -le 0) {
            Write-Host "[FAIL] Baseline case degerleri sifir/negatif: $dosya"
            $infrastructureFailed = $true
            return
        }
        $oranP50 = $absP50 / $baseP50
        $oranP90 = $absP90 / $baseP90
        $p50OranListe.Add($oranP50)
        $p90OranListe.Add($oranP90)

        if ($Mode -eq "per_case") {
            $budgetFail = ($MinBaselineP50Ratio -gt 0 -and $oranP50 -lt $MinBaselineP50Ratio) -or
                          ($MinBaselineP90Ratio -gt 0 -and $oranP90 -lt $MinBaselineP90Ratio)
            if ($budgetFail) {
                Write-Host "[FAIL] $dosya budget orani P50=$oranP50 P90=$oranP90 (hedef: $MinBaselineP50Ratio / $MinBaselineP90Ratio)"
                $failed = $true
            } else {
                Write-Host "[OK] $dosya budget orani P50=$oranP50 P90=$oranP90"
            }
        } else {
            Write-Host "[BUDGET] $dosya oran P50=$oranP50 P90=$oranP90"
        }
    }
}

if ($parsedLineCount -eq 0) {
    Write-Host "Benchmark dosyasi bos veya gecersiz: $JsonL"
    exit 3
}

if ($Mode -eq "suite") {
    $suiteP50 = Get-Median $p50Liste
    $suiteP90 = Get-Median $p90Liste
    Write-Host "[SUITE] median P50=$suiteP50 P90=$suiteP90 (hedef: $MinP50 / $MinP90)"
    if ($suiteP50 -lt $MinP50 -or $suiteP90 -lt $MinP90) {
        $failed = $true
    }

    if ($budgetEtkin) {
        $suiteOranP50 = Get-Median $p50OranListe
        $suiteOranP90 = Get-Median $p90OranListe
        Write-Host "[SUITE-BUDGET] median ratio P50=$suiteOranP50 P90=$suiteOranP90 (hedef: $MinBaselineP50Ratio / $MinBaselineP90Ratio)"
        if (($MinBaselineP50Ratio -gt 0 -and $suiteOranP50 -lt $MinBaselineP50Ratio) -or
            ($MinBaselineP90Ratio -gt 0 -and $suiteOranP90 -lt $MinBaselineP90Ratio)) {
            $failed = $true
        }
    }
}

if ($infrastructureFailed) {
    Write-Host "Benchmark gate altyapi hatasi."
    exit 3
}

if ($failed) {
    Write-Host "Benchmark gate basarisiz."
    exit 2
}

Write-Host "Benchmark gate gecti."
exit 0
