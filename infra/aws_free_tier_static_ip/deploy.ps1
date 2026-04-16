param(
  [string]$Region = "ap-south-1",
  [string]$KeyPairName = "thriftcloud-key",
  [string]$ProjectName = "thriftcloud",
  [string]$InstanceType = "t3.micro",
  [string]$AllowedSshCidr = "",
  [switch]$AutoApprove
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Attempt to auto-detect public IP if not provided
if (-not $AllowedSshCidr) {
  Write-Host "Auto-detecting your public IP..."
  try {
    $ip = (Invoke-RestMethod -Uri "https://ifconfig.me" -TimeoutSec 5).Trim()
    if ($ip) {
      $AllowedSshCidr = "$ip/32"
      Write-Host "Detected public IP: $AllowedSshCidr"
    }
  } catch {
    Write-Host "Could not auto-detect public IP. Defaulting to 0.0.0.0/0 (WARNING: NOT SECURE)"
    $AllowedSshCidr = "0.0.0.0/0"
  }
}

Write-Host "Creating terraform.tfvars..."
$tfvarsContent = @"
aws_region = "$Region"
key_pair_name = "$KeyPairName"
project_name = "$ProjectName"
instance_type = "$InstanceType"
allowed_ssh_cidr = "$AllowedSshCidr"
"@
Set-Content -Path (Join-Path $scriptDir "terraform.tfvars") -Value $tfvarsContent

Push-Location $scriptDir
try {
  terraform init
  terraform plan
  if ($AutoApprove) {
    terraform apply -auto-approve
  } else {
    terraform apply
  }
} catch {
  Write-Host "Terraform deployment failed. Ensure you have terraform installed and AWS CLI configured." -ForegroundColor Red
} finally {
  Pop-Location
}
