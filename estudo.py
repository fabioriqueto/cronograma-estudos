import json
import os, time
from datetime import datetime, timedelta
from utils import clear_screen

ARQUIVO_JSON = "cronograma_estudos.json"

# ---------------- UTILITÁRIAS ---------------- #

def salvar_dados(disciplinas):
    with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(disciplinas, f, indent=4, ensure_ascii=False)

def carregar_dados():
    if os.path.exists(ARQUIVO_JSON):
        with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def input_data(msg, obrigatoria=True):
    while True:
        entrada = input(msg + " (dd/mm/aaaa ou Enter para pular): ").strip()
        if not entrada and not obrigatoria:
            return None
        try:
            data = datetime.strptime(entrada, "%d/%m/%Y")
            return data
        except ValueError:
            print("❌ Data inválida. Use o formato dd/mm/aaaa.")
            time.sleep(2)
            clear_screen()

def distribuir_datas(inicio, fim, quantidade):
    if quantidade <= 0:
        return []
    delta = (fim - inicio) / quantidade
    return [(inicio + delta * i).strftime("%d/%m/%Y") for i in range(1, quantidade + 1)]

# ---------------- DISCIPLINAS ---------------- #

def adicionar_disciplina(disciplinas):
    trabalhos = []
    unidades = []
    clear_screen()
    nome = input("📘 Nome da disciplina: ")
    inicio = input_data("📅 Data de início da disciplina")
    fim = input_data("🏁 Data de término da disciplina")

    fim_trabalhos = None
    qtd_trabalhos = int(input("✏️ Quantos trabalhos a disciplina terá? "))
    if qtd_trabalhos > 0:
        fim_trabalhos = input_data("📦 Data final de entrega dos trabalhos")

    
    
    
    confirm = input(f"Existe Prova? (s/n): ").lower()
    provas = []
    if confirm == 's':
        qtd_provas = int(input("Quantos períodos de prova? "))
        for i in range(qtd_provas):
            print(f"📘 Prova {i+1}:")
            prova_inicio = input_data("🧾 Data de início da prova")
            prova_fim = input_data("🏁 Data final da prova")
            provas.append({
                "id": i+1,
                "inicio": prova_inicio.strftime("%d/%m/%Y"),
                "fim": prova_fim.strftime("%d/%m/%Y"),
                "nota": None
            })

    qtd_unidades = int(input("📚 Quantas unidades a disciplina possui? "))
    if qtd_unidades > 0:
        print("Agora, informe os detalhes de cada unidade.")
        for u in range(qtd_unidades):
            print(f"\n--- Unidade {u+1} ---")
            titulo_unidade = input(f"Título da unidade {u+1}: ") or f"Unidade {u+1}"
            qtd_aulas = int(input(f"📖 Quantas aulas na unidade {u+1}? "))
            if qtd_aulas <= 0:
                qtd_aulas = 1
            aulas = [
                {
                    "id": i+1,
                    "titulo": f"Aula {i+1}",
                    "data": None,
                    "horario": None,
                    "assistida": False,
                    "leitura": False
                } for i in range(qtd_aulas)
            ]
            exercicios = []
            qtd_ex = int(input(f"📝 Quantos exercícios para {titulo_unidade}? "))
            for e in range(qtd_ex):
                print(f"➡️ Exercício {e+1}:")
                titulo_ex = input("Título do exercício: ") or f"Exercício {e+1}"
                data_entrega = input_data("Data de entrega (opcional)", obrigatoria=False)
                if not data_entrega:
                    data_entrega = fim  # usa a data final da disciplina
                exercicios.append({
                    "id": e+1,
                    "titulo": titulo_ex,
                    "data_entrega": data_entrega.strftime("%d/%m/%Y"),
                    "nota": None
                })
            unidades.append({
                "id": u+1,
                "titulo": titulo_unidade,
                "aulas": aulas,
                "exercicios": exercicios
            })

    # Trabalhos
    if qtd_trabalhos > 0 and fim_trabalhos:
        datas_trabalho_prevista = distribuir_datas(inicio, fim_trabalhos, qtd_trabalhos)
        trabalhos = []
        print("\n📦 Agora informe (opcionalmente) as datas reais de entrega de cada trabalho:")
        for i, data_prevista in enumerate(datas_trabalho_prevista, start=1):
            print(f"Trabalho {i} - Data sugerida: {data_prevista}")
            data_real = input_data("Data real de entrega (opcional)", obrigatoria=False)
            trabalhos.append({
                "id": i,
                "data_prevista": data_prevista,  # gerada automaticamente
                "data_entrega": data_real.strftime("%d/%m/%Y") if data_real else None,
                "nota": None
            })

    disciplinas.append({
        "nome": nome,
        "inicio": inicio.strftime("%d/%m/%Y"),
        "fim": fim.strftime("%d/%m/%Y"),
        "fim_trabalhos": fim_trabalhos.strftime("%d/%m/%Y") if fim_trabalhos else None,
        "provas": provas,
        "status": "Cursando",
        "unidades": unidades,
        "trabalhos": trabalhos
    })
    salvar_dados(disciplinas)
    print(f"✅ Disciplina '{nome}' adicionada com sucesso!\n")
    time.sleep(2)

