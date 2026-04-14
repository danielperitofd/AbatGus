# AbatGus

Primeira entrega do SaaS `AbatGus`, focada na base estrutural do sistema de gestão para abatedouro.

## Stack

- Django 5
- Bootstrap 5
- SQLite por padrão
- Preparado para PostgreSQL por variáveis de ambiente
- Arquitetura multi-organização

## Módulos desta fase

- autenticação com papéis
- organizações
- usuários
- acessos
- dashboard inicial
- fontes de renda
- carnes
- resíduos
- indenizações
- hub de relatórios

## Perfis

- Master Global
- Gestor da Organização
- Usuário Auxiliar

## Credenciais iniciais

- Usuário master: `danielguspedev`
- Senha master: `Dnov@0380`

Usuário gestor demo:

- Usuário: `gestor.demo`
- Senha: `Gestor@123`

## Como executar

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_initial_data
python manage.py runserver
```

## Banco de dados

SQLite é o padrão. Para PostgreSQL, configure:

- `DB_ENGINE=postgresql`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

## Próximas etapas recomendadas

1. CRUD completo com edição, exclusão segura e confirmação de dependências.
2. Semáforo operacional com regras por meta e comparação entre períodos.
3. Importação de Excel e consolidação por competência.
4. Exportação PDF/Excel.
5. Auditoria automática via signals e middleware.
6. Gráficos reais no dashboard.
