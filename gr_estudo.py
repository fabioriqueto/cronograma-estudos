import json
import os
import matplotlib.pyplot as plt
import argparse
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import numpy as np
import math
from matplotlib.patches import Patch

ARQUIVO_JSON = "cronograma_estudos.json"

# Paleta de cores Período estudos (ORIGINAL)
COR_ESTUDO = plt.cm.RdYlGn

# Paleta de cores para unidades
CORES_UNIDADES = [
    "#f8f9fa", "#e3f2fd", "#f1f8e9", "#fff3e0", "#fce4ec",
    "#ede7f6", "#e0f7fa", "#f9fbe7", "#fffde7", "#e8eaf6"
]

# Função para degradê de cor para provas (ORIGINAL)
COR_PROVA_DEGRADE = lambda frac: (0.0 + frac, 1 - frac, 0.0)

# Cor para período de trabalhos (ORIGINAL)
COR_TRABALHO = "#d0d0d0"

# Paleta de cores para entregas de trabalhos Datas sugestivas (ORIGINAL)
CORES_ENTREGA = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

# Paleta de cores para entregas de trabalhos Datas reais (ORIGINAL)
COR_REAL_ENTREGA = ["#8c564b", "#e377c2", "#17becf", "#bcbd22", "#7f7f7f"]

# Cores para elementos específicos (MELHORADAS)
COR_HOJE = "#d32f2f"
COR_AULAS = "#5c6bc0"
COR_EXERCICIOS = "#26a69a"
COR_PROGRESSO = "#43a047"
COR_FRACIONADO = "#ffb74d"  # cor para progresso fracionado (parcial)
COR_BAIXO = "#e53935"       # cor para progresso baixo
COR_EXERC_FINALIZADO = "#067e02"  # verde escuro para exercícios finalizados
COR_EXERC_PENDENTE = "#525252"    # laranja para exercícios pendentes
# Deslocamento vertical (em pixels) para o marcador 'HOJE' — positivo move para cima
HOJE_TEXT_OFFSET_PX = 30

def parse_data_segura(data_str):
    if not data_str:
        return None
    try:
        data = datetime.strptime(data_str.strip(), "%d/%m/%Y")
        if 2000 <= data.year <= 2100:
            return data
        return None
    except:
        return None

