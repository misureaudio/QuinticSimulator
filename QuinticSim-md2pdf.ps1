# Convert a Markdown file to a rendered PDF via pandoc + XeLaTeX.
# Usage:  .\QuinticSim-md2pdf.ps1 <base-name>
#         .\QuinticSim-md2pdf.ps1 report          (report.md -> report.pdf)
#         .\QuinticSim-md2pdf.ps1 "my report"     (quotes needed for spaces)
#
# Accepts either a base name ("report") or a full path with/without .md
# ("report.md", "C:\docs\report.md").

param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Name
)

$ErrorActionPreference = 'Stop'

# Normalise to a base name without extension, keeping the directory.
if ($Name -match '\.md$') { $base = $Name -replace '\.md$', '' }
else { $base = $Name }

$mdFile    = "$base.md"
$tmpFile   = "$base_fixed.md"
$pdfFile   = "$base.pdf"

if (-not (Test-Path -LiteralPath $mdFile)) {
    throw "Markdown file not found: $mdFile"
}

# Replace the emoji checkmark (not always in the font) with the plain one.
# -Encoding utf8 avoids mojibake on Windows PowerShell 5.1.
(Get-Content -LiteralPath $mdFile -Raw) -replace '✅', '✓' |
    Set-Content -LiteralPath $tmpFile -Encoding utf8

try {
    & pandoc $tmpFile `
        -o $pdfFile `
        --pdf-engine=xelatex `
        -V geometry:margin=1in `
        -V mainfont="DejaVu Sans" `
        -V monofont="DejaVu Sans Mono" `
        -V fontsize=10pt

    if ($LASTEXITCODE -ne 0) {
        throw "pandoc failed with exit code $LASTEXITCODE"
    }
}
finally {
    Remove-Item -LiteralPath $tmpFile -ErrorAction SilentlyContinue
}

Write-Host "Created $pdfFile"
