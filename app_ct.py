import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re
import requests
from PIL import Image
from io import BytesIO

# --- Coloque este bloco aqui, logo após os imports ---
def carregar_logo(url):
    try:
        resposta = requests.get(url)
        resposta.raise_for_status()
        img = Image.open(BytesIO(resposta.content))
        return img
    except Exception as e:
        st.sidebar.error(f"Erro ao carregar logo: {e}")
        return None

url_logo = "https://raw.githubusercontent.com/Julia812-r/phisonct/main/logo.jpg
try:
    st.sidebar.image(url_logo, use_container_width=True)
except Exception as e:
    st.sidebar.write(f"Erro ao carregar imagem diretamente: {e}")
logo = carregar_logo(url_logo)

def formatar_cpf(cpf):
    numeros = re.sub(r'\D', '', str(cpf))
    if len(numeros) == 11:
        return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
    return cpf

def formatar_telefone(tel):
    numeros = re.sub(r'\D', '', str(tel))
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2]}{numeros[3:7]}-{numeros[7:]}"
    elif len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    return tel

def preparar_para_exibir(df):
    df_copy = df.copy()
    for col in df_copy.columns:
        if len(df_copy[col].dropna()) > 0:
            primeiro_valor = df_copy[col].dropna().iloc[0]
            if pd.api.types.is_datetime64_any_dtype(df_copy[col]) or isinstance(primeiro_valor, (datetime, pd.Timestamp)):
                df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce').dt.strftime("%Y-%m-%d")

    if "CPF" in df_copy.columns:
        df_copy["CPF"] = df_copy["CPF"].apply(formatar_cpf)
    if "Celular" in df_copy.columns:
        df_copy["Celular"] = df_copy["Celular"].apply(formatar_telefone)
    if "Telefone" in df_copy.columns:
        df_copy["Telefone"] = df_copy["Telefone"].apply(formatar_telefone)
    return df_copy

# Caminhos para salvar os dados
ALUNOS_PATH = "dados_alunos.csv"
FINANCEIRO_PATH = "dados_financeiro.csv"
HORARIOS_PATH = "dados_horarios.csv"
PROFS_PATH = "dados_professores.csv"
DESPESAS_PATH = "dados_despesas.csv"

# Função para carregar CSV ou criar vazio
def carregar_dados(caminho, colunas):
    if os.path.exists(caminho):
        parse_dates_cols = [col for col in ["Data", "Data de Pagamento", "Nascimento"] if col in colunas]
        if parse_dates_cols:
            return pd.read_csv(caminho, parse_dates=parse_dates_cols)
        else:
            return pd.read_csv(caminho)
    else:
        return pd.DataFrame(columns=colunas)

def salvar_dados():
    st.session_state.alunos.to_csv(ALUNOS_PATH, index=False)
    st.session_state.financeiro.to_csv(FINANCEIRO_PATH, index=False)
    st.session_state.horarios.to_csv(HORARIOS_PATH, index=False)
    st.session_state.professores.to_csv(PROFS_PATH, index=False)
    st.session_state.despesas.to_csv(DESPESAS_PATH, index=False)

def preparar_para_exibir(df):
    df_copy = df.copy()
    for col in df_copy.columns:
        if len(df_copy[col].dropna()) > 0:
            primeiro_valor = df_copy[col].dropna().iloc[0]
            if pd.api.types.is_datetime64_any_dtype(df_copy[col]) or isinstance(primeiro_valor, (datetime, pd.Timestamp)):
                df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce').dt.strftime("%Y-%m-%d")
    return df_copy

# Inicialização dos dados no session_state
if 'alunos' not in st.session_state:
    st.session_state.alunos = carregar_dados(ALUNOS_PATH, ["Nome", "CPF", "Nascimento", "Celular", "Email", "Plano", "Periodicidade", "Valor", "Vencimento", "Necessidades", "Status"])

if 'financeiro' not in st.session_state:
    st.session_state.financeiro = carregar_dados(FINANCEIRO_PATH, ["Data", "Tipo", "Descrição", "Valor"])

