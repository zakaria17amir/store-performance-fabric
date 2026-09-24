# Best Practice Analyzer on the semantic model: Microsoft's standard rules, then the project rules.
# Exits non-zero if the model fails to load or any severity-3 rule is violated.
param([Parameter(Mandatory)][string]$TabularEditor)

$model = Join-Path $PSScriptRoot "../StorePerformance.SemanticModel/definition/database.tmdl"
foreach ($rules in "microsoft-rules.json", "project-rules.json") {
    Write-Host "== BPA: $rules"
    # piping makes PowerShell wait for the GUI-subsystem exe and sets $LASTEXITCODE
    & $TabularEditor $model -A (Join-Path $PSScriptRoot $rules) -G | Out-Default
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
