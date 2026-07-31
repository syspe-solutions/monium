# Monium

[![License: AGPL v3](https://img.shields.io/badge/License-AGPLv3-blue.svg)](LICENSE)

Monium é um sistema open source e self-hosted de gestão de inventário e
ativos que substitui planilhas por um sistema único para rastrear
equipamentos, empréstimos internos e manutenção — com controle
multi-organização e alertas automáticos, sem limites de uso ou custo de
licença.

## Principais recursos

- **Inventário**: cadastro de itens com categoria, setor, localização, marca,
  status e condição; dashboard com visão geral e distribuição por categoria/setor.
- **Empréstimos**: registro de empréstimos internos com detecção automática de
  atraso e alerta por e-mail.
- **Multi-organização**: cada conta pertence a uma ou mais organizações
  (dono/membro), com onboarding obrigatório na criação da conta, sem limite
  de organizações, membros ou itens.
- **Auditoria e segurança**: log estruturado por camada (acesso, negócio,
  segurança, performance, erros, banco de dados) com dashboards internos,
  bloqueio por tentativas de login (exponential backoff) e trilha de
  auditoria de alterações em modelos sensíveis.
- **Contas**: cadastro, login, recuperação de senha, avatar, exclusão de
  conta com período de carência.

## Stack

- **Backend**: Django 5.2. Sem Celery/broker: as únicas duas tarefas de fundo
  (auditoria e checagem de empréstimos atrasados) rodam de forma síncrona ou
  via um scheduler simples embutido no `gunicorn.conf.py` — ver
  `python manage.py check_overdue_loans`. Cache numa tabela própria do banco
  configurado (sem Redis).
- **Frontend**: Tailwind CSS + TypeScript (compilado via esbuild), templates
  Django server-side.
- **Banco de dados**: SQLite (padrão, zero configuração) ou PostgreSQL (servidor
  externo) — escolhido no instalador de primeiro uso, ver abaixo.
- **Infra**: Docker Compose. O próprio Django/gunicorn serve os arquivos
  estáticos via WhiteNoise — sem reverse proxy dedicado.

## Instalação (Docker Compose)

```bash
git clone <url-do-repositorio> monium
cd monium
cp src/.env.example src/.env
# edite src/.env — no mínimo DJANGO_SECRET_KEY e DJANGO_ENCRYPTION_KEY
# (veja os comandos de geração nos comentários do próprio arquivo)

docker compose up -d --build
```

Acesse `http://localhost:8088/` (porta configurável via `APP_PORT` no
`.env`) e siga o instalador — próxima seção.

> **Upload de arquivos**: avatar de usuário, logo de organização e fotos de
> item dependem de um serviço de storage HTTP externo (variáveis
> `STORAGE_BASE_URL`/`STORAGE_TOKEN`), que **não está incluído neste
> repositório**. Sem isso configurado, a aplicação funciona normalmente,
> mas upload de arquivos falha. Ver `src/.env.example` para detalhes.

## Primeira execução

Sem `DB_ENGINE` definido no `.env`, a aplicação sobe em modo instalador: toda
navegação é redirecionada para `/setup/`. O fluxo é:

1. **Banco de dados** (`/setup/database/`) — escolha SQLite (recomendado para
   uso simples, nenhum serviço extra necessário) ou informe host/porta/usuário/
   senha de um PostgreSQL externo. A conexão é testada (roundtrip de escrita)
   antes de qualquer coisa ser salva. Escolhendo SQLite, a configuração é
   aplicada na hora; escolhendo PostgreSQL, a aplicação reinicia sozinha (via
   `restart: always`) pra aplicar a nova configuração.

   | SQLite | PostgreSQL |
   | --- | --- |
   | ![Escolha de banco SQLite](docs/screenshots/setup-01-database-sqlite.png) | ![Escolha de banco PostgreSQL](docs/screenshots/setup-02-database-postgresql.png) |

2. **Administrador** (`/setup/admin/`) — depois do banco confirmado e
   migrado, cria a primeira conta de superusuário antes de liberar o resto do
   sistema.

   | Criação de conta | Validação de erros |
   | --- | --- |
   | ![Criação da conta de administrador](docs/screenshots/setup-03-admin-account.png) | ![Validação de erros no formulário](docs/screenshots/setup-04-admin-validation-error.png) |

A configuração escolhida fica persistida em `APP_DATA_DIR/database.env` (um
volume Docker — `app_data` no `compose.yml`), sobrevivendo a recriações do
container. Quem preferir configurar o banco manualmente pode simplesmente
definir `DB_ENGINE`/`DB_NAME`/`DB_USER`/`DB_PASSWORD`/`DB_HOST`/`DB_PORT` no
`.env` — o instalador é pulado inteiramente nesse caso.

## Desenvolvimento

```bash
cd src
uv sync                       # dependências Python
npm install && npm run build  # assets (Tailwind + TypeScript)
cp .env.example .env          # ajuste os valores
uv run python manage.py migrate
uv run python manage.py runserver
```

## Licença

Distribuído sob a [GNU Affero General Public License v3.0](LICENSE). Em
resumo: você pode usar, modificar e redistribuir livremente, inclusive
rodando uma instância própria — mas se você rodar uma versão modificada como
serviço de rede acessível a terceiros, é obrigado a disponibilizar o código
dessa versão modificada para os usuários desse serviço.
