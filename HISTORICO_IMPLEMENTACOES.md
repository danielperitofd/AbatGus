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

## 2026-04-14 - regionalizacao, acessos e operacao

### Base de regionalizacao e internacionalizacao
- Inclusao de `LocaleMiddleware`, `LANGUAGES` e `LOCALE_PATHS` no projeto.
- Preparacao da organizacao para persistir:
  - moeda padrao (`BRL`, `USD`, `EUR`)
  - idioma padrao (`pt-br`, `en`, `es`)
- Ativacao automatica do idioma da organizacao no middleware.
- Criacao de camada centralizada de formatacao para:
  - moeda
  - numero
  - kg
  - g
  - l
  - rotulos de mes, semana e unidade

### Navegacao e consistencia visual
- Inclusao de breadcrumb clicavel no cabecalho compartilhado.
- Uso de titulos e subtitulos padronizados nas telas principais.
- Atualizacao do layout base para expor idioma e moeda ao frontend.
- Padronizacao visual de toggles/switches e cards de acesso.

### Operacoes
- Listagens de fontes de renda, carnes, residuos e indenizacoes atualizadas para usar a camada centralizada de formatacao.
- Valores monetarios agora renderizados conforme a moeda configurada da organizacao.
- Pesos e volumes padronizados em kg, g e l nas tabelas e cards.
- Limpeza das colunas de cadastros:
  - `Configuracao` -> `Preco base` em fontes de renda
  - coluna de carnes simplificada para `Preco/Kg`
  - coluna de residuos simplificada para `Meta`
- Detalhes operacionais passaram a exibir valores formatados por tipo de campo.

### Modulo de acessos
- Nova tela de acessos com:
  - selecao de usuario por dropdown
  - cards por modulo
  - toggle de ativacao/desativacao por tela
  - persistencia via `UserModuleAccess`
- Distincao visual clara entre acessos ativos e inativos.

### Modulo de carnes
- Listagem expandida com:
  - media por cabeca
  - media geral
  - media anterior
  - receita
  - doacao
  - tendencia
- Resumo gerencial com receita total, peso total, bovinos abatidos e doacao controlada.
- Melhor e pior rendimento destacados na tela.
- Formulario passa a calcular automaticamente a media por cabeca a partir de peso e abate.
- Formulario busca historico para sugerir media do mes anterior e media geral quando nao informadas.

### Modulo de indenizacoes
- Leitura de negocio reforcada para:
  - perda bruta
  - valor recuperado
  - prejuizo liquido
  - percentual de recuperacao
- Inclusao de status gerencial:
  - sem prejuizo liquido
  - prejuizo integral
  - perda parcialmente recuperada
- Inclusao de insights de motivo recorrente, produto com mais perdas e responsavel recorrente.
- Inclusao de serie mensal de prejuizo liquido para visualizacao gerencial.

### Validacao tecnica
- Criada migration `organizations.0002_organization_default_currency_and_more`.
- Validado com `manage.py check`.
- Validado com smoke test autenticado nas rotas principais:
  - dashboard
  - operacoes
  - cadastros
  - acessos
  - contas
  - organizacoes

## 2026-04-15 - carga documental e dashboard de carnes

### Carga documental para demonstracao real
- Criado comando `manage.py load_document_samples` para popular o SQLite com dados transcritos dos documentos operacionais enviados.
- Carga aplicada para:
  - `CARNES MARCO 2026`
  - `BALANCO GERAL FONTES DE RENDA (MARCO)`
  - `INDENIZACOES MARCO DE 2026`
  - `RESIDUOS FEVEREIRO DE 2026`
- Base preenchida com:
  - 23 registros de carnes
  - 28 registros de fontes de renda
  - 8 registros de indenizacoes
  - 10 registros de residuos

### Tela de carnes mais visual
- A listagem de `Carnes` deixou de depender de cards isolados e passou a exibir um dashboard do periodo.
- Inclusos graficos para:
  - receita por categoria
  - peso por categoria
  - doacao por categoria
  - media por cabeca
- Inclusos insights automaticos destacando lideres de receita, peso, doacao e rendimento.

### Observacoes desta carga
- A transcricao foi manual a partir das imagens, priorizando os trechos mais legiveis.
- Em alguns itens de carnes, o `preco_por_kg` do lancamento foi derivado de `receita / peso` para preservar a receita exibida no documento.
- Os dados servem para demonstracao operacional realista e podem ser refinados depois com importador guiado ou revisao humana linha a linha.

### Filtros analiticos do dashboard
- Inclusao de seletor de janela analitica no dashboard principal:
  - mensal
  - trimestral
  - semestral
  - anual
- O filtro passou a afetar os graficos principais e os resumos operacionais do dashboard.
- O comparativo mensal de `Receita por competencia` agora considera fevereiro e marco para `Fontes de renda`, incluindo fevereiro com `R$ 277.000,00`.

## 2026-04-17 - experiencia de indenizacoes e admin tools

