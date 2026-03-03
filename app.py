import streamlit as st
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

# 2. Cabeçalho com Logo (Ordem Invertida)
# 1º: A Logo no topo
col_logo, col_vazia = st.columns([1, 2]) 
with col_logo:
    st.image("logo.png", width=380)

# 2º: O Título Principal
st.markdown("<h1>SIMULADOR</h1>", unsafe_allow_html=True)

# 3º: O Subtítulo
st.markdown("<h4 style='color: #984cfc; font-weight: normal; margin-top: -10px;'> CONJUGAÇÃO DE ESQUEMAS DE CORTE</h4>", unsafe_allow_html=True)
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
