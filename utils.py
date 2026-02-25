import json, os, re, time
from datetime import datetime

def clear_screen():
    """Limpa a tela do console."""
    # Para Windows
    if os.name == 'nt':
        os.system('cls')
    # Para Linux e macOS
    else:
        os.system('clear')


def limpar_cpf(cpf: str) -> str:
    """Remove qualquer caractere não numérico."""
    return re.sub(r"\D", "", cpf or "")

def validar_cpf(cpf: str) -> bool:
    """
    Retorna True se o CPF for válido, False caso contrário.
    Regras:
      - 11 dígitos
      - não pode ter todos os dígitos iguais
      - dígitos verificadores conforme módulo 11
    """
    cpf_num = limpar_cpf(cpf)

    # tamanho correto
    if len(cpf_num) != 11:
        return False

    # rejeita sequências do tipo 00000000000, 11111111111, etc.
#    if cpf_num == cpf_num[0] * 11:
#        return False

    # calcula 1º dígito verificador
    soma = sum(int(d) * peso for d, peso in zip(cpf_num[:9], range(10, 1, -1)))
    resto = soma % 11
    dv1 = 0 if resto < 2 else 11 - resto
    if dv1 != int(cpf_num[9]):
        return False

    # calcula 2º dígito verificador
    soma = sum(int(d) * peso for d, peso in zip(cpf_num[:10], range(11, 1, -1)))
    resto = soma % 11
    dv2 = 0 if resto < 2 else 11 - resto
    if dv2 != int(cpf_num[10]):
        return False

    return True

def formatar_cpf(cpf: str) -> str:
    """Formata para XXX.XXX.XXX-YY se tiver 11 dígitos; caso contrário, retorna original."""
    cpf_num = limpar_cpf(cpf)
    if len(cpf_num) != 11:
        return cpf
    return f"{cpf_num[:3]}.{cpf_num[3:6]}.{cpf_num[6:9]}-{cpf_num[9:]}"


# -------------------------------
# Tratamento de Data de Nascimento
# -------------------------------
def validar_data_nascimento(data_str: str) -> datetime | None:
    """
    Valida e converte a data de nascimento no formato DD/MM/AAAA.
    Retorna um objeto datetime ou None se for inválida.
    """
    try:
        return datetime.strptime(data_str, "%d/%m/%Y")
    except ValueError:
        return None


def calcular_idade(data_nascimento: datetime) -> int:
    """
    Calcula a idade em anos a partir da data de nascimento.
    """
    hoje = datetime.today()
    idade = hoje.year - data_nascimento.year
    if (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day):
        idade -= 1
    return idade


# -------------------------------
# Tratamento de Nome
# -------------------------------
def tratar_nome(nome: str) -> str:
    """
    Remove espaços extras, caracteres inválidos e capitaliza cada palavra.
    """
    if not nome:
        return ""
    nome = re.sub(r"[^a-zA-ZÀ-ÿ\s]", "", nome)  # mantém letras e acentos
    return " ".join(nome.split()).title()


# -------------------------------
# Tratamento de Telefone
# -------------------------------
def tratar_telefone(telefone: str) -> str | None:
    """
    Valida e formata número de telefone (com DDD).
    Retorna no formato (XX) XXXXX-XXXX ou None se inválido.
    """
    numeros = re.sub(r"\D", "", telefone)
    
    if len(numeros) == 10:  # Ex: fixo (XX) XXXX-XXXX
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    elif len(numeros) == 11:  # Ex: celular (XX) XXXXX-XXXX
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    else:
        return None

# -------------------------------
# Tratamento de idade
# -------------------------------
def tratar_idade(valor: str) -> int:
    """
    Trata a entrada da idade do paciente.
    - Converte para inteiro
    - Garante que está em um intervalo válido (0 a 120)
    """
    while True:
        if not valor.isdigit():
            valor = input("❌ Idade inválida. Digite apenas números: ")
            continue
        
        idade = int(valor)
        
        if idade < 0 or idade > 120:
            valor = input("❌ Idade fora do intervalo válido (0-120). Digite novamente: ")
            continue
        
        return idade

def input_sn(msg: str = "Digite S para sim ou N para não: ") -> str:
    while True:
        entrada = input(msg).strip().upper()
        if entrada in ["S", "N"]:
            return entrada
        print("Entrada inválida! Digite apenas S ou N.")
        
def input_default(msg, default=""):
    entrada = input(f"{msg} [{default}]: ").strip()
    return entrada if entrada else default