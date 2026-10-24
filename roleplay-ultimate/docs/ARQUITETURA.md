# Arquitetura do protótipo

`tools/build.py` contém um gerador de instruções e um montador pequeno para o subconjunto usado de bytecode SCM/CLEO. Inteiros são int32 little endian com tag 1; variáveis locais usam tag 3 e índice uint16; strings ASCII usam tag 14 e tamanho uint8. O arquivo é um script externo sem cabeçalho. Saltos usam offsets negativos relativos ao início do script; um NOP inicial evita salto ao offset zero. O comando de texto com argumentos variáveis termina em byte zero.

Não há patch de memória, chamada nativa em endereço fixo ou alteração de arquivo original. Isso reduz dependência de endereços específicos, mas não comprova compatibilidade com todas as versões do jogo ou CLEO.

Estados: inativo → confirmação → ativo. A criação só grava depois da confirmação; o dinheiro só é substituído após a gravação inicial verificada. Carregamento lê os dois arquivos sem modificar o jogo e só aplica o saldo depois da confirmação. Cancelamento mantém o dinheiro original.

Os serviços da alpha operam em subrotinas independentes: identidade, carteira profissional, abertura de conta, depósito, saque e consulta. A interface é provisória. A camada de economia usa os opcodes originais de dinheiro e um saldo bancário local, limitados a 999999999. Depósitos/saques alteram os dois lados pela mesma quantia. Não há juros, empréstimos, salário ou geração artificial de renda.

## Formato de perfil v1

Nove int32, exatamente 36 bytes:

| Offset | Campo |
|---|---|
| 0 | Identificador 1380995121 |
| 4 | Versão 1 |
| 8 | Geração (1 a 1000000) |
| 12 | Dinheiro em mãos |
| 16 | Banco |
| 20 | ID (0 ou 100001) |
| 24 | Carteira de trabalho (0 ou 1) |
| 28 | Conta bancária (0 ou 1) |
| 32 | Soma 777 + campos dos offsets 4 a 28 |

São rejeitados saldos negativos, valores fora do limite, versão desconhecida, tamanho diferente e combinações impossíveis (carteira/conta sem ID ou saldo sem conta). A soma máxima fica dentro de int32. O limite de gerações evita overflow; atingido o limite, gravações são recusadas explicitamente.

## Referências técnicas consultadas

- CLEO4: implementação de open/read/write/size/exists/text/keyboard em https://github.com/cleolibrary/CLEO4/blob/master/source/CCustomOpcodeSystem.cpp
- Tipos: https://docs.sannybuilder.com/language/data-types
- Saltos em scripts externos: https://docs.sannybuilder.com/troubleshooting/errors/0084
- Sintaxe de opcodes: https://docs.sannybuilder.com/language/instructions/opcodes

Essas referências embasam o formato e os comandos. Não substituem execução no runtime real. O pacote contém código original deste protótipo; não redistribui o código do CLEO ou arquivos do GTA.
