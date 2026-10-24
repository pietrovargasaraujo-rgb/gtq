# GTA San Andreas — Single Player Roleplay Ultimate

**0.1.0-alpha — primeiro protótipo técnico da Fase 1.**

Este pacote contém um script CLEO binário, seu código-fonte, ferramentas de construção e testes. Ainda não é a Fase 1 completa nem a transformação de mundo descrita no documento original. O script foi gerado e testado por uma máquina virtual própria em Linux; **não foi executado no GTA/Windows**. A compatibilidade real precisa ser verificada na sua cópia de teste.

## O que esta entrega implementa

- Ativação manual com confirmação antes de substituir o dinheiro do personagem.
- Perfil inicial com $150, banco zerado e documentos pendentes.
- Identidade provisória numerada, gratuita e persistente. Neste perfil único o número é 100001; ainda não há nome, sobrenome nem data de nascimento.
- Carteira de trabalho de $10, exigindo identidade, sem cobrança repetida.
- Conta bancária exigindo identidade, depósitos e saques de $100 usando o dinheiro real do jogo.
- Verificação de saldo, limites e conservação do dinheiro nas transferências.
- Consulta dos saldos e situação dos documentos por texto na tela.
- Salvamento manual, automático a cada 30 segundos de execução do script e após operações.
- Dois arquivos alternados de perfil, validação de tamanho, versão, campos e soma de verificação, releitura após gravação e recuperação da última geração válida.

Os serviços são acessados por um menu de teste em qualquer local. Não há prefeitura física, agência bancária ou NPC de atendimento nesta versão. A consulta mostra os saldos atuais; **não existe histórico de transações ainda**.

## Requisitos

- GTA San Andreas **clássico de PC**, preferencialmente 1.0 US. O script não identifica automaticamente a versão; outras versões não foram validadas. Não usar na Definitive Edition ou em multiplayer.
- **CLEO 4.3 ou posterior compatível**, instalado e funcionando. A foto de CLEO.asi não confirma sua versão. Confirme no log `cleo.log`; se estiver usando CLEO 5, a compatibilidade com estes comandos legados também precisa ser testada.
- Permissão de escrita na pasta `CLEO` do jogo.
- Não precisa de MoonLoader, CLEO+, SAMPFUNCS, conexão com internet nem banco remoto. Não inclui os binários do CLEO ou arquivos comerciais do GTA.

## Instalação e primeiro teste

1. Feche o GTA. Use a **cópia de teste** cujo backup você já fez.
2. Abra a pasta `instalar` do ZIP e copie sua pasta `CLEO` para a pasta que contém `gta_sa.exe`. O resultado deve ser `GTA San Andreas\CLEO\RP_Ultimate.cs`.
3. Não coloque o projeto inteiro no Mod Loader e não substitua `main.scm`, `script.img`, `gta_sa.exe` ou seu CLEO existente.
4. Abra um save de teste, **fora de missão**, e espere ter controle normal. Este protótipo usa o início e o mundo originais; não substitui a introdução.
5. Pressione **F6** e leia a confirmação. **F7** cria/carrega o perfil RP e substitui o dinheiro em mãos pelo saldo desse perfil. **F8** cancela sem alterar o dinheiro.
6. Pressione F6 novamente se necessário para mostrar o menu. Use os números da fileira superior do teclado, não o teclado numérico.

Se não aparecer nada, feche o jogo e confira o log do CLEO. Se houver erro ou travamento, remova apenas `RP_Ultimate.cs` e envie o `cleo.log`, a informação da versão do jogo e eventual relatório do CrashInfo. Não instale pacotes aleatórios para tentar corrigir.

## Controles

| Tecla | Ação |
|---|---|
| F6 | Ativar/abrir os serviços de teste |
| F7 | Confirmar criação/carregamento, somente na tela inicial do RP |
| F8 | Cancelar, somente nessa confirmação |
| 1 | Emitir identidade provisória |
| 2 | Emitir carteira de trabalho ($10) |
| 3 | Abrir conta bancária |
| 4 | Depositar $100 |
| 5 | Sacar $100 |
| 6 | Salvar o perfil RP |
| 7 | Consultar saldos e documentos |
| Backspace | Fechar o menu; o RP continua ativo |

