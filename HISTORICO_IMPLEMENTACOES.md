# Histórico de Implementações e Melhorias

## 2026-04-13

### Estrutura inicial do produto
- Criação do projeto Django `AbatGus`.
- Organização em apps: `core`, `accounts`, `organizations`, `access`, `operations` e `reports`.
- Configuração base para SQLite com preparação para PostgreSQL via variáveis de ambiente.

### Multi-organização e usuários
- Criação do modelo customizado de usuário com perfis:
  - Master Global
  - Gestor da Organização
  - Usuário Auxiliar
- Implementação de contexto de organização ativa por sessão.
- Criação de tela para troca de organização pelo Master Global.

### Operação do abatedouro
- Modelos iniciais para:
  - Fontes de renda
  - Produção de carnes
  - Resíduos e subprodutos
  - Indenizações
  - Auditoria
- Formulários e listagens iniciais para os módulos operacionais.

### Interface
- Criação de login com identidade visual do produto.
- Criação de layout administrativo com:
  - navbar superior
  - sidebar responsiva
  - cards métricos
  - dashboard inicial
- Telas-base para organizações, usuários, acessos e relatórios.

### Setup local
- Criação de `.venv`.
- Instalação das dependências em `requirements.txt`.
- Criação de `.env` e `.env.example`.
- Criação de `.gitignore`.
- Seed inicial com:
  - usuário master global
  - organização demo
  - gestor demo
  - módulos padrão
  - catálogos iniciais

### Próximas melhorias sugeridas
- CRUD completo com editar, visualizar e excluir.
- Importação de Excel.
- Exportação PDF/Excel.
- Semáforo operacional com regras reais de meta.
- Auditoria automática por ação do usuário.
- Dashboard com gráficos reais.

## 2026-04-13 - etapa 2

### CRUDs operacionais completos
- Inclusão de visualização detalhada para fontes de renda, carnes, resíduos e indenizações.
- Inclusão de edição para todos os registros operacionais.
- Inclusão de exclusão com página de confirmação explícita.
- Tratamento de falha por dependência ao excluir registros protegidos.

### Semáforo operacional
- Implementação de semáforo por regra de negócio:
  - Fontes de renda comparadas à base de preço padrão.
  - Carnes comparadas com média geral e média do mês anterior.
  - Resíduos comparados com meta mensal por categoria.
  - Indenizações classificadas por impacto líquido.
- Inclusão do resumo verde/amarelo/vermelho nas listagens e no dashboard.

### Importação e exportação
- Importação de planilhas `.xlsx` e `.csv` para os quatro módulos operacionais.
- Exportação de Excel `.xlsx` por módulo.
- Exportação PDF por módulo.
- Estrutura de serviços reutilizáveis para importação, semáforo e exportação.

### Ajustes de projeto
- Atualização do `requirements.txt` com bibliotecas de Excel e PDF.
- Ampliação do `.gitignore` com arquivos de cobertura e logs.

## 2026-04-13 - etapa 3

### Cadastros-base operacionais
- CRUD para itens de fontes de renda.
- CRUD para categorias de carnes.
- CRUD para categorias de residuos.
- Inclusao desses cadastros no menu lateral para administracao continua.

### Filtros gerenciais
- Filtros por busca textual, ano, mes, semana e status nas listagens operacionais.
- Filtros especificos por periodo mensal para residuos e indenizacoes.

### Dashboard com graficos
- Inclusao de grafico de receita por competencia.
- Inclusao de grafico de receita por categoria de carne.
- Inclusao de grafico consolidado do semaforo operacional.
- Ajuste da base para suportar blocos extras de script no layout principal.

## 2026-04-14

### Ergonomia global de formularios
- Padronizacao global para selecionar automaticamente o conteudo de campos de texto, numero, busca, email, telefone, url, senha e textarea quando recebem foco.
- A melhoria foi aplicada no layout base, entao vale para os formularios atuais e para os proximos formularios criados no sistema sem necessidade de configuracao extra.

### Ajustes de usabilidade em operacoes
- Formulario de fontes de renda com:
  - item preenchendo preco unitario automaticamente
  - quantidade inteira em vez de decimal
  - ano atual preenchido
  - mes por extenso
  - semana por extenso
- Formulario de carnes com:
  - ano atual preenchido
  - mes atual por extenso
  - semana por extenso
  - categoria preenchendo preco por kg automaticamente
  - preco por kg em formato monetario brasileiro
  - label `Categoria` em pt-BR
