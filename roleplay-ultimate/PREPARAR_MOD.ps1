$ErrorActionPreference = 'Stop'
$baseRP = $PSScriptRoot
$arquivoRP = Join-Path $baseRP 'instalar\CLEO\RP_Ultimate.cs'
$dadosRP = [IO.File]::ReadAllText((Join-Path $baseRP 'instalar\CLEO\RP_Ultimate.cs.b64'))
$bytesRP = [Convert]::FromBase64String($dadosRP)
$shaRP = [Security.Cryptography.SHA256]::Create()
try {
    $hashRP = [BitConverter]::ToString($shaRP.ComputeHash($bytesRP)).Replace('-', '').ToLowerInvariant()
} finally { $shaRP.Dispose() }
if ($hashRP -ne '82af35741f7b39bad2715b96b7a14f7b76976f79d3933e9965eedfaf97d95c36') {
    throw 'Arquivo invalido. Baixe o projeto novamente; nenhum script foi gerado.'
}
if (Test-Path $arquivoRP) {
    if ([Convert]::ToBase64String([IO.File]::ReadAllBytes($arquivoRP)) -ne [Convert]::ToBase64String($bytesRP)) {
        throw 'Ja existe um script diferente neste caminho. Mova-o antes de continuar.'
    }
} else { [IO.File]::WriteAllBytes($arquivoRP, $bytesRP) }
Write-Host 'Pronto: instalar\CLEO\RP_Ultimate.cs'
Write-Host 'Leia LEIA-ME.md e copie somente o .cs para a pasta CLEO da copia de teste do GTA.'
Write-Host 'Alpha experimental; ainda nao testada dentro do GTA.'