Cada tecla precisa ser solta antes de repetir a ação. O menu usa legendas, não bloqueia o personagem e não pausa o mundo. Pode conflitar com outros mods que usem estas teclas. Mensagens de outros scripts podem encobrir o menu. Não use os serviços durante combate, direção ou missões nesta etapa.

## Sequência para conferir no jogo

Depois de confirmar a criação do perfil, você deve ter $150:

1. Tente abrir conta (3): deve exigir identidade.
2. Emita identidade (1), depois carteira (2): devem restar $140.
3. Aperte 2 novamente: não deve cobrar outra vez.
4. Abra conta (3), deposite (4): devem ficar $40 na mão e $100 no banco.
5. Tente depositar novamente: deve recusar por saldo insuficiente.
6. Saque (5): deve voltar a $140 na mão e $0 no banco.
7. Salve (6), feche o GTA, abra o mesmo save de teste e ative com F6/F7: os documentos e os saldos devem reaparecer.

Isso é o teste pendente no seu GTA, não um resultado já confirmado neste ambiente.

## Salvamento e recuperação

Os arquivos criados são `CLEO\RP_Ultimate_A.dat` e `CLEO\RP_Ultimate_B.dat`. Guarde **ambos** ao fazer backup. Há um único perfil por instalação; todas as partidas nessa pasta acessam o mesmo perfil.

Cada gravação usa o arquivo alternativo e só avança a geração após reler e validar os dados. No carregamento, prevalece a geração válida mais recente. Se um arquivo estiver incompleto ou inválido, o outro poderá recuperar a geração anterior. Isso pode perder a operação mais recente; não equivale a uma transação atômica garantida pelo sistema operacional. A soma de verificação detecta alguns erros acidentais, não adulteração intencional.

Se houver arquivo de perfil, mas nenhuma cópia válida, o script recusa a ativação e não cria um perfil por cima. Copie ambos para um local seguro antes de qualquer tentativa de recuperação. Para reiniciar deliberadamente, feche o GTA e mova ambos para fora da pasta CLEO; na próxima ativação será oferecido outro perfil.

**Se a gravação falhar durante uma operação, os valores continuam somente na sessão atual.** Corrija a permissão e pressione 6 antes de sair. O script mostra o erro; fechar o jogo pode perder essas alterações. O salvamento não pode ser garantido se faltar energia, espaço ou acesso ao disco.

O perfil guarda somente dinheiro, banco e os três indicadores de documentação/conta. **Posição, inventário, veículos, propriedades, relógio e progresso do mundo continuam sob o salvamento original do GTA.** Não misture este perfil com partidas diferentes: os dados do mundo e do RP ainda não são sincronizados. Não há proteção contra exploração por alternância de saves ou edição de arquivos.

## Configuração e reconstrução

O `config.json` é uma **configuração de construção**, não um INI lido em tempo de jogo. O binário incluído usa os valores acima. Para alterá-los, edite o JSON e execute na pasta deste projeto com Python 3:

```text
python tools/build.py
python -m unittest discover -s tests -v
```

Copie o `.cs` reconstruído para o GTA com o jogo fechado. Alterar o dinheiro inicial só afeta a criação de outro perfil; não modifica um já existente. O fonte em `src/RP_Ultimate.txt` também está em sintaxe de opcodes do Sanny Builder, modo GTA SA/CLEO, para inspeção e compilação independente. Essa recompilação pelo Sanny ainda não foi realizada aqui.

## Desinstalação

Feche o jogo e retire `CLEO\RP_Ultimate.cs`. Os arquivos A/B podem ser guardados para continuar depois. Não remova o CLEO, o Mod Loader ou DLLs de outros mods. Se você salvar a partida original depois de operações RP, o dinheiro dessa partida também poderá ter mudado; remover o script não desfaz essa alteração. Use seu backup se quiser restaurar a partida anterior.

## Próximas etapas da Fase 1

Ainda faltam: início independente sem campanha, desbloqueio controlado das cidades, prefeitura física e atendimento por NPC, cadastro completo, banco físico, HUD próprio, configuração em tempo de execução e salvamento integrado do mundo. Depois vêm empregos e demais fases. Nenhum modelo, interior ou animação personalizada foi incluído ou anunciado como pronto.

O próximo passo depende do teste acima e da confirmação das versões do GTA e CLEO. Não é necessário baixar outras dependências para este protótipo.
