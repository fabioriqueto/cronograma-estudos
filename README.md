# 📚 Cronograma de Estudos - Dashboard Interativo

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Plotly](https://img.shields.io/badge/Plotly-5.0+-orange.svg)](https://plotly.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.1+-purple.svg)](https://getbootstrap.com/)

> Um sistema completo para gerenciamento e visualização de cronogramas de estudos universitários, desenvolvido para otimizar o tempo e acompanhar o progresso acadêmico.

## 🎯 Visão Geral

Este projeto nasceu da necessidade prática durante estudos universitários, oferecendo uma representação temporal clara e abrangente do cronograma de estudos. Permite programar e visualizar o tempo disponível para cada disciplina, unidade, aula e tarefa, facilitando verificar se tudo está em dia e se os trabalhos e exercícios foram realizados.

### ✨ Principais Funcionalidades

- **📊 Visualização Temporal**: Gráficos interativos (timeline e Gantt) para acompanhar o progresso ao longo do tempo.
- **📝 Gerenciamento Completo**: CRUD para disciplinas, unidades, aulas, exercícios, trabalhos e provas.
- **📈 Métricas em Tempo Real**: Contadores de disciplinas cursando, ativas e tarefas pendentes.
- **🔍 Filtros Inteligentes**: Selecione disciplinas específicas para foco personalizado.
- **🎨 Interface Moderna**: Design responsivo com Bootstrap, acessível em desktop e mobile.
- **🔗 Integração**: Botão para gerar gráficos Gantt originais via `gr_estudo.py`.

## 🛠️ Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML5, Bootstrap 5, Plotly.js
- **Dados**: JSON (persistência local)
- **Gráficos**: Plotly (interativos) e Matplotlib (Gantt original)
- **Ambiente**: Virtualenv (venv)

## 🚀 Instalação e Uso

### Pré-requisitos
- Python 3.8+
- Ambiente virtual (venv)

### Passos

1. **Clone ou baixe o projeto**:
   ```bash
   cd "C:\Planilha Anhanguera"
   ```

2. **Ative o ambiente virtual**:
   ```bash
   & "venv\Scripts\Activate.ps1"
   ```

3. **Instale as dependências**:
   ```bash
   pip install flask pandas plotly matplotlib
   ```

4. **Execute o aplicativo**:
   ```bash
   python estudo.py
   ```
   
   no terminal, ou,
   
   ```bash
   python app.py
   ```

6. **Acesse no navegador**:
   - [http://localhost:5001](http://localhost:5001)

## 📋 Estrutura do Projeto

```
📁 Planilha Anhanguera/
├── 📄 app.py                 # Aplicação Flask principal
├── 📄 cronograma_estudos.json # Dados do cronograma
├── 📄 estudo.py              # Script CLI para gerenciamento
├── 📄 gr_estudo.py           # Geração de gráficos Gantt
├── 📁 templates/             # Templates HTML
│   ├── index.html
│   ├── add_*.html
│   └── edit_*.html
├── 📁 static/                # Arquivos estáticos (CSS/JS)
└── 📄 requirements.txt       # Dependências
```

## 🎮 Como Usar

1. **Adicione Disciplinas**: Use o botão "➕ Adicionar Disciplina" para criar novas matérias.
2. **Gerencie Conteúdo**: Para cada disciplina, adicione unidades, aulas, exercícios, trabalhos e provas.
3. **Acompanhe Progresso**: Visualize gráficos e listas de tarefas pendentes.
4. **Gere Relatórios**: Clique em "📊 Gerar Gráfico Gantt Original" para salvar imagens.

## 📊 Exemplos de Visualizações

- **Timeline Horizontal**: Mostra o período de cada disciplina com cores distintas.
- **Gráfico Gantt Interativo**: Timeline detalhada com tarefas e entregas.
- **Tarefas Pendentes**: Lista organizada de itens não concluídos.

## 🤝 Contribuição

Este é um projeto pessoal, mas sugestões são bem-vindas! Para melhorias:
- Você pode aprimorar este projeto como desejar, e pode começar
adicionando tratamentos de erros. 
- Abra uma issue descrevendo a ideia.
- Faça um fork e envie um pull request.

## 📄 Licença

Este projeto é de uso pessoal. Sinta-se à vontade para adaptar conforme suas necessidades.
O uso deste projeto por plataformas ou instituições de ensino é permitido, desde que os créditos ao autor sejam mantidos.
---

**Desenvolvido para otimizar estudos universitários.**
