import streamlit as st

st.title("SIMULADOR - conjugação de esquemas de Corte")

import streamlit as st
import pandas as pd

# 1. Configuração da página
st.set_page_config(page_title="MAGNERA - Otimizador", layout="wide")

# ==========================================
# INJEÇÃO DE ESTILO WEB (MAGNERA.COM)
# ==========================================
st.markdown("""
<style>
    /* Título principal em Indigo super escuro e forte */
    h1 {
        color: #110b4f !important; 
        font-weight: 800 !important;
    }
    
    /* Subtítulos em Lilac corporativo (conforme Brand Guidelines) */
    h2, h3 {
        color: #984cfc !important; 
        font-weight: 700 !important;
    }
    
    /* Botão de Ação (CTA) idêntico aos botões web da Magnera (Ruby) */
    .stButton>button {
        background-color: #ed1b52 !important;
        color: #ffffff !important;
        font-weight: bold;
        border-radius: 30px; /* Deixa o botão mais arredondado e elegante */
        border: none;
        padding: 10px 24px;
        transition: all 0.3s ease; /* Efeito de transição suave */
    }
    
    /* Efeito ao passar o mouse sobre o botão (Hover) */
    .stButton>button:hover {
        background-color: #c91443 !important; /* Ruby levemente mais escuro */
        box-shadow: 0 4px 12px rgba(237, 27, 82, 0.4); /* Sombra Ruby */
    }
    
    /* Suaviza as bordas das caixas de texto e tabelas para um look moderno */
    div[data-baseweb="select"] > div, input[type="number"] {
        border-radius: 6px !important;
        border-color: #ced4da !important; /* Cor Gray 2 do manual */
    }
</style>
""", unsafe_allow_html=True)

# ==========================================

# 2. Cabeçalho
st.title("MAGNERA")
st.caption("NONWOVEN OPTIMIZATION ENGINE")
st.markdown("---")

# 3. Bloco Superior: Especificações e Restrições
col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("ESPECIFICAÇÕES DO MATERIAL")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.selectbox("MÁQUINA", ["SJP07", "SJP08"])
        st.selectbox("CALANDRA", ["OVAL", "DIAMANTE"])
    with c2:
        st.selectbox("TECNOLOGIA", ["SMS", "SSMMS"])
        st.number_input("GRAMATURA (GSM)", value=11)
    with c3:
        st.selectbox("SURFACTANTE", ["HFO", "ZEB"])
        st.number_input("METRAGEM LINEAR (M)", value=13500)

with col_dir:
    st.subheader("RESTRIÇÕES DE CORTE")
    c4, c5 = st.columns(2)
    with c4:
        st.number_input("LARGURA MASTER (MM)", value=4130)
        st.number_input("QTDE_FACAS", value=45)
    with c5:
        st.number_input("MAX_SETUPS", value=10)
        st.number_input("META_OTIF", value=1.05)

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
    st.slider("CUSTO_FALTA_PEDIDO", min_value=0, max_value=20000, value=15000, step=100)

st.markdown("---")

# 5. Bloco Inferior: Demandas de Venda
st.subheader("DEMANDAS DE VENDA")

if 'df_demandas' not in st.session_state:
    st.session_state.df_demandas = pd.DataFrame(
        [
            {"Largura Líquida (MM)": 235, "Arruela (MM)": 7, "Peso Desejado (KG)": 6000},
            {"Largura Líquida (MM)": 270, "Arruela (MM)": 7, "Peso Desejado (KG)": 10000},
            {"Largura Líquida (MM)": 400, "Arruela (MM)": 7, "Peso Desejado (KG)": 8500}
        ]
    )

st.data_editor(st.session_state.df_demandas, num_rows="dynamic", use_container_width=True)

# 6. Botão de Processar
st.markdown("<br>", unsafe_allow_html=True)
if st.button("🚀 PROCESSAR OTIMIZAÇÃO", type="primary", use_container_width=True):
    st.info("Sucesso! O botão funciona. Na próxima fase vamos conectar o motor matemático aqui!")
