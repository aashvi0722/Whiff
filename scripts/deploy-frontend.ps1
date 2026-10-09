# Deploys the frontend to S3 + CloudFront (PowerShell). Run from the repo root.
#   .\scripts\deploy-frontend.ps1               builds /frontend if it has a package.json, otherwise uploads the placeholder
#   .\scripts\deploy-frontend.ps1 -Placeholder  always uploads infra/placeholder
param([switch]$Placeholder)
$ErrorActionPreference = "Stop"
$stack = "whiff"; $region = "ap-south-1"

function Get-StackOutput($key) {
    $v = aws cloudformation describe-stacks --stack-name $stack --region $region `
        --query "Stacks[0].Outputs[?OutputKey=='$key'].OutputValue" --output text
    if ($LASTEXITCODE -ne 0 -or -not $v -or $v -eq "None") { throw "Stack output '$key' not found. Run sam deploy first." }
    return $v
}
$bucket = Get-StackOutput "FrontendBucket"
$dist   = Get-StackOutput "FrontendDistributionId"
$url    = Get-StackOutput "FrontendUrl"

if ($Placeholder -or -not (Test-Path "frontend/package.json")) {
    $src = "infra/placeholder"
    Write-Host "Uploading the placeholder page..."
} else {
    Push-Location frontend
    try {
        npm ci;        if ($LASTEXITCODE -ne 0) { throw "npm ci failed" }
        npm run build; if ($LASTEXITCODE -ne 0) { throw "npm run build failed" }
    } finally { Pop-Location }
    $src = "frontend/dist"
    Write-Host "Uploading the built app..."
}
aws s3 sync $src "s3://$bucket" --delete --region $region
if ($LASTEXITCODE -ne 0) { throw "s3 sync failed" }
aws cloudfront create-invalidation --distribution-id $dist --paths "/*" --query "Invalidation.Status" --output text
if ($LASTEXITCODE -ne 0) { throw "invalidation failed" }
Write-Host "Done. Live at $url (CloudFront can take a minute to refresh)."
