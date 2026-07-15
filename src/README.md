# Monium

Monium é um SaaS de gestão de inventário e ativos que substitui planilhas por
um sistema único para rastrear equipamentos, empréstimos internos e
manutenção — com controle multi-organização, alertas automáticos e planos
pagos.

## Principais recursos

- **Inventário**: cadastro de itens com categoria, setor, localização, marca,
  status e condição; dashboard com visão geral e distribuição por categoria/setor.
- **Empréstimos**: registro de empréstimos internos com detecção automática de
  atraso e alerta por e-mail (recurso de planos pagos).
- **Multi-organização**: cada conta pertence a uma ou mais organizações
  (dono/membro), com onboarding obrigatório na criação da conta.
- **Assinaturas**: planos Free/Starter/Pro/Enterprise com limite de itens,
  usuários e organizações por plano, checkout via Mercado Pago (Checkout Pro)
  e enforcement automático dos limites.
- **Auditoria e segurança**: log estruturado por camada (acesso, negócio,
  segurança, performance, erros, Celery, banco de dados) com dashboards
  internos, bloqueio por tentativas de login (exponential backoff) e trilha
  de auditoria de alterações em modelos sensíveis.
- **Contas**: cadastro, login, recuperação de senha, avatar, exclusão de
  conta com período de carência.

## Stack

- **Backend**: Django 5.2 + Celery/Celery Beat (tarefas periódicas) + Redis
  (cache/broker) + Channels (websockets).
- **Frontend**: Tailwind CSS + TypeScript (compilado via esbuild), templates
  Django server-side.
- **Banco de dados**: PostgreSQL (SQLite em desenvolvimento).
- **Infra**: Docker Compose + Nginx como reverse proxy.
- **Pagamentos**: Mercado Pago (assinaturas recorrentes via Preapproval).

## Desenvolvimento

```bash
uv sync                    # dependências Python
npm install && npm run build  # assets (Tailwind + TypeScript)
python manage.py migrate
python manage.py runserver
```

Variáveis de ambiente esperadas estão documentadas em `.env` (não
versionado — veja o time do projeto para os valores de desenvolvimento).
