import streamlit as st

st.title("SIMULADOR - conjugação de esquemas de Corte")
import streamlit as st
import pandas as pd

# 1. Configuração da página (deixa a tela larga como no seu design)
st.set_page_config(page_title="MAGNERA - Otimizador", layout="wide")

# 2. Cabeçalho
st.title("MAGNERA")
st.caption("Possibilities Made Real")
st.markdown("---")

# 3. Bloco Superior: Especificações e Restrições
col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("ESPECIFICAÇÕES DO MATERIAL")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.selectbox("MÁQUINA", ["PAL01","PAL02","SJP05","SJP06","SJP07""SJP08", "SJP09"])
        st.selectbox("CALANDRA", ["OVAL","ESTRELA"])
    with c2:
        st.selectbox("TECNOLOGIA", ["SMS", "SSS"])
        st.number_input("GRAMATURA (GSM)", value=11)
    with c3:
        st.selectbox("SURFACTANTE", ["HFO","HFL","ZEB"])
        st.number_input("METRAGEM LINEAR (M)", value=13500, step=100)

with col_dir:
    st.subheader("RESTRIÇÕES DE CORTE")
    c4, c5 = st.columns(2)
    with c4:
        st.number_input("LARGURA ÚTIL (MM)", value=4130)
        st.number_input("QTDE_FACAS", value=45)
    with c5:
        st.number_input("MAX_SETUPS", value=10)
        st.number_input("META_IN FULL", value=1.05)

st.markdown("---")

# 4. Bloco do Meio: Regras de Negócio
st.subheader("REGRAS DE NEGÓCIO (Pesos e Penalidades)")
col_r1, col_r2 = st.columns(2)

with col_r1:
    st.slider("FATOR_LU_MINIMA", min_value=0, max_value=15000, value=10000, step=100)
    st.slider("CUSTO_POR_TIRADA", min_value=0, max_value=15000, value=8000, step=100)
    st.slider("CUSTO_ESTOQUE_PARADO", min_value=0, max_value=15000, value=3000, step=100)

with col_r2:
    st.slider("PREMIO_AVANCO", min_value=0, max_value=15000, value=5000, step=100)
    st.slider("CUSTO_TROCA_FACA", min_value=0, max_value=15000, value=2000, step=100)
    st.slider("CUSTO_FALTA_PEDIDO", min_value=0, max_value=15000, value=15000, step=100)

st.markdown("---")

# 5. Bloco Inferior: Demandas de Venda
st.subheader("DADOS DO PEDIDO")

# Cria uma tabela inicial com dados de exemplo
if 'df_demandas' not in st.session_state:
    st.session_state.df_demandas = pd.DataFrame(
        [
            {"Largura (MM)": 235, "Arruela (MM)": 7, "QUANTIDADE (KG)": 6000},
            {"Largura (MM)": 270, "Arruela (MM)": 7, "QUANTIDADE (KG)": 10000},
            {"Largura (MM)": 400, "Arruela (MM)": 7, "QUANTIDADE (KG)": 8500}
        ]
    )

# Renderiza a tabela editável na tela
st.data_editor(st.session_state.df_demandas, num_rows="dynamic", use_container_width=True)

# 6. Botão de Processar
st.markdown("<br>", unsafe_allow_html=True)
if st.button("🚀 GERAR SIMULAÇÃO", type="primary", use_container_width=True):
    st.info("Sucesso! O botão funciona. Na próxima fase vamos conectar o motor matemático aqui!")
