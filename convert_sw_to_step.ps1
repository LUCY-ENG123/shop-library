param(
  [Parameter(Mandatory=$true)]
  [string]$Folder
)

# ---- SolidWorks constants ----
$swDocPART = 1
$swOpenDocOptions_Silent = 1
$swSaveAsOptions_Silent = 2

function Convert-PartToStep($swApp, $fullPath) {
  $base = [System.IO.Path]::GetFileNameWithoutExtension($fullPath)
  $outStep = Join-Path (Split-Path $fullPath -Parent) ($base + ".step")

  # Skip if STEP already exists
  if (Test-Path $outStep) {
    Write-Host "SKIP (STEP exists): $outStep"
    return
  }

  $errors = 0
  $warnings = 0

  $model = $swApp.OpenDoc6(
    $fullPath,
    $swDocPART,
    $swOpenDocOptions_Silent,
    "",
    [ref]$errors,
    [ref]$warnings
  )

  if ($null -eq $model) {
    Write-Host "FAIL open: $fullPath"
    return
  }

  $saveErrors = 0
  $saveWarnings = 0
  $ok = $model.Extension.SaveAs(
    $outStep,
    0,
    $swSaveAsOptions_Silent,
    $null,
    [ref]$saveErrors,
    [ref]$saveWarnings
  )

  $swApp.CloseDoc($model.GetTitle()) | Out-Null

  if ($ok) {
    Write-Host "CREATED: $outStep"
  } else {
    Write-Host "FAIL save: $outStep"
    if (Test-Path $outStep) { Remove-Item $outStep -Force }
  }
}

# Normalize folder
$Folder = (Resolve-Path $Folder).Path
$parts = Get-ChildItem $Folder -File -ErrorAction SilentlyContinue | Where-Object { $_.Extension -ieq ".sldprt" }


if ($parts.Count -eq 0) {
  Write-Host "No SLDPRT files found."
  exit 0
}

# Try to start SolidWorks
try {
    $swApp = New-Object -ComObject 'SldWorks.Application'
    $swApp.Visible = $false
}
catch {
    Write-Host "=========================================="
    Write-Host "⚠ SolidWorks COM FAILED"
    Write-Host $_.Exception.Message
    Write-Host "=========================================="
    exit 1
}


foreach ($p in $parts) {
  Convert-PartToStep $swApp $p.FullName
}

$swApp.ExitApp()
[System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($swApp) | Out-Null

Write-Host "STEP conversion complete."
