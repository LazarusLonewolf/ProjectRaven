# Raven Startup Script

$desktopPath = [System.IO.Path]::Combine($env:USERPROFILE, 'Desktop', 'RavenMail')
$containerName = "aeris_core"
$imageName = "aeris_core"

# Ensure RavenMail folder exists
if (-not (Test-Path $desktopPath)) {
    New-Item -Path $desktopPath -ItemType Directory | Out-Null
    Write-Host "Created RavenMail folder at: $desktopPath"
} else {
    Write-Host "RavenMail folder already exists at: $desktopPath"
}

# Ensure Docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not installed or not in PATH."
    Read-Host "Press Enter to exit..."
    exit 1
}

# Remove any previous container instance
Write-Host "`nRemoving old container (if exists)..."
docker rm -f $containerName 2>$null | Out-Null

# Launch container with root-level access and correct volume mapping
Write-Host "`nLaunching Raven container..."
docker run -it --rm `
    --name $containerName `
    --user root `
    -v "$env:USERPROFILE\Desktop\RavenMail:/app/RavenMail" `
    -v "${PWD}:/app" `
    -v "${PWD}\..\..\eris_volumes:/aeris_volumes" `
    -w /app `
    --entrypoint /usr/local/bin/aeris_entry.sh `
    $imageName
