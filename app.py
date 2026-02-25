from flask import Flask, render_template, request, redirect, url_for
import json
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import subprocess

app = Flask(__name__)

# Adicionar enumerate ao Jinja2
app.jinja_env.globals.update(enumerate=enumerate)

# Carregar dados do JSON
def carregar_dados():
    with open('cronograma_estudos.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_dados(disciplinas):
    with open('cronograma_estudos.json', 'w', encoding='utf-8') as f:
        json.dump(disciplinas, f, indent=4, ensure_ascii=False)

# Função para parsear datas
def parse_data(data_str):
    if not data_str:
        return None
    try:
        return datetime.strptime(data_str, '%d/%m/%Y')
    except:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    disciplinas = carregar_dados()
    disciplina_selecionada = request.form.get('disciplina', 'Todas')
    
    if disciplina_selecionada != 'Todas':
        disciplinas_filtradas = [d for d in disciplinas if d['nome'] == disciplina_selecionada]
    else:
        disciplinas_filtradas = disciplinas
    
    disciplinas_com_index = [(i, d) for i, d in enumerate(disciplinas) if d in disciplinas_filtradas]
    
    # Métricas
    total_disciplinas = len(disciplinas)
    cursando = sum(1 for d in disciplinas if d.get('status') == 'Cursando')
    hoje = datetime.now()
    proximas = sum(1 for d in disciplinas if parse_data(d.get('fim')) and parse_data(d.get('fim')) > hoje)
    
    # Gráfico Timeline
    fig_timeline = go.Figure()
    cores = px.colors.qualitative.Set1
    for i, disc in enumerate(disciplinas_filtradas):
        cor = cores[i % len(cores)]
        inicio = parse_data(disc.get('inicio'))
        fim = parse_data(disc.get('fim'))
        if inicio and fim:
            fig_timeline.add_trace(go.Bar(
                y=[disc['nome']],
                x=[(fim - inicio).total_seconds() / 86400],  # dias
                base=[inicio],
                orientation='h',
                name=disc['nome'],
                marker_color=cor
            ))
    
    fig_timeline.update_layout(
        title='Timeline das Disciplinas',
        xaxis_title='Data',
        yaxis_title='Disciplina',
        barmode='stack'
    )
    timeline_json = json.dumps(fig_timeline, cls=PlotlyJSONEncoder)
    
    # Gráfico Gantt
    df = []
    for disc in disciplinas_filtradas:
        inicio = parse_data(disc.get('inicio'))
        fim = parse_data(disc.get('fim'))
        if inicio and fim:
            df.append({
                'Task': disc['nome'],
                'Start': inicio,
                'Finish': fim,
                'Resource': 'Disciplina'
            })
        for trab in disc.get('trabalhos', []):
            data_ent = parse_data(trab.get('data_entrega'))
            if data_ent:
                df.append({
                    'Task': f"{disc['nome']} - Trabalho",
                    'Start': data_ent,
                    'Finish': data_ent,
                    'Resource': 'Trabalho'
                })
        for prova in disc.get('provas', []):
            p_inicio = parse_data(prova.get('inicio'))
            p_fim = parse_data(prova.get('fim'))
            if p_inicio and p_fim:
                df.append({
                    'Task': f"{disc['nome']} - Prova",
                    'Start': p_inicio,
                    'Finish': p_fim,
                    'Resource': 'Prova'
                })
    
    if df:
        df_gantt = pd.DataFrame(df)
        fig_gantt = px.timeline(df_gantt, x_start="Start", x_end="Finish", y="Task", color="Resource")
        fig_gantt.update_yaxes(autorange="reversed")
        gantt_json = json.dumps(fig_gantt, cls=PlotlyJSONEncoder)
    else:
        gantt_json = None
    
    # Adicionar contadores às unidades
    for disc in disciplinas_filtradas:
        for unidade in disc.get('unidades', []):
            unidade['aulas_assistidas'] = sum(1 for a in unidade.get('aulas', []) if a.get('assistida'))
            unidade['total_aulas'] = len(unidade.get('aulas', []))
            unidade['exerc_finalizados'] = sum(1 for e in unidade.get('exercicios', []) if e.get('finalizado', False))
            unidade['total_exerc'] = len(unidade.get('exercicios', []))
    
    # Tarefas Pendentes
    tarefas = []
    for disc in disciplinas_filtradas:
        for unidade in disc.get('unidades', []):
            for aula in unidade.get('aulas', []):
                if not aula.get('assistida', False):
                    tarefas.append({
                        'tipo': 'Aula',
                        'disciplina': disc['nome'],
                        'titulo': aula.get('titulo', 'N/A'),
                        'data': aula.get('data')
                    })
            for exerc in unidade.get('exercicios', []):
                if not exerc.get('finalizado', False):
                    tarefas.append({
                        'tipo': 'Exercício',
                        'disciplina': disc['nome'],
                        'titulo': exerc.get('titulo', 'N/A'),
                        'data': exerc.get('data_entrega')
                    })
        for trab in disc.get('trabalhos', []):
            if not trab.get('nota'):
                tarefas.append({
                    'tipo': 'Trabalho',
                    'disciplina': disc['nome'],
                    'titulo': f"Trabalho {trab['id']}",
                    'data': trab.get('data_entrega')
                })
        for prova in disc.get('provas', []):
            if not prova.get('nota'):
                tarefas.append({
                    'tipo': 'Prova',
                    'disciplina': disc['nome'],
                    'titulo': f"Prova {prova['id']}",
                    'data': prova.get('fim')
                })
    
    return render_template('index.html', 
                          disciplinas=disciplinas,
                          disciplinas_com_index=disciplinas_com_index,
                          disciplina_selecionada=disciplina_selecionada,
                          total_disciplinas=total_disciplinas,
                          cursando=cursando,
                          proximas=proximas,
                          timeline_json=timeline_json,
                          gantt_json=gantt_json,
                          tarefas=tarefas)

@app.route('/add_disciplina', methods=['GET', 'POST'])
def add_disciplina():
    if request.method == 'POST':
        nome = request.form.get('nome')
        inicio = request.form.get('inicio')
        fim = request.form.get('fim')
        fim_trabalhos = request.form.get('fim_trabalhos')
        status = request.form.get('status', 'Cursando')
        
        nova_disciplina = {
            "nome": nome,
            "inicio": inicio,
            "fim": fim,
            "fim_trabalhos": fim_trabalhos,
            "provas": [],
            "status": status,
            "unidades": [],
            "trabalhos": []
        }
        
        disciplinas = carregar_dados()
        disciplinas.append(nova_disciplina)
        salvar_dados(disciplinas)
        
        return redirect(url_for('index'))
    
    return render_template('add_disciplina.html')

@app.route('/delete_disciplina/<int:index>', methods=['POST'])
def delete_disciplina(index):
    disciplinas = carregar_dados()
    if 0 <= index < len(disciplinas):
        del disciplinas[index]
        salvar_dados(disciplinas)
    return redirect(url_for('index'))

@app.route('/edit_disciplina/<int:index>', methods=['GET', 'POST'])
def edit_disciplina(index):
    disciplinas = carregar_dados()
    if not (0 <= index < len(disciplinas)):
        return redirect(url_for('index'))
    
    disc = disciplinas[index]
    
    if request.method == 'POST':
        disc['nome'] = request.form.get('nome')
        disc['inicio'] = request.form.get('inicio')
        disc['fim'] = request.form.get('fim')
        disc['fim_trabalhos'] = request.form.get('fim_trabalhos')
        disc['status'] = request.form.get('status')
        salvar_dados(disciplinas)
        return redirect(url_for('index'))
    
    return render_template('edit_disciplina.html', disc=disc, index=index)

@app.route('/add_trabalho/<int:disc_index>', methods=['GET', 'POST'])
def add_trabalho(disc_index):
    disciplinas = carregar_dados()
    if not (0 <= disc_index < len(disciplinas)):
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        data_prevista = request.form.get('data_prevista')
        data_entrega = request.form.get('data_entrega')
        nota = request.form.get('nota')
        if nota:
            nota = float(nota)
        else:
            nota = None
        
        novo_trabalho = {
            "data_prevista": data_prevista,
            "data_entrega": data_entrega,
            "nota": nota
        }
        
        disciplinas[disc_index]['trabalhos'].append(novo_trabalho)
        salvar_dados(disciplinas)
        return redirect(url_for('index'))
    
    return render_template('add_trabalho.html', disc_index=disc_index)

@app.route('/edit_trabalho/<int:disc_index>/<int:trab_index>', methods=['GET', 'POST'])
def edit_trabalho(disc_index, trab_index):
    disciplinas = carregar_dados()
    if not (0 <= disc_index < len(disciplinas)) or not (0 <= trab_index < len(disciplinas[disc_index]['trabalhos'])):
        return redirect(url_for('index'))
    
    trab = disciplinas[disc_index]['trabalhos'][trab_index]
    
    if request.method == 'POST':
        trab['data_prevista'] = request.form.get('data_prevista')
        trab['data_entrega'] = request.form.get('data_entrega')
        nota = request.form.get('nota')
        if nota:
            trab['nota'] = float(nota)
        else:
            trab['nota'] = None
        salvar_dados(disciplinas)
        return redirect(url_for('index'))
    
    return render_template('edit_trabalho.html', trab=trab, disc_index=disc_index, trab_index=trab_index)

@app.route('/delete_trabalho/<int:disc_index>/<int:trab_index>', methods=['POST'])
def delete_trabalho(disc_index, trab_index):
    disciplinas = carregar_dados()
    if 0 <= disc_index < len(disciplinas) and 0 <= trab_index < len(disciplinas[disc_index]['trabalhos']):
        del disciplinas[disc_index]['trabalhos'][trab_index]
        salvar_dados(disciplinas)
    return redirect(url_for('index'))

@app.route('/add_prova/<int:disc_index>', methods=['GET', 'POST'])
def add_prova(disc_index):
    disciplinas = carregar_dados()
    if not (0 <= disc_index < len(disciplinas)):
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        inicio = request.form.get('inicio')
        fim = request.form.get('fim')
        nota = request.form.get('nota')
        if nota:
            nota = float(nota)
        else:
            nota = None
        
        nova_prova = {
            "inicio": inicio,
            "fim": fim,
            "nota": nota
        }
        
        disciplinas[disc_index]['provas'].append(nova_prova)
        salvar_dados(disciplinas)
        return redirect(url_for('index'))
    
    return render_template('add_prova.html', disc_index=disc_index)

@app.route('/edit_prova/<int:disc_index>/<int:prova_index>', methods=['GET', 'POST'])
def edit_prova(disc_index, prova_index):
    disciplinas = carregar_dados()
    if not (0 <= disc_index < len(disciplinas)) or not (0 <= prova_index < len(disciplinas[disc_index]['provas'])):
        return redirect(url_for('index'))
    
    prova = disciplinas[disc_index]['provas'][prova_index]
    
    if request.method == 'POST':
        prova['inicio'] = request.form.get('inicio')
        prova['fim'] = request.form.get('fim')
        nota = request.form.get('nota')
        if nota:
            prova['nota'] = float(nota)
        else:
            prova['nota'] = None
        salvar_dados(disciplinas)
        return redirect(url_for('index'))
    
    return render_template('edit_prova.html', prova=prova, disc_index=disc_index, prova_index=prova_index)

@app.route('/delete_prova/<int:disc_index>/<int:prova_index>', methods=['POST'])
def delete_prova(disc_index, prova_index):
    disciplinas = carregar_dados()
    if 0 <= disc_index < len(disciplinas) and 0 <= prova_index < len(disciplinas[disc_index]['provas']):
        del disciplinas[disc_index]['provas'][prova_index]
        salvar_dados(disciplinas)
    return redirect(url_for('index'))

@app.route('/add_unidade/<int:disc_index>', methods=['GET', 'POST'])
def add_unidade(disc_index):
    disciplinas = carregar_dados()
    if not (0 <= disc_index < len(disciplinas)):
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        
        nova_unidade = {
            "titulo": titulo,
            "aulas": [],
            "exercicios": []
        }
        
        disciplinas[disc_index]['unidades'].append(nova_unidade)
        salvar_dados(disciplinas)
        return redirect(url_for('index'))
    
    return render_template('add_unidade.html', disc_index=disc_index)

@app.route('/edit_unidade/<int:disc_index>/<int:unidade_index>', methods=['GET', 'POST'])
def edit_unidade(disc_index, unidade_index):
    disciplinas = carregar_dados()
    if not (0 <= disc_index < len(disciplinas)) or not (0 <= unidade_index < len(disciplinas[disc_index]['unidades'])):
        return redirect(url_for('index'))
    
    unidade = disciplinas[disc_index]['unidades'][unidade_index]
    
    if request.method == 'POST':
        unidade['titulo'] = request.form.get('titulo')
        salvar_dados(disciplinas)
        return redirect(url_for('index'))
    
    return render_template('edit_unidade.html', unidade=unidade, disc_index=disc_index, unidade_index=unidade_index)

@app.route('/delete_unidade/<int:disc_index>/<int:unidade_index>', methods=['POST'])
def delete_unidade(disc_index, unidade_index):
    disciplinas = carregar_dados()
    if 0 <= disc_index < len(disciplinas) and 0 <= unidade_index < len(disciplinas[disc_index]['unidades']):
        del disciplinas[disc_index]['unidades'][unidade_index]
        salvar_dados(disciplinas)
    return redirect(url_for('index'))

@app.route('/add_aula/<int:disc_index>/<int:unidade_index>', methods=['GET', 'POST'])
def add_aula(disc_index, unidade_index):
    disciplinas = carregar_dados()
    if not (0 <= disc_index < len(disciplinas)) or not (0 <= unidade_index < len(disciplinas[disc_index]['unidades'])):
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        data = request.form.get('data')
        horario = request.form.get('horario')
        assistida = 'assistida' in request.form
        leitura = 'leitura' in request.form
        
        nova_aula = {
            "titulo": titulo,
            "data": data,
            "horario": horario,
            "assistida": assistida,
            "leitura": leitura
        }
        
        disciplinas[disc_index]['unidades'][unidade_index]['aulas'].append(nova_aula)
        salvar_dados(disciplinas)
        return redirect(url_for('index'))
    
    return render_template('add_aula.html', disc_index=disc_index, unidade_index=unidade_index)

@app.route('/edit_aula/<int:disc_index>/<int:unidade_index>/<int:aula_index>', methods=['GET', 'POST'])
def edit_aula(disc_index, unidade_index, aula_index):
    disciplinas = carregar_dados()
    if not (0 <= disc_index < len(disciplinas)) or not (0 <= unidade_index < len(disciplinas[disc_index]['unidades'])) or not (0 <= aula_index < len(disciplinas[disc_index]['unidades'][unidade_index]['aulas'])):
        return redirect(url_for('index'))
    
    aula = disciplinas[disc_index]['unidades'][unidade_index]['aulas'][aula_index]
    
    if request.method == 'POST':
        aula['titulo'] = request.form.get('titulo')
        aula['data'] = request.form.get('data')
        aula['horario'] = request.form.get('horario')
        aula['assistida'] = 'assistida' in request.form
        aula['leitura'] = 'leitura' in request.form
        salvar_dados(disciplinas)
        return redirect(url_for('index'))
    
    return render_template('edit_aula.html', aula=aula, disc_index=disc_index, unidade_index=unidade_index, aula_index=aula_index)

@app.route('/delete_aula/<int:disc_index>/<int:unidade_index>/<int:aula_index>', methods=['POST'])
def delete_aula(disc_index, unidade_index, aula_index):
    disciplinas = carregar_dados()
    if 0 <= disc_index < len(disciplinas) and 0 <= unidade_index < len(disciplinas[disc_index]['unidades']) and 0 <= aula_index < len(disciplinas[disc_index]['unidades'][unidade_index]['aulas']):
        del disciplinas[disc_index]['unidades'][unidade_index]['aulas'][aula_index]
        salvar_dados(disciplinas)
    return redirect(url_for('index'))

@app.route('/add_exercicio/<int:disc_index>/<int:unidade_index>', methods=['GET', 'POST'])
def add_exercicio(disc_index, unidade_index):
    disciplinas = carregar_dados()
    if not (0 <= disc_index < len(disciplinas)) or not (0 <= unidade_index < len(disciplinas[disc_index]['unidades'])):
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        data_entrega = request.form.get('data_entrega')
        finalizado = 'finalizado' in request.form
        
        novo_exercicio = {
            "titulo": titulo,
            "data_entrega": data_entrega,
            "finalizado": finalizado
        }
        
        disciplinas[disc_index]['unidades'][unidade_index]['exercicios'].append(novo_exercicio)
        salvar_dados(disciplinas)
        return redirect(url_for('index'))
    
    return render_template('add_exercicio.html', disc_index=disc_index, unidade_index=unidade_index)

@app.route('/edit_exercicio/<int:disc_index>/<int:unidade_index>/<int:exerc_index>', methods=['GET', 'POST'])
def edit_exercicio(disc_index, unidade_index, exerc_index):
    disciplinas = carregar_dados()
    if not (0 <= disc_index < len(disciplinas)) or not (0 <= unidade_index < len(disciplinas[disc_index]['unidades'])) or not (0 <= exerc_index < len(disciplinas[disc_index]['unidades'][unidade_index]['exercicios'])):
        return redirect(url_for('index'))
    
    exerc = disciplinas[disc_index]['unidades'][unidade_index]['exercicios'][exerc_index]
    
    if request.method == 'POST':
        exerc['titulo'] = request.form.get('titulo')
        exerc['data_entrega'] = request.form.get('data_entrega')
        exerc['finalizado'] = 'finalizado' in request.form
        salvar_dados(disciplinas)
        return redirect(url_for('index'))
    
    return render_template('edit_exercicio.html', exerc=exerc, disc_index=disc_index, unidade_index=unidade_index, exerc_index=exerc_index)

@app.route('/delete_exercicio/<int:disc_index>/<int:unidade_index>/<int:exerc_index>', methods=['POST'])
def delete_exercicio(disc_index, unidade_index, exerc_index):
    disciplinas = carregar_dados()
    if 0 <= disc_index < len(disciplinas) and 0 <= unidade_index < len(disciplinas[disc_index]['unidades']) and 0 <= exerc_index < len(disciplinas[disc_index]['unidades'][unidade_index]['exercicios']):
        del disciplinas[disc_index]['unidades'][unidade_index]['exercicios'][exerc_index]
        salvar_dados(disciplinas)
    return redirect(url_for('index'))

@app.route('/gerar_grafico')
def gerar_grafico():
    try:
        result = subprocess.run(['C:\\Users\\Silene\\Desktop\\Planilha Anhanguera\\venv\\Scripts\\python.exe', 'gr_estudo.py'], capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            return f"<h1>Gráfico gerado com sucesso!</h1><p>Output: {result.stdout}</p><a href='{url_for('index')}'>Voltar</a>"
        else:
            return f"<h1>Erro ao gerar gráfico</h1><p>Error: {result.stderr}</p><a href='{url_for('index')}'>Voltar</a>"
    except Exception as e:
        return f"<h1>Erro</h1><p>{str(e)}</p><a href='{url_for('index')}'>Voltar</a>"

if __name__ == '__main__':
    app.run(debug=True, port=5001)