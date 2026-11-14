<h1 align="center">obsidian-second-brain-contabil</h1>

<p align="center">
  <em>Fork enxuto de <a href="https://github.com/eugeniughelbur/obsidian-second-brain">obsidian-second-brain</a>, de Eugeniu Ghelbur (licença MIT), preparado para escritórios de contabilidade. O que mandava conteúdo do cofre ou da conversa para serviços de terceiros foi removido.</em>
</p>

<p align="center">
  <a href="#o-que-é">O que é</a> &middot;
  <a href="#como-funciona-a-memória">Memória</a> &middot;
  <a href="#instalação-no-windows-passo-a-passo">Instalar</a> &middot;
  <a href="#38-comandos">Comandos</a> &middot;
  <a href="#privacidade">Privacidade</a> &middot;
  <a href="#limitações-e-o-que-não-foi-testado">Limitações</a> &middot;
  <a href="CHANGELOG.md">Histórico de mudanças</a>
</p>

## O que é

Uma habilidade para o Claude Code (e, com menos automação, para o Codex) que usa um cofre do [Obsidian](https://obsidian.md) como memória. O cofre é uma pasta de arquivos Markdown no seu computador. Você conversa com o agente do jeito de sempre, e ele guarda o que vale a pena (decisões, combinados com clientes, passos de processo, mudanças de norma com fonte) e consulta isso na próxima conversa.

Este fork traz o preset `contabil`: pastas `Clientes`, `Processos`, `Legislação`, `Decisões` e `Fontes`, modelos de nota em português e um manual (`_CLAUDE.md`) que manda o agente escrever em português do Brasil, citar fonte e dizer o nível de confiança de cada afirmação (fato, interpretação ou hipótese).

## O que este fork tirou e por quê

O upstream tinha recursos que mandavam texto do cofre, ou do que você estava lendo, para serviços de terceiros. Para um escritório que lida com dados de clientes, isso não serve. Saíram:

- pesquisa na web e pesquisa profunda por serviços externos, e os comandos de transcrição de vídeo e podcast;
- leitura de posts de uma rede social e o resumo de tendências dela;
- o robô de diário pelo Telegram;
- NotebookLM, Firecrawl, Tavily e demais conectores de pesquisa;
- os comandos de calendário e de arquitetura de projeto de software;
- a chamada à API da Anthropic que um script de triagem de links fazia por conta própria (agora ele só lista os links quebrados e o agente decide);
- a avaliação de comportamento por serviço externo e a via Grok da avaliação de busca;
- as versões para Gemini CLI, Grok Bot, Hermes e Pi, a página de documentação e os arquivos de mídia.

O que continua: os 38 comandos que trabalham só com os arquivos do cofre, a regra de escrita "AI-first" (notas feitas para o agente reler), o validador de notas e a busca local.

## Como funciona a memória

O plugin traz cinco "hooks" (pequenos programas que o Claude Code roda sozinho em certos momentos). Todos ficam em silêncio se a variável `OBSIDIAN_VAULT_PATH` não estiver definida.

| Quando | Hook | O que faz |
|---|---|---|
| Ao abrir a sessão (`SessionStart`) | `load_vault_context.sh` | Entrega ao agente o manual `_CLAUDE.md` do cofre. |
| A cada pergunta sua (`UserPromptSubmit`) | `obsidian-recall.sh` (recall) | Procura no cofre e, se achar algo relevante, acrescenta até 4 notas (cerca de 900 caracteres) ao contexto. Se o resultado for fraco, não acrescenta nada. Ligado por padrão. Desliga com `OBSIDIAN_RECALL_ENABLED=0`. |
| Quando o agente termina de responder (`Stop`) | `obsidian-save-reminder.sh` (lembrete) | Conta as respostas. Passadas 6 sem nenhuma gravação no cofre (`OBSIDIAN_SAVE_REMINDER_TURNS` muda o número), pede uma vez ao agente que salve o que for durável, ou que termine em silêncio se não houver nada. Desliga com `OBSIDIAN_SAVE_REMINDER=0`. |
| Depois de gravar um arquivo (`PostToolUse`) | `validate-ai-first.sh` (validador) | Confere se a nota gravada no cofre tem o cabeçalho e a seção que o agente espera, e se não tem segredo ou caractere estranho. Avisa o agente para corrigir. Não bloqueia nada. |
| Depois de o Claude compactar a conversa (`PostCompact`) | `obsidian-bg-agent.sh` | Inerte: só funciona se você ligar de propósito. Veja abaixo. |

**Sem o ai-memory (ou outra ferramenta de memória), isto é o que existe de automático:** o manual carregado no início, o recall a cada pergunta e o lembrete de salvar. O resto é manual: você (ou o agente, quando a conversa pede) roda `/obsidian-save`, `/obsidian-decide`, `/obsidian-person` e companhia. O lembrete só cutuca; quem decide o que é durável é o agente, e ele pode concluir que não há nada.

**Com o ai-memory instalado,** ele cuida da memória entre sessões do projeto e os hooks daqui continuam valendo por cima. Se os dois injetarem a mesma coisa e incomodar, desligue o recall ou o lembrete com as variáveis acima.

**Sobre o hook de PostCompact:** ele chama o comando `claude` (precisa estar no PATH) em segundo plano, com `--dangerously-skip-permissions` limitado às ferramentas de arquivo, para gravar no cofre sozinho. Este fork recomenda deixá-lo desligado em computador de escritório. Fica desligado se você não definir `OBSIDIAN_BG_AGENT_ENABLED=1`.

**No Codex** o build não traz hooks automáticos. A memória é a habilidade mais o salvamento manual (`$obsidian-save` ou "salve isto"). Há um arquivo de exemplo (`.codex/hooks.example.json` no build) para SessionStart e UserPromptSubmit, nunca testado.

## Instalação no Windows, passo a passo

Para quem não programa. Faça uma vez só, na ordem.

1. **Git for Windows.** Baixe em [git-scm.com/download/win](https://git-scm.com/download/win) e instale aceitando as opções padrão. Ele traz o "Git Bash", um terminal que alguns passos abaixo usam.
2. **Python ou uv.** O mais simples: baixe o Python em [python.org/downloads/windows](https://www.python.org/downloads/windows/) e, na primeira tela do instalador, marque **Add python.exe to PATH**. Alternativa: instalar o [uv](https://docs.astral.sh/uv/). Não use o `python3` que vem com o Windows: é um atalho da Microsoft Store que não executa nada.
3. **Obsidian.** Baixe em [obsidian.md](https://obsidian.md) e instale. Plugins úteis (Configurações, Plugins da comunidade): Dataview, Templater e Kanban.
4. **O agente.** O aplicativo Claude (aba **Code**) ou o Codex no aplicativo ChatGPT.

Depois, escolha um dos dois caminhos.

### Caminho A: plugin do Claude Code

Na aba Code, digite estes dois comandos, um de cada vez:

```
/plugin marketplace add Mouraovicente/obsidian-second-brain-contabil
/plugin install obsidian-second-brain@obsidian-second-brain-contabil
```

Isso instala os 38 comandos (com o prefixo `/obsidian-second-brain:`, por exemplo `/obsidian-second-brain:obsidian-save`), os cinco hooks e o servidor MCP do cofre. Depois configure o caminho do cofre (seção seguinte) e reinicie o Claude.

### Caminho B: o clássico, pelo Git Bash

Abra o **Git Bash** (não digite `bash` no PowerShell; se o WSL estiver instalado, isso abre outro Linux, com outra pasta pessoal e outro Python). Cole:

```bash
curl -fsSL https://raw.githubusercontent.com/Mouraovicente/obsidian-second-brain-contabil/main/scripts/quick-install.sh | bash
```

Isso baixa a habilidade para `~/.claude/skills/obsidian-second-brain` e instala os comandos (no Windows eles são copiados, não ligados; veja "Como atualizar"). O próximo passo, `setup.sh`, aponta o Claude para o seu cofre e registra os hooks no `settings.json`. Ele não precisa mais do `jq`. Você o roda depois de criar o cofre.

## Onde fica a configuração

O Claude lê o caminho do cofre da variável `OBSIDIAN_VAULT_PATH`, no bloco `env` do arquivo `settings.json` do usuário: `%USERPROFILE%\.claude\settings.json` no Windows. Exemplo (use barras normais no caminho, para não precisar duplicar as barras invertidas):

```json
{
  "env": { "OBSIDIAN_VAULT_PATH": "C:/Users/maria/Documents/CofreContabil" }
}
```

O `setup.sh` (caminho B) escreve isso para você. No caminho A, edite o arquivo à mão ou peça ao Claude. As outras variáveis desta página (`OBSIDIAN_RECALL_ENABLED`, `OBSIDIAN_SAVE_REMINDER`, `OBSIDIAN_SAVE_REMINDER_TURNS`) vão no mesmo bloco `env`. Um arquivo opcional de preferências fica em `%USERPROFILE%\.config\obsidian-second-brain\.env` (modelo em `.env.example`).

## Criar o cofre, ou usar um que já existe

**Cofre novo com o preset contabil.** No Git Bash:

```bash
cd ~/.claude/skills/obsidian-second-brain
python scripts/bootstrap_vault.py --path ~/Documents/CofreContabil --name "Seu Nome" --preset contabil
bash scripts/setup.sh ~/Documents/CofreContabil
```

(com uv, troque `python` por `uv run python`). No caminho A você pode pedir ao Claude: "crie meu cofre com o preset contabil em C:/Users/maria/Documents/CofreContabil". Depois abra a pasta no Obsidian e, numa sessão do Claude dentro da pasta, rode `/obsidian-init` (ou `/obsidian-second-brain:obsidian-init`).

Estrutura criada: `Clientes`, `Processos`, `Legislação`, `Decisões`, `Fontes` (em português) mais `Daily`, `Boards`, `Templates` e `_trash`. Estas quatro ficam com o nome em inglês de propósito: os comandos, o validador, a busca e a verificação de saúde procuram exatamente esses nomes, e traduzi-los quebraria o reconhecimento. Isso está explicado também no `_CLAUDE.md` gerado.

**Cofre que o escritório já tem.** Pode rodar o mesmo comando em cima da pasta existente: o script nunca sobrescreve arquivo que já existe (`AGENTS.md`, `CLAUDE.md`, `Home.md`, suas notas). Ele só cria o que falta. O `_CLAUDE.md` gerado manda o agente ler e obedecer o `AGENTS.md` e o `CLAUDE.md` do escritório, que valem mais que o manual do plugin.

## 38 comandos

Você não precisa decorar nada: dizer a frase de exemplo, em português, na conversa já dispara o comando. As frases vêm do campo `triggers_pt` de cada comando.

```
  CAMADA 1: Operações (28 comandos)       o agente guarda e organiza
  CAMADA 2: Ferramentas de pensar (9 comandos)  o agente pensa com você
  CAMADA 3: Contexto (1 comando)          o agente sabe quem você é
```

### Operações

| Comando | O que faz | Frase de exemplo |
|---|---|---|
| `/obsidian-save` | Guarda no cofre o que vale a pena da conversa: decisões, tarefas, pessoas, ideias. | "salve isto" |
| `/obsidian-ingest` | Lê uma fonte (link, PDF, Word, áudio, imagem, pasta) e atualiza as notas que já existem em vez de empilhar notas novas. | "ingira esta fonte" |
| `/obsidian-synthesize` | Procura padrões entre as fontes e escreve páginas de síntese. | "sintetize" |
| `/obsidian-reconcile` | Acha contradições entre notas e ajuda a resolver. | "encontre contradições" |
| `/obsidian-checkin` | Pergunta se notas antigas de pessoas e projetos ainda valem, mostrando o que cada uma diz. | "check-in do cofre" |
| `/obsidian-export` | Gera uma cópia limpa do cofre em JSON ou Markdown para outra ferramenta ler. | "exporte o vault" |
| `/obsidian-daily` | Cria ou atualiza a nota de hoje. | "nota de hoje" |
| `/obsidian-recurring` | Registra uma obrigação recorrente com periodicidade e próxima data calculada. | "obrigação mensal" |
| `/obsidian-log` | Registra uma sessão de trabalho e liga o registro às notas certas. | "registre esta sessão" |
| `/obsidian-task` | Põe uma tarefa no quadro certo, com prioridade e prazo. | "adicione uma tarefa" |
| `/obsidian-person` | Cria ou atualiza a nota de uma pessoa. | "adicione uma pessoa" |
| `/obsidian-capture` | Anota uma ideia rápida, sem burocracia. | "capture esta ideia" |
| `/obsidian-find` | Busca no cofre e devolve os resultados com contexto. | "pesquise minhas notas" |
| `/obsidian-recap` | Resume um dia, uma semana ou um mês. | "recapitule a semana" |
| `/obsidian-review` | Monta a revisão semanal ou mensal. | "revisão semanal" |
| `/obsidian-board` | Mostra e atualiza o quadro kanban. | "mostre o board" |
| `/obsidian-board-hygiene` | Faz a triagem do quadro: itens parados ou atrasados, para arquivar, remarcar ou dar como feitos. | "limpe meu board" |
| `/obsidian-project` | Cria ou atualiza a nota de um projeto, ligada ao quadro e à nota do dia. | "novo projeto" |
| `/obsidian-health` | Auditoria do cofre: contradições, lacunas, afirmações vencidas, notas soltas, links quebrados. | "saúde do vault" |
| `/obsidian-merge` | Junta duas notas quase duplicadas (primeiro mostra o que faria, sem alterar nada). | "mescle estas notas" |
| `/obsidian-reindex` | Atualiza o índice da busca por significado e diz a cobertura. | "reindexe o vault" |
| `/obsidian-retrieval-eval` | Mede se a busca acha a nota certa para uma pergunta em linguagem natural. | "avalie a recuperação" |
| `/obsidian-decide` | Registra decisões nas notas certas; com `--formal`, escreve o registro completo. | "registre esta decisão" |
| `/obsidian-visualize` | Gera um mapa visual do cofre (canvas do Obsidian). | "mapa do vault" |
| `/obsidian-learn` | Revisa o que o cofre aprendeu, descarta o que venceu e mostra padrões que viram regra. | "o que eu aprendi" |
| `/obsidian-init` | Lê um cofre existente e gera `_CLAUDE.md`, `index.md` e `log.md`. Não toca em `AGENTS.md` nem em `CLAUDE.md` da raiz. | "inicialize o vault" |
| `/crew` | Diário compartilhado entre vários agentes (Claude Code, Codex, Cursor) numa pasta comum. | "configurar o Crew" |
| `/create-command` | Cria um comando novo por entrevista, sem editar Markdown. | "crie um comando" |

### Ferramentas de pensar

| Comando | O que faz | Frase de exemplo |
|---|---|---|
| `/obsidian-brainstorm` | Entrevista de uma pergunta por vez até a ideia se fechar, e termina numa nota de desenho. | "faça um brainstorm comigo" |
| `/obsidian-challenge` | O cofre argumenta contra a sua ideia usando o seu próprio histórico. | "desafie isto" |
| `/obsidian-panel` | Reúne vários pontos de vista sobre uma decisão, um veredito de cada e uma síntese. | "convoque um painel" |
| `/obsidian-emerge` | Mostra padrões dos últimos 30 dias que você nunca nomeou. | "encontre padrões" |
| `/obsidian-connect` | Liga dois assuntos sem relação aparente para gerar ideias. | "conecte domínios" |
| `/vault-deep-synthesis` | Cruza tudo o que o cofre sabe sobre um assunto: concordâncias, contradições, pontos vencidos, lacunas. | "síntese profunda sobre" |
| `/obsidian-distill` | Condensa uma nota ou fonte longa nas afirmações principais, cada uma apontando para o trecho de origem. | "destile esta fonte" |
| `/idea-discovery` | Sugere de 3 a 5 próximos caminhos a partir de ideias, perguntas abertas e pesquisa solta. | "em que devo trabalhar agora" |
| `/obsidian-graduate` | Transforma um fragmento de ideia em projeto completo, com tarefas. | "transforme isto em projeto" |

### Contexto

| Comando | O que faz | Frase de exemplo |
|---|---|---|
| `/obsidian-world` | Carrega identidade e situação atual, em níveis, para não gastar contexto à toa. | "carregue contexto" |

## Privacidade

- **O que fica na máquina:** o cofre inteiro (arquivos Markdown), o índice de busca, o estado do lembrete (um arquivo pequeno na pasta temporária do sistema) e os registros do recall (`<cofre>/.claude-runs/`). Nenhum hook faz chamada de rede.
- **O que vai para o fornecedor do modelo:** o agente precisa ler as notas para usá-las, e tudo o que ele lê vira parte da conversa com o modelo (Anthropic no Claude, OpenAI no Codex). Isso vale para as notas que ele abre, para o trecho que o recall acrescenta a cada pergunta e para o que você digita. Se a política do escritório proíbe mandar determinados dados para o fornecedor, não os grave no cofre, ou mantenha-os em pasta que o agente não deve abrir. O `_CLAUDE.md` do preset manda nunca gravar senhas, tokens, chaves, códigos de verificação e certificados digitais.
- **Busca por significado:** opcional e desligada até você montar o índice. Por padrão usa o [Ollama](https://ollama.com) na própria máquina, e nada sai dela. Sem o Ollama, a busca é só por palavras, também local. O backend `openai` (variável `OBSIDIAN_EMBED_BACKEND=openai`) manda texto das notas para o endereço configurado: só use se aceitar isso, e use `OBSIDIAN_EMBED_EXCLUDE` para manter pastas de fora.
- **Primeira execução do servidor MCP:** o `uv` baixa o pacote `mcp` do PyPI. É download de programa, não envio de dados do cofre.
- **O PostCompact:** se você o ligar, ele roda outro `claude` em segundo plano (veja "Como funciona a memória").

## Limitações e o que não foi testado

- **Nada foi executado num Windows de verdade.** Os testes automáticos rodam em macOS; os scripts foram escritos para Git Bash e há testes que simulam o Windows (caminhos, `python3` falso, falta de `jq`), mas não substituem uma instalação real.
- **O aplicativo Claude Desktop (aba Code) não foi testado.** Os testes de ponta a ponta usaram o `claude` em linha de comando.
- **O modo de inferência por terceiros com gateway não foi testado.**
- **O Codex no aplicativo ChatGPT não foi testado.** O build existe, o exemplo de hooks também, nada disso foi rodado lá.
- **O lembrete de salvar** foi verificado de ponta a ponta uma vez (Claude Code, modelo pequeno, macOS): o hook disparou e o modelo seguiu o procedimento de salvar. Se o modelo gravar sozinho antes do lembrete, ele não dispara. Em sessões sem permissão para gravar, o agente avisa que não conseguiu.
- **O PostCompact** não foi exercitado de ponta a ponta, e ainda usa o `jq` (por isso fica inerte sem ele).
- Os hooks `.sh` precisam do Git Bash. O validador não exige mais o `jq` (usa Python quando ele falta).
- O preset `contabil` só existe no modo pessoal, e o recall e o lembrete olham um cofre por sessão.

## Como atualizar

- **Plugin (caminho A):** `/plugin update obsidian-second-brain` e reinicie o Claude.
- **Clássico (caminho B), no Git Bash:** `cd ~/.claude/skills/obsidian-second-brain && git pull`. No Windows rode também `bash update.sh`, que recopia os comandos, e reinicie o Claude. Depois de atualizar, rode `bash scripts/setup.sh "<caminho do cofre>"` de novo se quiser registrar hooks novos; é seguro repetir.

O histórico de mudanças está no [CHANGELOG.md](CHANGELOG.md). Mais sobre Windows em [WINDOWS.md](WINDOWS.md) e sobre idioma em [LANGUAGES.md](LANGUAGES.md).

## Para quem desenvolve

A regra de escrita dos cofres está em [AI-FIRST.md](AI-FIRST.md) e, completa, em `references/ai-first-rules.md`. O código-fonte dos comandos fica em `commands/`; os "builds" por plataforma saem de `bash scripts/build.sh`. Quem quiser mexer: [CONTRIBUTING.md](CONTRIBUTING.md) e [adapters/OWNERS.md](adapters/OWNERS.md). Os testes rodam com `uv run pytest -q`.

<!-- conformance:start -->
| Build | Emits a real tree | Script paths resolved | Docs reachable | Toolkit runnable |
|---|---|---|---|---|
| Agent Skills | pass | pass | pass | pass |
| Claude Code | pass | pass | pass | pass |
| Codex CLI | pass | pass | pass | pass |
| OpenCode | pass | pass | pass | pass |

*Generated by `scripts/conformance_report.py`, verified in CI on every push. Each build is compiled from the same source tree, then checked for a non-empty output, a resolved script root, reference paths that actually exist in that build, and a Python project shipped beside the scripts. A red cell here is a real red cell, not a missing test.*
<!-- conformance:end -->

## Licença e crédito

Licença MIT, a mesma do projeto original (arquivo [LICENSE](LICENSE)). O trabalho é de **Eugeniu Ghelbur**, autor do [obsidian-second-brain](https://github.com/eugeniughelbur/obsidian-second-brain), que este fork adapta. A ideia de base é o padrão "LLM Wiki" de [Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). As adaptações para escritórios de contabilidade ficam neste repositório: [Mouraovicente/obsidian-second-brain-contabil](https://github.com/Mouraovicente/obsidian-second-brain-contabil).

## English summary

This is a slimmed fork of Eugeniu Ghelbur's obsidian-second-brain (MIT), a Claude Code plugin and skill that keeps agent memory in an Obsidian vault, adapted for Brazilian accounting offices. Everything that sent vault or conversation content to third-party services was removed. It adds a `contabil` bootstrap preset (Portuguese folders, templates and operating manual; bootstrap never overwrites existing files), accent-insensitive search, vault recall on every prompt (on by default), a Stop-hook reminder to save durable notes, and a jq-free Windows install. The README is in Portuguese for the target audience; nothing has been run on real Windows, in the Claude Desktop Code tab, or in Codex inside the ChatGPT app. The 38 commands and the AI-first note rules are unchanged from upstream.