### Formulario de indenizacoes
- Campo `Ocorrencia` passou a abrir com a data atual por padrao.
- Campos `Valor de saida` e `Reversao` passaram a usar mascara monetaria com simbolo de moeda na interface.
- Campos `Produto`, `Dono`, `Responsavel` e `Motivo` passaram a ser alimentados pelo banco em dropdowns reutilizaveis.

### Base reutilizavel para dropdowns
- Criado o modelo `IndemnityLookupValue` para armazenar valores base de:
  - produto
  - dono
  - responsavel
  - motivo
- A importacao e o salvamento de indenizacoes agora retroalimentam esse catalogo automaticamente.

### Admin Tools para dados de teste
- Criada a tela `Dados de teste` em `Admin Tools`.
- Inclusao de acoes para:
  - popular ate 10 valores/registros de teste por tela
  - excluir dados de teste por tela
  - popular tudo
  - excluir tudo
- A operacao respeita a organizacao ativa selecionada no topo do sistema.

### Listagem de indenizacoes mais clara
- A tela de `Indenizacoes` passou a explicar melhor a diferenca entre:
  - leitura gerencial
  - semaforo de impacto
- Os cards de status tambem ganharam descricoes mais objetivas.

## 2026-04-19 - harmonizacao visual e interacao do dashboard

### Padrao visual de cards destacados
- Definido um novo padrao visual para cards de destaque do sistema, com:
  - hierarquia visual mais forte
  - area de valor principal mais evidente
  - acabamento grafico sutil no fundo
  - uso consistente nas telas principais
- Esse padrao passou a ser aplicado no:
  - dashboard principal
  - fontes de renda
  - carnes
  - residuos
  - indenizacoes
  - central de relatorios

### Sidebar com rolagem natural
- Removido o comportamento fixo/sticky da sidebar no desktop.
- A barra lateral agora rola junto com a pagina inteira, acompanhando o fluxo natural do conteudo.

### Dashboard principal
- O filtro `Janela analitica` deixou de depender de botao `Aplicar`.
- A troca do dropdown agora submete automaticamente o formulario.
- Cards superiores da visao geral receberam o novo estilo de destaque visual.

### Tela de carnes
- Graficos ajustados para leitura mais harmonica entre desktop e mobile.
- Em telas maiores, os graficos ganharam mais altura util.
- Em tablet e smartphone, os valores deixaram de aparecer dentro do grafico e passaram a ser exibidos em `card_legenda` abaixo de cada bloco.
- Os cards de insights finais receberam novo padrao visual com:
  - rotulo
  - item em destaque
  - valor principal
  - cor de apoio por contexto

### Padrao operacional unificado
- Cards de status verde/amarelo/vermelho foram refinados visualmente nas listagens operacionais.
- Cards de resumo financeiro/quantitativo tambem passaram a usar o padrao de destaque mais forte.
- A central de relatorios foi ajustada para seguir a mesma linguagem visual das demais telas.

## 2026-04-19 - refinamentos mobile e relatorios analiticos de indenizacoes

### Cabecalho mobile e acoes operacionais
- Reestruturado o cabecalho mobile para trazer:
  - organizacao ativa na barra superior escura
  - avatar do usuario ao lado do menu
  - card branco inferior mais limpo com breadcrumb, titulo e descricao
- Reorganizados os botoes de acoes das telas operacionais no mobile para evitar colapso visual:
  - CTA principal em destaque
  - importacao em linha propria
  - acoes secundarias distribuidas com melhor leitura

### Indenizacoes - leitura gerencial reforcada
- A secao `Leituras gerenciais` foi evoluida para um layout em grade 2x2 no desktop e empilhamento natural no mobile.
- Cada card passou a exibir:
  - label do insight
  - valor principal
  - metrica percentual ou quantitativa
  - descricao de apoio
  - meta de referencia
- Novos indicadores adicionados:
  - percentual do motivo mais frequente em relacao ao total
  - percentual do produto com mais perdas em relacao ao total
  - quantidade de responsaveis fora do ideal zero
  - clientes afetados por `mau manejo`

### Indenizacoes - navegacao analitica
- Os cards de status `Verde`, `Amarelo` e `Vermelho` passaram a abrir relatorios analiticos por cor/semaforo.
- Os cards de `Leituras gerenciais` tambem passaram a ser clicaveis, levando para relatorios analiticos especificos de:
  - motivo
  - produto
  - responsavel
  - clientes afetados
- Criada a tela dedicada `indemnity_analytic_report.html` para consolidar os recortes analiticos com:
  - resumo do recorte
  - destaques analiticos
  - filtros
  - tabela detalhada das ocorrencias

### Validacao tecnica desta rodada
- Validado com `manage.py check`.
- Validadas as rotas:
  - `/operacoes/indenizacoes/`
  - `/operacoes/indenizacoes/analitico/success/`
  - `/operacoes/indenizacoes/analitico/warning/`
  - `/operacoes/indenizacoes/analitico/danger/`
  - `/operacoes/indenizacoes/analitico/insight/reason/`
  - `/operacoes/indenizacoes/analitico/insight/product/`
  - `/operacoes/indenizacoes/analitico/insight/responsible/`
  - `/operacoes/indenizacoes/analitico/insight/affected-clients/`

