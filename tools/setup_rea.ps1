# Pinned, project-local analysis tools. No global Node or agent configuration changes.
$ErrorActionPreference = 'Stop'
$toolRoot = Join-Path (Split-Path -Parent $PSScriptRoot) '.tools'
New-Item -ItemType Directory -Force -Path $toolRoot | Out-Null
$nodeVersion = '24.22.1'
$nodeArchiveName = "node-v$nodeVersion-win-x64.zip"
$nodeArchive = Join-Path $toolRoot $nodeArchiveName
$nodeRoot = Join-Path $toolRoot "node-v$nodeVersion-win-x64"
$expectedHash = 'd2046d28c2c3dcd211ac5145c0bf30e2047ef9dfb306693c8c6e2eccd8b95fa5'
if (-not (Test-Path -LiteralPath $nodeArchive)) {
    Invoke-WebRequest -Uri "https://nodejs.org/dist/v$nodeVersion/$nodeArchiveName" -OutFile $nodeArchive
}
if ((Get-FileHash -LiteralPath $nodeArchive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedHash) {
    throw 'Isolated Node archive checksum mismatch.'
}
if (-not (Test-Path -LiteralPath (Join-Path $nodeRoot 'node.exe'))) {
    Expand-Archive -LiteralPath $nodeArchive -DestinationPath $toolRoot
}
$node = Join-Path $nodeRoot 'node.exe'
$npm = Join-Path $nodeRoot 'node_modules/npm/bin/npm-cli.js'
$reaRoot = Join-Path $toolRoot 'rea'
& $node $npm install --prefix $reaRoot --ignore-scripts --no-audit --no-fund 'rea-agents@6.7.0'
if ($LASTEXITCODE -ne 0) { throw 'Isolated REA package install failed.' }
& $node (Join-Path $reaRoot 'node_modules/rea-agents/scripts/rea.mjs') --version
if ($LASTEXITCODE -ne 0) { throw 'Isolated REA version check failed.' }