# ---------------- EDITAR DISCIPLINA ---------------- #

def editar_disciplina(disciplinas):
    clear_screen()
    listar_disciplinas(disciplinas)
    idx = int(input("Informe o número da disciplina para editar: ")) - 1
    if not (0 <= idx < len(disciplinas)):
        print("❌ Opção inválida.")
        time.sleep(2)
        return

    disc = disciplinas[idx]
    print(f"✏️ Editando {disc['nome']}")

    novo_nome = input(f"Novo nome ({disc['nome']}): ").strip()
    if novo_nome:
        disc["nome"] = novo_nome

    nova_data_inicio = input(f"Nova data de início ({disc['inicio']}): ").strip()
    if nova_data_inicio:
        disc["inicio"] = nova_data_inicio

    nova_data_fim = input(f"Nova data de término ({disc['fim']}): ").strip()
    if nova_data_fim:
        disc["fim"] = nova_data_fim

    # Editar provas
    alterar_provas = input("Deseja alterar os períodos de prova? (s/n): ").lower()
    if alterar_provas == 's':
        provas = []
        qtd_provas = int(input("Quantos períodos de prova? "))
        for i in range(qtd_provas):
            print(f"📘 Prova {i+1}:")
            prova_inicio = input_data("🧾 Data de início da prova")
            prova_fim = input_data("🏁 Data final da prova")
            nota = input("Nota (ou Enter se não houver): ").strip() or None
            provas.append({
                "id": i+1,
                "inicio": prova_inicio.strftime("%d/%m/%Y"),
                "fim": prova_fim.strftime("%d/%m/%Y"),
                "nota": float(nota) if nota else None
            })
        disc["provas"] = provas

    salvar_dados(disciplinas)
    print("✅ Disciplina atualizada com sucesso!")
    time.sleep(2)

# ---------------- OUTRAS FUNÇÕES ---------------- #

def excluir_disciplina(disciplinas):
    clear_screen()
    listar_disciplinas(disciplinas)
    idx = int(input("Informe o número da disciplina para excluir: ")) - 1
    if 0 <= idx < len(disciplinas):
        nome = disciplinas[idx]['nome']
        confirm = input(f"Tem certeza que deseja excluir '{nome}'? (s/n): ").lower()
        if confirm == 's':
            disciplinas.pop(idx)
            salvar_dados(disciplinas)
            print(f"🗑️ Disciplina '{nome}' removida.")
    else:
        print("❌ Opção inválida.")
    time.sleep(2)

def listar_disciplinas(disciplinas):
    print("\n📚 Disciplinas:")
    for i, d in enumerate(disciplinas, start=1):
        print(f"{i}. {d['nome']}")
    print()

# ---------------- MAIN ---------------- #

def main():
    disciplinas = carregar_dados()
    while True:
        clear_screen()
        print("\n📘 MENU PRINCIPAL")
        print("1. Adicionar disciplina")
        print("2. Editar disciplina")
        print("3. Excluir disciplina")
        print("4. Listar disciplinas")
        print("5. Sair")
        opc = input("Escolha: ")

        if opc == "1":
            adicionar_disciplina(disciplinas)
        elif opc == "2":
            editar_disciplina(disciplinas)
        elif opc == "3":
            excluir_disciplina(disciplinas)
        elif opc == "4":
            listar_disciplinas(disciplinas)
            input("Pressione Enter para continuar...")
        elif opc == "5":
            break
        else:
            print("❌ Opção inválida.")
        time.sleep(2)

if __name__ == "__main__":
    main()