def carregar_dados():
    if os.path.exists(ARQUIVO_JSON):
        with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def gerar_grafico(save_path=None, dpi=200):
    disciplinas = carregar_dados()
    if not disciplinas:
        print("❌ Nenhuma disciplina encontrada.")
        return

    # Configurar figura com tamanho adaptável
    n_disciplinas = len(disciplinas)
    altura_figura = max(10, n_disciplinas * 3.5)
    fig, ax = plt.subplots(figsize=(16, altura_figura))
    
    hoje = datetime.now()
    y_pos = 0  # Começar do topo

    # Constantes de layout
    ALTURA_BARRA = 0.8  # Ligeiramente maior para caber texto
    ESPACO_ENTRE_SECOES = 0.9
    ESPACO_ENTRE_DISCIPLINAS = 3.8

    # Coletar todas as datas para definir os limites do gráfico
    todas_datas = []
    for disc in disciplinas:
        datas = [
            parse_data_segura(disc.get("inicio")),
            parse_data_segura(disc.get("fim")),
            parse_data_segura(disc.get("fim_trabalhos"))
        ]
        for prova in disc.get("provas", []):
            datas.append(parse_data_segura(prova.get("inicio")))
            datas.append(parse_data_segura(prova.get("fim")))
        for trab in disc.get("trabalhos", []):
            datas.append(parse_data_segura(trab.get("data_prevista")))
            datas.append(parse_data_segura(trab.get("data_entrega")))
        todas_datas += [d for d in datas if d]

    if not todas_datas:
        print("❌ Nenhuma data válida encontrada.")
        return

    menor_inicio = min(todas_datas)
    maior_fim = max(todas_datas)

    # TÍTULO PRINCIPAL
    ax.set_title("CRONOGRAMA DE ESTUDOS - ADS - Anhanguera", 
                fontsize=16, fontweight="bold", pad=40, color="#2e7d32")

    # LINHA DA DATA ATUAL
    ax.axvline(hoje, color=COR_HOJE, linestyle="-", linewidth=2.5, 
               alpha=0.8, label="Hoje")
    
    # Marcador de data atual no topo (posição ajustável em pixels)
    y_topo = ax.get_ylim()[1] - 0.5
    ax.annotate(f"HOJE\n{hoje.strftime('%d/%m/%Y')}",
                xy=(hoje, y_topo),
                xytext=(0, HOJE_TEXT_OFFSET_PX),
                textcoords='offset points',
                ha="center", va="bottom", fontsize=9, color=COR_HOJE,
                fontweight="bold", backgroundcolor="white",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                         edgecolor=COR_HOJE, alpha=0.9))

    for disc in disciplinas:
        nome = disc.get("nome", "Sem nome")
        inicio = parse_data_segura(disc.get("inicio"))
        fim = parse_data_segura(disc.get("fim"))
        fim_trab = parse_data_segura(disc.get("fim_trabalhos"))
        unidades = disc.get("unidades", [])
        # Coletor para exercícios que são na verdade trabalhos (detectados pelo título)
        disc_trabalhos = []
        
        if not inicio or not fim:
            continue

        # CABEÇALHO DA DISCIPLINA
        ax.text(menor_inicio - timedelta(days=2), y_pos + ALTURA_BARRA + 0.3, 
                nome.upper(), ha="left", va="bottom", fontsize=8, 
                color="#1a237e", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#e8eaf6", 
                         edgecolor="#1a237e", alpha=0.3))

        # === Período de Estudos ===
        dias_estudo = (fim - inicio).days
        for i in range(dias_estudo):
            frac = i / dias_estudo
            data = inicio + timedelta(days=i)
            ax.barh(y_pos, 1, left=data, color=COR_ESTUDO(1 - frac), height=ALTURA_BARRA + 0.2)

        ax.text(
            inicio + (fim - inicio) / 2,
            y_pos,
            f"Período de estudos de {inicio.strftime('%d/%m/%Y')} até {fim.strftime('%d/%m/%Y')}",
            ha="center",
            va="center",
            fontsize=8,
            color="black",
            fontweight="bold"
        )


        y_pos -= ALTURA_BARRA + ESPACO_ENTRE_SECOES + 0.5

        # UNIDADES DE ESTUDO
        if unidades:
            total_unid = len(unidades)
            duracao_unid = dias_estudo / total_unid
            y_unidades = y_pos

            for i, unidade in enumerate(unidades):
                cor_unid = CORES_UNIDADES[i % len(CORES_UNIDADES)]
                ini_unid = inicio + timedelta(days=i * duracao_unid)
                fim_unid = inicio + timedelta(days=(i + 1) * duracao_unid)

                # Calcular progresso:
                # - cada aula contribui 50% por 'assistida' e 50% por 'leitura' (0.5 + 0.5 = 1.0 quando ambas são True)
                # - cada exercício conta 100% se tiver NOTA (não nula)
                aulas = unidade.get("aulas", [])
                exercicios = unidade.get("exercicios", [])
                total_itens = len(aulas) + len(exercicios)
                # Somar frações para as aulas (0.5 cada) e 1.0 para exercícios concluídos
                concluidos_aulas = sum((0.5 if a.get("assistida") is True else 0) + (0.5 if a.get("leitura") is True else 0) for a in aulas)
                concluidos_exerc = sum(1 for e in exercicios if e.get("nota") is not None)
                concluidos = concluidos_aulas + concluidos_exerc
                progresso = (concluidos / total_itens * 100) if total_itens > 0 else 0

                # Barra da unidade
                ax.barh(y_unidades, duracao_unid, left=ini_unid,
                       color="white", edgecolor="gray", height=ALTURA_BARRA * 1.2,
                       linewidth=1.5, alpha=0.9)

                # Escolher cor e ícone dependendo do progresso (fração, completo, baixo)
                has_fraction = abs(progresso - round(progresso)) > 1e-6
                if progresso >= 100:
                    bar_color = COR_PROGRESSO
                    icon = " ✔"
                elif has_fraction:
                    bar_color = COR_FRACIONADO
                    icon = " ✦"
                elif progresso < 50:
                    bar_color = COR_BAIXO
                    icon = ""
                else:
                    bar_color = COR_PROGRESSO
                    icon = ""

                # Barra de progresso (usa cor dinâmica)
                if progresso > 0:
                    ax.barh(y_unidades, duracao_unid * (progresso / 100),
                           left=ini_unid, color=bar_color,
                           height=ALTURA_BARRA * 0.4, alpha=0.8, zorder=3)

                # Informações da unidade
                ax.text(ini_unid + timedelta(days=0.5), y_unidades + ALTURA_BARRA * 0.9,
                       f"Unidade {i+1}", ha="left", va="bottom", fontsize=8,
                       color="darkblue", fontweight="bold")

                ax.text(ini_unid + (fim_unid - ini_unid) / 2, y_unidades,
                       f"{progresso:.1f}%{icon}", ha="center", va="center", fontsize=8,
                       color="black", weight="bold",
                       bbox=dict(boxstyle="circle,pad=0.2", facecolor="white", 
                                edgecolor="gray", alpha=0.8))

                ax.text(fim_unid - timedelta(days=0.5), y_unidades,
                       fim_unid.strftime('%d/%m'), ha="right", va="center",
                       fontsize=7, color="black", style="italic")

            y_pos = y_unidades - ALTURA_BARRA - ESPACO_ENTRE_SECOES


            # LISTAGEM DE AULAS E EXERCÍCIOS (MANTENDO O PADRÃO ORIGINAL)
            y_aulas = y_pos
            aulas_agendadas = False
            
            for unidade in unidades:
                for aula in unidade.get("aulas", []):
                    data_aula = parse_data_segura(aula.get("data"))
                    horario_aula = aula.get("horario")
                    titulo_aula = aula.get("titulo", "")
                    
                    if data_aula and horario_aula and titulo_aula:
                        if not aulas_agendadas:
                            ax.text(
                                menor_inicio,
                                y_aulas,
                                "Aulas agendadas:",
                                ha="left",
                                va="bottom",
                                fontsize=8,
                                color="black",
                                style="italic",
                                fontweight="bold"
                            )
                            y_aulas -= 0.9
                            aulas_agendadas = True
                        
                        ax.text(
                            menor_inicio,
                            y_aulas,
                            f"  {titulo_aula}",
                            ha="left",
                            va="bottom",
                            fontsize=7,
                            color="darkblue"
                        )
                        y_aulas -= 0.7
                        
                        ax.text(
                            menor_inicio,
                            y_aulas,
                            f"  {data_aula.strftime('%d/%m/%Y')} às {horario_aula}",
                            ha="left",
                            va="bottom",
                            fontsize=6,
                            color="black"
                        )
                        y_aulas -= 0.7

            y_exercicios = y_aulas - 0.5
            exercicios_agendados = False
            
            for u_idx, unidade in enumerate(unidades):
                # Calcular data de finalização da unidade para usar como sugestão
                duracao_unid = dias_estudo / total_unid
                fim_unid_calc = inicio + timedelta(days=(u_idx + 1) * duracao_unid)
                num_unidade = u_idx + 1
                
                # Todos os exercícios da unidade (sem filtro de trabalho)
                ex_list = unidade.get("exercicios", []) or []

                for exercicio in ex_list:
                    titulo_exercicio = exercicio.get("titulo", "")

                    if titulo_exercicio:
                        data_entrega_real = parse_data_segura(exercicio.get("data_entrega_real"))
                        data_entrega_prev = parse_data_segura(exercicio.get("data_entrega"))
                        entregue_em = parse_data_segura(exercicio.get("entregue_em"))  # Campo entregue_em (opcional)
                        feito = exercicio.get("feito") is True
                        obs_exercicio = exercicio.get("obs", "")

                        if not exercicios_agendados:
                            ax.text(
                                menor_inicio,
                                y_exercicios,
                                "Exercícios agendados:",
                                ha="left",
                                va="bottom",
                                fontsize=8,
                                color="black",
                                style="italic",
                                fontweight="bold"
                            )
                            y_exercicios -= 0.9
                            exercicios_agendados = True
                        
                        # Determinar se finalizado ou pendente (considera NOTA válida)
                        nota_valida = exercicio.get("nota") is not None
                        finalizado = feito or (data_entrega_real is not None) or nota_valida
                        status_color = COR_EXERC_FINALIZADO if finalizado else COR_EXERC_PENDENTE
                        status_text = "[Finalizado]" if finalizado else "[Pendente]"
                        
                        # Exibir data de sugestão (finalização da unidade) e data prevista/real se houver
                        datas_info = [f"Un: {num_unidade}: Data Sugerida: {fim_unid_calc.strftime('%d/%m/%Y')}"]
                        
                        # Adicionar data de entrega (entregue_em) se existir e for válida
                        if entregue_em:
                            datas_info.append(f"Entregue em: {entregue_em.strftime('%d/%m/%Y')}")
                        
                        if data_entrega_prev:
                            datas_info.append(f"Fim prazo: {data_entrega_prev.strftime('%d/%m/%Y')}")
                        if data_entrega_real:
                            datas_info.append(f"Entregue: {data_entrega_real.strftime('%d/%m/%Y')}")
                        
                        # Mostrar nota se existir
                        if nota_valida:
                            nota = exercicio.get("nota")
                            if isinstance(nota, (int, float)):
                                datas_info.append(f"Nota: {nota:.1f}")
                            else:
                                datas_info.append(f"Nota: {nota}")
                        
                        datas_str = " - " + " / ".join(datas_info)
                        
                        ax.text(
                            menor_inicio,
                            y_exercicios,
                            f"  {titulo_exercicio} {status_text}{datas_str}",
                            ha="left",
                            va="bottom",
                            fontsize=6,
                            color=status_color,
                            fontweight="bold" if not finalizado else "normal"
                        )
                        y_exercicios -= 1.0
                        
                        if obs_exercicio:
                            ax.text(
                                menor_inicio,
                                y_exercicios,
                                f"  Obs: {obs_exercicio}",
                                ha="left",
                                va="bottom",
                                fontsize=5.5,
                                color="brown"
                            )
                            y_exercicios -= 0.8

            y_pos = min(y_aulas, y_exercicios) - 0.9

        # PERÍODO DE PROVAS (COM COR ORIGINAL)
        y_provas = y_pos
        provas = disc.get("provas", [])
        
        if provas:
            pass  # subtítulo 'PROVAS' removido conforme solicitado

        for i, prova in enumerate(provas):
            ini = parse_data_segura(prova.get("inicio"))
            fim_p = parse_data_segura(prova.get("fim"))
            if ini and fim_p:
                dias = (fim_p - ini).days or 1
                for j in range(dias):
                    frac = j / dias
                    data = ini + timedelta(days=j)
                    # Usando a cor original para provas
                    ax.barh(y_provas, 1, left=data, color=COR_PROVA_DEGRADE(frac),
                           height=ALTURA_BARRA * 0.8, edgecolor="white", linewidth=0.5)

                ax.text(ini - timedelta(days=0.5), y_provas,
                       f"Prova {i+1}: {ini.strftime('%d/%m')}-{fim_p.strftime('%d/%m')}",
                       ha="right", va="center", fontsize=8, color="darkred",
                       fontweight="bold")
                y_provas -= ALTURA_BARRA + 0.3

        y_pos = y_provas - ESPACO_ENTRE_SECOES

        # PERÍODO DE TRABALHOS (COM COR ORIGINAL)
        if fim_trab:
            # Barra do período de trabalhos
            ax.barh(y_pos, (fim_trab - inicio).days, left=inicio,
                   color=COR_TRABALHO, height=ALTURA_BARRA * 1.5,
                   alpha=0.7, edgecolor="gray", linewidth=2)

            ax.text(inicio + (fim_trab - inicio) / 2, y_pos,
                   f"Período dos trabalhos de {inicio.strftime('%d/%m')} até {fim_trab.strftime('%d/%m')}",
                   ha="center", va="center", fontsize=8, color="black",
                   fontweight="bold")

            # Entregas de trabalhos
            y_entregas = y_pos - ALTURA_BARRA - 0.2
            # Começar com os trabalhos declarados na disciplina
            trabalhos = list(disc.get("trabalhos", []))

            # Incluir exercícios declarados no nível da disciplina (sem unidade)
            # como entregas/trabalhos para exibição na seção de trabalhos
            disc_exercicios = disc.get("exercicios", []) or []
            for ex in disc_exercicios:
                # Mapear campos dos exercícios para o formato de 'trabalhos'
                trabalhos.append({
                    "id": ex.get("id"),
                    "data_prevista": ex.get("data_entrega"),
                    "data_entrega": ex.get("data_entrega_real"),
                    "titulo": ex.get("titulo"),
                    "nota": ex.get("nota") if isinstance(ex.get("nota"), (int, float)) else None
                })
            # Incluir também exercícios detectados dentro das unidades como trabalhos
            if disc_trabalhos:
                trabalhos.extend(disc_trabalhos)
            if trabalhos:
                pass  # subtítulo 'ENTREGAS' removido conforme solicitado

            # Datas sugeridas (se não houver datas reais)
            tem_datas_reais = any(parse_data_segura(t.get("data_entrega")) for t in trabalhos)
            
            if not tem_datas_reais and trabalhos:
                entrega_atual = inicio
                for idx, trab in enumerate(trabalhos):
                    data_prev = parse_data_segura(trab.get("data_prevista"))
                    if data_prev:
                        dias = (data_prev - entrega_atual).days or 1
                        cor = CORES_ENTREGA[idx % len(CORES_ENTREGA)]
                        ax.barh(y_entregas, dias, left=entrega_atual,
                                color=cor, height=ALTURA_BARRA * 0.4)
                        # Mostrar a data abaixo da tarja, em preto, para melhor legibilidade
                        label_y = y_entregas - (ALTURA_BARRA * 0.55)
                        # Mostrar a data de entrega sugerida no formato dd/mm/YYYY, alinhada à direita
                        ax.text(data_prev, label_y, data_prev.strftime('%d/%m/%Y'),
                                ha="right", va="top", fontsize=6, color="black",
                                fontweight="bold", clip_on=False)
                        entrega_atual = data_prev + timedelta(days=1)
                y_entregas -= ALTURA_BARRA + 0.15

            # Datas reais
            if tem_datas_reais:
                entrega_atual_real = inicio
                for idx, trab in enumerate(trabalhos):
                    data_real = parse_data_segura(trab.get("data_entrega"))
                    if data_real:
                        dias = (data_real - entrega_atual_real).days or 1
                        cor = COR_REAL_ENTREGA[idx % len(COR_REAL_ENTREGA)]
                        ax.barh(y_entregas, dias, left=entrega_atual_real,
                                color=cor, height=ALTURA_BARRA * 0.4)
                        # Mostrar a data real abaixo da tarja, em preto, alinhada à direita
                        label_y = y_entregas - (ALTURA_BARRA * 0.55)
                        ax.text(data_real, label_y, data_real.strftime('%d/%m/%Y'),
                                ha="right", va="top", fontsize=6, color="black",
                                fontweight="bold", clip_on=False)
                        entrega_atual_real = data_real + timedelta(days=1)
                y_entregas -= ALTURA_BARRA + 0.15

            y_pos = y_entregas - ESPACO_ENTRE_DISCIPLINAS

        # Linha separadora entre disciplinas
        ax.axhline(y_pos + ESPACO_ENTRE_DISCIPLINAS * 0.3, color="gray", 
                  linestyle="--", linewidth=0.8, alpha=0.6)

    # LEGENDA REMOVIDA (comentada)
    # legend_elements = [
    #     Patch(facecolor=COR_ESTUDO(0.5), label='Período de Estudos'),
    #     Patch(facecolor=CORES_UNIDADES[0], label='Unidades de Estudo'),
    #     Patch(facecolor=COR_PROGRESSO, label='Progresso nas Unidades'),
    #     Patch(facecolor=COR_FRACIONADO, label='Progresso fracionado'),
    #     Patch(facecolor=COR_PROVA_DEGRADE(0.5), label='Período de Provas'),
    #     Patch(facecolor=COR_TRABALHO, label='Período de Trabalhos'),
    #     Patch(facecolor=CORES_ENTREGA[0], label='Datas Sugeridas'),
    #     Patch(facecolor=COR_REAL_ENTREGA[0], label='Datas Reais'),
    #     Patch(facecolor=COR_HOJE, label='Data Atual')
    # ]
    # ax.legend(handles=legend_elements, loc='upper center', 
    #           bbox_to_anchor=(0.5, -0.05), ncol=4, fontsize=9,
    #           framealpha=0.9, fancybox=True, shadow=True)

    # CONFIGURAÇÕES FINAIS DO GRÁFICO
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    
    fig.autofmt_xdate(rotation=45)
    ax.set_xlabel("Linha do Tempo (Datas)", fontsize=11, fontweight="bold", labelpad=15)
    ax.set_yticks([])
    
    # Grid para melhor leitura
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.grid(axis="y", linestyle="--", alpha=0.1)
    
    # Limites do gráfico
    ax.set_xlim(menor_inicio - timedelta(days=5), maior_fim + timedelta(days=5))
    ax.set_ylim(y_pos - 1, ax.get_ylim()[1] + 1)
    
    # Fundo do gráfico
    ax.set_facecolor("#fafafa")
    fig.patch.set_facecolor("white")
    
    plt.tight_layout()
    if save_path:
        # salvar em alta resolução e fechar a figura sem abrir janela
        fig.savefig(save_path, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        print(f"✅ Preview salvo em: {save_path}")
    else:
        plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gerar cronograma de estudos")
    parser.add_argument("--save", help="Caminho para salvar o preview como PNG")
    parser.add_argument("--dpi", type=int, default=200, help="DPI para salvar a imagem")
    args = parser.parse_args()
    gerar_grafico(save_path=args.save, dpi=args.dpi)