# GTA SA — Single Player Roleplay Ultimate

**0.1.0-alpha: prototipo tecnico experimental. Nao testado dentro do GTA.**

Inclui identidade provisoria, carteira de trabalho, conta bancaria, deposito/saque e perfil persistente. Ainda nao inclui novo inicio sem campanha, prefeitura fisica, interiores ou empregos.

## Baixar e preparar no Windows

1. No repositorio, clique em **Code → Download ZIP** e extraia.
2. Entre na pasta **roleplay-ultimate**.
3. Execute **PREPARAR_MOD.bat**. Ele converte o arquivo Base64 incluido no script binario CLEO e confere seu SHA-256; nao baixa nem instala dependencias. O PowerShell tambem pode ser aberto manualmente para executar o `.ps1`.
4. Leia [LEIA-ME.md](LEIA-ME.md) e copie somente `instalar/CLEO/RP_Ultimate.cs` para a pasta `CLEO` da copia de teste do GTA.
5. Requer CLEO 4.3 ou posterior compativel. No jogo, fora de missao: **F6 → F7** para confirmar. Isso substitui o dinheiro em maos pelo do perfil RP.

O arquivo `.cs.b64` nao deve ser instalado no GTA. E uma representacao textual exata do binario para transporte pelo conector GitHub. O fonte e o construtor tambem estao incluidos.

Alternativa: em **Actions → RP Ultimate — build**, abra uma execucao bem-sucedida e baixe o artefato **GTA_SA_RP_Ultimate_0.1.0_alpha**. Ele inclui o `.cs` gerado, sem precisar do preparador. O download de artefatos exige login e eles expiram conforme a retencao do GitHub.

## Codigo e testes

```text
python tools/build.py
python -m unittest discover -s tests -v
```

Os 17 testes exercitam o bytecode gerado numa VM propria. Nao comprovam funcionamento no runtime real do GTA/CLEO. Consulte [docs/TESTES.txt](docs/TESTES.txt), [docs/ESTADO.md](docs/ESTADO.md) e o manual para limitacoes e recuperacao do perfil.

Este projeto e independente do ZIP de outro mod que ja existe na raiz do repositorio. A integracao entre eles nao foi testada.