if 'horarios' not in st.session_state:
    st.session_state.horarios = carregar_dados(HORARIOS_PATH, ["Dia", "Hora", "Professor", "Alunos"])

if 'professores' not in st.session_state:
    st.session_state.professores = carregar_dados(PROFS_PATH, ["Nome", "CPF", "Telefone", "Email", "Data de Pagamento"])

if 'despesas' not in st.session_state:
    st.session_state.despesas = carregar_dados(DESPESAS_PATH, ["Descrição", "Valor", "Dia Vencimento"])

if logo:
    st.sidebar.image(logo, use_container_width=True)
else:
    st.sidebar.write("Logo não disponível")


st.markdown(
    """
    <h1 style='text-align: center; font-weight: 900; font-size: 3.5rem; margin-bottom: 1rem;'>
        PHISON
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
        /* Sidebar preta */
        [data-testid="stSidebar"] {
            background-color: black;
        }

        /* Textos gerais em preto */
        [data-testid="stSidebar"] * {
            color: black !important;
        }

        /* Label "Menu" branca */
        section[data-testid="stSidebar"] label {
            color: white !important;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True
)

menu = st.sidebar.selectbox("Menu", [
    "Cadastro de Alunos", 
    "Histórico de Alunos", 
    "Horários", 
    "Mensalidades", 
    "Cadastro de Professores",
    "Controle Carga Horária Professores", 
    "Financeiro",
    "Despesas Mensais"
])


if menu == "Despesas Mensais":
    st.subheader("Cadastro e controle de despesas mensais")

    with st.form("form_despesas"):
        descricao = st.text_input("Descrição da despesa")
        valor = st.number_input("Valor da despesa", min_value=0.0, step=50.0)
        dia_vencimento = st.number_input("Dia de vencimento", min_value=1, max_value=31)

        cadastrar = st.form_submit_button("Cadastrar despesa")
        if cadastrar:
            nova = {"Descrição": descricao, "Valor": valor, "Dia Vencimento": dia_vencimento}
            st.session_state.despesas = pd.concat([st.session_state.despesas, pd.DataFrame([nova])], ignore_index=True)
            salvar_dados()
            st.success("Despesa cadastrada com sucesso!")

    st.subheader("Despesas cadastradas")

    if not st.session_state.despesas.empty:
        df_despesas = st.session_state.despesas.copy()
        st.dataframe(preparar_para_exibir(df_despesas))

        despesa_selecionada = st.selectbox("Selecione uma despesa", st.session_state.despesas["Descrição"].tolist())

        col1, col2 = st.columns(2)

        if "editando_despesa" not in st.session_state:
            st.session_state.editando_despesa = False
        if "excluindo_despesa" not in st.session_state:
            st.session_state.excluindo_despesa = False

        if col1.button("Editar despesa"):
            st.session_state.editando_despesa = True
            st.session_state.excluindo_despesa = False

        if col2.button("Excluir despesa"):
            st.session_state.excluindo_despesa = True
            st.session_state.editando_despesa = False

        idx = st.session_state.despesas[st.session_state.despesas["Descrição"] == despesa_selecionada].index[0]
        despesa = st.session_state.despesas.loc[idx]

        if st.session_state.editando_despesa:
            with st.form("form_editar_despesa"):
                descricao_edit = st.text_input("Descrição", despesa["Descrição"])
                valor_edit = st.number_input("Valor", value=float(despesa["Valor"]))
                dia_venc = st.number_input("Dia de vencimento", value=int(despesa["Dia Vencimento"]), min_value=1, max_value=31)

                pagar = st.checkbox("Marcar como paga e enviar para financeiro")

                atualizar = st.form_submit_button("Atualizar despesa")
                if atualizar:
                    st.session_state.despesas.loc[idx] = [descricao_edit, valor_edit, dia_venc]
                    if pagar:
                        novo_mov = {
                            "Data": datetime.today(),
                            "Tipo": "Saída",
                            "Descrição": f"Pagamento despesa - {descricao_edit}",
                            "Valor": valor_edit
                        }
                        st.session_state.financeiro = pd.concat([st.session_state.financeiro, pd.DataFrame([novo_mov])], ignore_index=True)
                        st.success("Despesa marcada como paga e registrada no financeiro!")

                    salvar_dados()
                    st.success("Despesa atualizada!")
                    st.session_state.editando_despesa = False

        if st.session_state.excluindo_despesa:
            confirmar_excluir = st.checkbox("Confirmar exclusão desta despesa")
            if st.button("Excluir agora"):
                if confirmar_excluir:
                    st.session_state.despesas = st.session_state.despesas.drop(idx).reset_index(drop=True)
                    salvar_dados()
                    st.success("Despesa excluída!")
                    st.session_state.excluindo_despesa = False
                else:
                    st.warning("Marque a caixa para confirmar a exclusão.")

    else:
        st.info("Nenhuma despesa cadastrada.")


if menu == "Cadastro de Alunos":
    st.subheader("Cadastrar novo aluno")
    nome = st.text_input("Nome completo")
    cpf = st.text_input("CPF")
    nascimento = st.date_input("Data de nascimento", min_value=datetime(datetime.today().year - 65, 1, 1), max_value=datetime.today())
    celular = st.text_input("Celular")
    email = st.text_input("Email")
    plano = st.selectbox("Tipo de Plano", ["Mensal", "Semestral", "Anual"])
    periodicidade = st.selectbox("Periodicidade", ["Segunda, Quarta, Sexta", "Terça e Quinta"])
    valor = st.number_input("Valor da mensalidade", min_value=0.0, step=50.0)
    vencimento = st.number_input("Dia de vencimento", min_value=1, max_value=31)
    necessidades = st.text_area("Necessidades especiais (opcional)")
    status = st.selectbox("Status", ["Ativo", "Não Ativo"])

    if st.button("Salvar aluno"):
        cpf_formatado = formatar_cpf(cpf)
        celular_formatado = formatar_telefone(celular)
        novo = {
            "Nome": nome,
            "CPF": cpf_formatado,
            "Nascimento": nascimento,
            "Celular": celular_formatado,
            "Email": email,
            "Plano": plano,
            "Periodicidade": periodicidade,
            "Valor": valor,
            "Vencimento": vencimento,
            "Necessidades": necessidades,
            "Status": status
        }
        st.session_state.alunos = pd.concat([st.session_state.alunos, pd.DataFrame([novo])], ignore_index=True)
        salvar_dados()
        st.success("Aluno cadastrado!")


elif menu == "Histórico de Alunos":
 

    if not st.session_state.alunos.empty:

        # Aniversariantes do mês
        st.write("### Aniversariantes do mês")
        hoje = datetime.today()
        alunos_aniversariantes = st.session_state.alunos.copy()
        alunos_aniversariantes["Nascimento"] = pd.to_datetime(alunos_aniversariantes["Nascimento"], errors='coerce')
        aniversariantes_mes = alunos_aniversariantes[alunos_aniversariantes["Nascimento"].dt.month == hoje.month]

        if not aniversariantes_mes.empty:
            st.dataframe(preparar_para_exibir(aniversariantes_mes))
        else:
            st.info("Nenhum aniversariante neste mês.")

        # Mensalidades a vencer nos próximos 7 dias
        st.write("### Mensalidades a vencer nos próximos 7 dias")
        alunos_vencimento = st.session_state.alunos.copy()
        hoje_dia = hoje.day
        dias_proximos = [(hoje + pd.Timedelta(days=i)).day for i in range(0, 7)]

        alunos_vencimento_prox = alunos_vencimento[
            alunos_vencimento["Vencimento"].isin(dias_proximos)
            & (alunos_vencimento["Status"] == "Ativo")
        ]

        if not alunos_vencimento_prox.empty:
            st.dataframe(preparar_para_exibir(alunos_vencimento_prox))
        else:
            st.info("Nenhuma mensalidade vencendo nos próximos 7 dias.")

    st.subheader("Histórico de Alunos")
    if not st.session_state.alunos.empty:
        # Separa ativos e não ativos
        df_ativos = st.session_state.alunos[st.session_state.alunos["Status"] == "Ativo"]
        df_nao_ativos = st.session_state.alunos[st.session_state.alunos["Status"] == "Não Ativo"]

        st.write("### Alunos Ativos")
        df_ativos = st.session_state.alunos[st.session_state.alunos["Status"] == "Ativo"]
        if not df_ativos.empty:
            st.dataframe(preparar_para_exibir(df_ativos))
        else:
            st.info("Nenhum aluno ativo.")

        st.write("### Alunos Não Ativos")
        df_nao_ativos = st.session_state.alunos[st.session_state.alunos["Status"] == "Não Ativo"]
        if not df_nao_ativos.empty:
            st.dataframe(preparar_para_exibir(df_nao_ativos))
        else:
            st.info("Nenhum aluno não ativo.")

        aluno_editar = st.selectbox(
            "Selecione o aluno para editar ou excluir",
            st.session_state.alunos["Nome"].tolist()
        )
        idx = st.session_state.alunos[st.session_state.alunos["Nome"] == aluno_editar].index[0]
        aluno = st.session_state.alunos.loc[idx]

        col1, col2 = st.columns(2)

        if "editando_aluno" not in st.session_state:
            st.session_state.editando_aluno = False

        if col1.button("Editar aluno"):
            st.session_state.editando_aluno = True

        if st.session_state.editando_aluno:
            with st.form("form_edicao"):
                nome = st.text_input("Nome completo", aluno["Nome"])
                cpf = st.text_input("CPF", aluno["CPF"])
                nascimento = st.date_input("Nascimento", pd.to_datetime(aluno["Nascimento"]))
                celular = st.text_input("Celular", aluno["Celular"])
                email = st.text_input("Email", aluno["Email"])
                plano = st.selectbox("Plano", ["Mensal", "Semestral", "Anual"], index=["Mensal", "Semestral", "Anual"].index(aluno["Plano"]))
                periodicidade = st.selectbox("Periodicidade", ["Segunda, Quarta, Sexta", "Terça e Quinta"], index=["Segunda, Quarta, Sexta", "Terça e Quinta"].index(aluno["Periodicidade"]))
                valor = st.number_input("Valor", value=float(aluno["Valor"]))
                vencimento = st.number_input("Vencimento", value=int(aluno["Vencimento"]))
                necessidades = st.text_area("Necessidades", aluno["Necessidades"])
                status = st.selectbox("Status", ["Ativo", "Não Ativo"], index=["Ativo", "Não Ativo"].index(aluno["Status"]))

                confirmar_atualizacao = st.checkbox("Confirmar atualização antes de salvar")

                atualizar = st.form_submit_button("Atualizar")
                if atualizar:
                    if confirmar_atualizacao:
                        st.session_state.alunos.loc[idx] = [nome, cpf, nascimento, celular, email, plano, periodicidade, valor, vencimento, necessidades, status]
                        salvar_dados()
                        st.success("Informações atualizadas!")
                        st.session_state.editando_aluno = False
                    else:
                        st.warning("Marque o checkbox para confirmar a atualização antes de salvar.")

        if col2.button("Excluir aluno"):
            st.session_state.alunos = st.session_state.alunos.drop(idx).reset_index(drop=True)
            salvar_dados()
            st.success("Aluno excluído!")
            st.session_state.editando_aluno = False

    else:
        st.info("Nenhum aluno cadastrado.")


elif menu == "Horários":
    st.subheader("Horários por dia e hora")

    filtrar_ativos = st.checkbox("Mostrar apenas alunos ativos", value=True)
    alunos_disponiveis = st.session_state.alunos
    if filtrar_ativos:
        alunos_disponiveis = alunos_disponiveis[alunos_disponiveis["Status"] == "Ativo"]

    nomes_alunos = alunos_disponiveis["Nome"].tolist()
    profs_cadastrados = st.session_state.professores["Nome"].tolist()

    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
    horas = [f"{str(h).zfill(2)}:00 - {str(h+1).zfill(2)}:00" for h in range(5, 21)]

    for dia in dias:
        with st.expander(f"{dia}"):
            for hora in horas:
                st.markdown(f"### {hora}")
                key_base = f"{dia}_{hora}"

                filtro = (st.session_state.horarios["Dia"] == dia) & (st.session_state.horarios["Hora"] == hora)
                if filtro.any():
                    linha = st.session_state.horarios[filtro].iloc[-1]
                    alunos_salvos_str = linha["Alunos"]
                    if isinstance(alunos_salvos_str, str) and alunos_salvos_str.strip():
                        alunos_salvos = alunos_salvos_str.split(", ")
                    else:
                        alunos_salvos = []
                    professor_salvo = linha["Professor"]
                else:
                    alunos_salvos = []
                    professor_salvo = None

                num_alunos = len(alunos_salvos)

                if num_alunos < 4:
                    cor_texto = "green"
                    mensagem_status = f" Vagas disponíveis ({4 - num_alunos} vagas)"
                else:
                    cor_texto = "red"
                    mensagem_status = "⚠️ Horário cheio"

                st.markdown(f'<p style="color:{cor_texto}; font-weight:bold;">{mensagem_status}</p>', unsafe_allow_html=True)

              # Filtra os alunos salvos para garantir que existem na lista atual de nomes
                alunos_salvos_validos = [aluno for aluno in alunos_salvos if aluno in nomes_alunos]

                alunos_selecionados = st.multiselect(
                    "Selecionar alunos (máx 4)",
                    nomes_alunos,
                    default=alunos_salvos_validos,
                    key=f"{key_base}_alunos"
                )

                if len(alunos_selecionados) > 4:
                    st.warning("Você pode selecionar no máximo 4 alunos por horário.")
                    alunos_selecionados = alunos_selecionados[:4]

                professor = st.selectbox(
                    "Professor",
                    ["Nenhum"] + profs_cadastrados,
                    index=(profs_cadastrados.index(professor_salvo) + 1) if professor_salvo in profs_cadastrados else 0,
                    key=f"{key_base}_prof"
                )
                if professor == "Nenhum":
                    professor = ""

                if st.button("Salvar", key=f"{key_base}_btn"):
                    novo_horario = {
                        "Dia": dia,
                        "Hora": hora,
                        "Professor": professor,
                        "Alunos": ", ".join(alunos_selecionados)
                    }
                    st.session_state.horarios = st.session_state.horarios[~filtro]
                    st.session_state.horarios = pd.concat([st.session_state.horarios, pd.DataFrame([novo_horario])], ignore_index=True)
                    salvar_dados()
                    st.success(f"Horário salvo para {dia} {hora}")

                if len(alunos_selecionados) >= 4:
                    st.markdown(f'<p style="color:red"><b>⚠️ Horário cheio com 4 alunos!</b></p>', unsafe_allow_html=True)

    st.subheader("Horários cadastrados")

    if not st.session_state.horarios.empty:
        df_horarios = st.session_state.horarios.reset_index(drop=True)

        # Montar lista de opções para excluir
        opcoes = []
        for idx, row in df_horarios.iterrows():
            descricao = f"{row['Dia']} - {row['Hora']}"
            opcoes.append((idx, descricao))

        # Cria selectbox com apenas dia e hora
        opcoes_labels = [desc for _, desc in opcoes]
        indice_selecionado = st.selectbox("Selecione um horário para excluir", options=opcoes_labels)

        # Encontra índice do dataframe
        idx_selecionado = [i for i, desc in opcoes if desc == indice_selecionado][0]

        if st.button("Excluir horário selecionado"):
            st.session_state.horarios = st.session_state.horarios.drop(idx_selecionado).reset_index(drop=True)
            salvar_dados()
            st.success("Horário excluído com sucesso!")
            st.rerun()

        # Exibe a tabela
        st.dataframe(preparar_para_exibir(st.session_state.horarios))
    else:
        st.info("Nenhum horário cadastrado.")


elif menu == "Mensalidades":
    st.subheader("Controle de mensalidades")

    if st.session_state.alunos.empty:
        st.warning("Não há alunos cadastrados.")
    else:
        aluno = st.selectbox("Aluno", st.session_state.alunos["Nome"].tolist())
        valor = st.number_input("Valor pago", min_value=0.0, step=50.0)
        data_pagamento = st.date_input("Data de pagamento", value=datetime.today())
        forma = st.selectbox("Forma de pagamento", ["PIX", "Débito", "Crédito", "Dinheiro"])

        if st.button("Registrar pagamento"):
            novo = {"Data": data_pagamento, "Tipo": "Entrada", "Descrição": f"Mensalidade - {aluno} ({forma})", "Valor": valor}
            st.session_state.financeiro = pd.concat([st.session_state.financeiro, pd.DataFrame([novo])], ignore_index=True)
            salvar_dados()
            st.success("Pagamento registrado!")

        st.subheader("Pagamentos registrados")
        entradas = st.session_state.financeiro[st.session_state.financeiro["Tipo"] == "Entrada"]
        st.dataframe(preparar_para_exibir(entradas))

elif menu == "Cadastro de Professores":
    st.subheader("Cadastro de Professores")

    with st.form("form_prof"):
        nome = st.text_input("Nome")
        cpf = st.text_input("CPF")
        telefone = st.text_input("Telefone")
        email = st.text_input("Email")
        data_pagamento = st.date_input("Data de pagamento")

        cadastrar = st.form_submit_button("Cadastrar")
        if cadastrar:
            cpf_formatado = formatar_cpf(cpf)
            telefone_formatado = formatar_telefone(telefone)
            novo = {
                "Nome": nome,
                "CPF": cpf_formatado,
                "Telefone": telefone_formatado,
                "Email": email,
                "Data de Pagamento": data_pagamento
            }
            st.session_state.professores = pd.concat([st.session_state.professores, pd.DataFrame([novo])], ignore_index=True)
            salvar_dados()
            st.success("Professor cadastrado com sucesso!")       

elif menu == "Controle Carga Horária Professores":
    st.subheader("Controle de carga horária dos professores")

    profs = st.session_state.professores["Nome"].tolist()
    for prof in profs:
        aulas = st.session_state.horarios[st.session_state.horarios["Professor"] == prof]
        num_aulas = aulas.shape[0]
        pagamento = num_aulas * 22
        st.write(f"**{prof}** - {num_aulas} aulas - R$ {pagamento:.2f}")

elif menu == "Financeiro":
    st.subheader("Controle financeiro geral")

    if st.session_state.financeiro.empty:
        st.info("Nenhum movimento financeiro registrado.")
    else:
        df_fin = st.session_state.financeiro.copy()
        df_fin["Data"] = pd.to_datetime(df_fin["Data"], errors='coerce')

        anos = sorted(list(set(df_fin["Data"].dt.year.dropna())), reverse=True)
        ano = st.selectbox("Ano", anos, index=0 if anos else 0)
        meses = ["Todos"] + list(range(1, 13))
        mes = st.selectbox("Mês", meses)

        df_filtrado = df_fin[df_fin["Data"].dt.year == ano]

        if mes != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Data"].dt.month == mes]

        tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor", min_value=0.0, step=50.0)
        data_fin = st.date_input("Data", value=datetime.today())

        if st.button("Registrar movimento"):
            novo = {"Data": data_fin, "Tipo": tipo, "Descrição": descricao, "Valor": valor}
            st.session_state.financeiro = pd.concat([st.session_state.financeiro, pd.DataFrame([novo])], ignore_index=True)
            salvar_dados()
            st.success("Movimento registrado!")

        st.subheader("Resumo")
        total_entradas = df_filtrado[df_filtrado["Tipo"] == "Entrada"]["Valor"].sum()
        total_saidas = df_filtrado[df_filtrado["Tipo"] == "Saída"]["Valor"].sum()
        saldo = total_entradas - total_saidas

        st.metric("Entradas", f"R$ {total_entradas:.2f}")
        st.metric("Saídas", f"R$ {total_saidas:.2f}")
        st.metric("Saldo", f"R$ {saldo:.2f}")

        st.dataframe(preparar_para_exibir(df_filtrado))          