## 2026-04-19 - menu de perfil e logout

### Navegacao do usuario autenticado
- Adicionado menu no avatar do usuario no desktop com acessos para:
  - `Perfil`
  - `Logout`
- Reaproveitado o mesmo conceito no mobile para manter consistencia entre as experiencias.
- O item `Perfil` aponta para a edicao do proprio usuario autenticado.

### Logout em configuracoes
- Incluido atalho explicito de `Logout` dentro da secao `Configuracoes` da sidebar.
- O encerramento de sessao foi mantido de forma segura via `POST`.

### Ajuste visual do dropdown no desktop
- Corrigido o comportamento do dropdown do avatar no desktop para nao ser cortado pelo conteudo logo abaixo do cabecalho.
- Ajustados `z-index` e `overflow` do topo para o menu abrir com a mesma limpeza visual aprovada no mobile.

### Validacao tecnica desta rodada
- Validado com `manage.py check`.
- Validado o render do dashboard com links de `Perfil` e `Logout`.
- Validado o ajuste visual do dropdown em telas desktop.

## 2026-04-19 - avatar real e upload visual de foto

### Exibicao de foto do usuario
- O sistema passou a exibir a foto real do usuario no cabecalho desktop e mobile quando o campo `avatar` estiver preenchido.
- Quando nao houver imagem enviada, o fallback continua sendo a inicial do nome no circulo de avatar.

### Formulario de usuarios
- O campo `foto` nas telas de:
  - criacao de usuario
  - edicao de usuario
  foi transformado em uma area visual de upload com:
  - bloco tracejado
  - instrucoes de PNG ou JPG
  - clique ou arraste
  - preview da imagem atual ou da nova imagem selecionada
- O input tambem passou a aceitar apenas formatos compativeis de imagem via atributo `accept`.

### Validacao tecnica desta rodada
- Validado com `manage.py check`.
- Validadas as rotas:
  - `/contas/usuarios/novo/`
  - `/contas/usuarios/1/editar/`
  - `/`

## 2026-04-19 - redesign da tela de usuarios

### Estrutura dedicada para cadastro e edicao
- A tela de `Novo usuario` e `Editar usuario` deixou de depender do layout generico de formulario.
- Foi criada uma pagina dedicada com:
  - painel lateral para foto, status e atalhos de contexto
  - painel principal com secoes separadas
  - bloco de seguranca com acoes de senha
  - rodape fixo com acoes principais

### Melhorias de experiencia
- Reordenacao dos campos para leitura mais natural:
  - identificacao e contato
  - vinculo e permissoes
  - seguranca
  - observacoes internas
- Inclusao de preview de username no bloco de identificacao.
- Inclusao de geracao rapida de senha e alternancia mostrar/ocultar.
- Ajuste da foto de perfil para um bloco mais valorizado e integrado ao contexto do usuario.

### Limpeza de redundancias
- Remocao do titulo duplicado dentro do conteudo da pagina, mantendo a identificacao principal no cabecalho global.
- Remocao de redundancias visuais no topo da pagina dedicada.

### Ajustes finos de layout
- Reaproveitamento melhor dos espacos do card principal.
- Ajuste do bloco `Status/Ativo` para altura natural, sem esticar nem vazar no container.
- Refinos de espacamento, alinhamento e proporcao dos blocos laterais e centrais.

### Validacao tecnica desta rodada
- Validado com `manage.py check`.
- Validadas as rotas:
  - `/contas/usuarios/novo/`
  - `/contas/usuarios/1/editar/`
  - `/contas/usuarios/3/editar/`

## 2026-04-20 - refinamentos finais na tela de usuarios

### Preview e upload de avatar
- A foto ja salva no banco passou a ser exibida com o mesmo enquadramento da preview de upload, evitando o efeito de zoom excessivo.
- O campo de avatar deixou de renderizar os textos padrao do Django no formulario:
  - `Atualmente:`
  - `Limpar`
  - `Modificar:`
- O preview visual ficou consistente entre:
  - imagem ja cadastrada
  - nova imagem selecionada
  - avatar exibido no cabecalho

### Fluxo de salvamento
- O botao `Salvar usuario` passou a manter o usuario na propria tela apos salvar.
- O fluxo de criacao agora redireciona para a tela de edicao do usuario recem-criado.
- O fluxo de edicao agora retorna para a propria rota de edicao, em vez de levar para a listagem.
- Quando o proprio usuario altera a propria senha, a sessao passa a ser preservada com `update_session_auth_hash`, evitando que o sistema derrube o login e redirecione para `/contas/login/`.

### Ajustes finais de layout
- Compactacao adicional do card `Ativo` na secao `Vinculo e permissoes`.
- Ajuste de largura e copy do bloco de status para reduzir altura desnecessaria e melhorar o equilibrio visual da linha.

### Validacao tecnica desta rodada
- Validado com `manage.py check`.
- Validado POST real em:
  - `/contas/usuarios/3/editar/`
- Confirmado redirecionamento de salvamento para:
  - `/contas/usuarios/3/editar/`
