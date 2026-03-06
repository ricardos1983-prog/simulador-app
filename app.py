import streamlit as st
import pandas as pd
import numpy as np
import math
import itertools
import re
import time

try:
    from ortools.linear_solver import pywraplp
    ORTOOLS_OK = True
except ImportError:
    ORTOOLS_OK = False

st.set_page_config(page_title="MAGNERA – Otimizador de Corte", page_icon="⚙️", layout="wide")

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700;900&family=JetBrains+Mono:wght@400;700&display=swap');

:root {
    --mg-accent: #8b5cf6;
    --mg-accent-2: #ec4899;
    --mg-success: #10b981;
    --mg-warning: #f59e0b;
    --mg-danger: #ef4444;
    --mg-info: #3b82f6;
    --mg-radius: 14px;
}

html, body, .stApp {
    font-family: 'Space Grotesk', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background-color: var(--background-color);
}

[data-testid="stSidebar"] {
    background-color: var(--secondary-background-color);
}

[data-testid="stHeader"] {
    background: transparent !important;
}

.block-container {
    padding-top: 1rem;
    max-width: 1450px;
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 900;
}

/* HEADER */

.magnera-header {
    background:
        linear-gradient(
            135deg,
            color-mix(in srgb, var(--secondary-background-color) 92%, var(--mg-accent) 8%) 0%,
            color-mix(in srgb, var(--background-color) 96%, #020617 4%) 100%
        );
    border: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
    border-radius: 18px;
    padding: 20px 28px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
}

/* SEÇÕES */

.section-title {
    font-size: 11px;
    font-weight: 900;
    color: var(--mg-accent);
    text-transform: uppercase;
    letter-spacing: 2px;
    border-left: 4px solid var(--mg-accent);
    padding-left: 10px;
    margin-bottom: 16px;
    display: block;
}

.orange-divider {
    height: 2px;
    background: linear-gradient(90deg, var(--mg-accent), transparent);
    border-radius: 99px;
    margin: 24px 0;
}

.param-box {
    background: var(--secondary-background-color);
    border: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.04);
}

.param-box-title {
    font-size: 9px;
    font-weight: 900;
    color: var(--mg-accent);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 12px;
}

/* KPIs */

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin: 20px 0;
}

.kpi-card {
    background: var(--secondary-background-color);
    border: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
    border-radius: var(--mg-radius);
    padding: 18px;
    border-top: 3px solid;
    box-shadow: 0 8px 24px rgba(0,0,0,0.05);
}

.kpi-label {
    font-size: 9px;
    font-weight: 900;
    color: color-mix(in srgb, var(--text-color) 50%, transparent);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 8px;
}

.kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 26px;
    font-weight: 700;
    line-height: 1;
}

.kpi-desc {
    font-size: 9px;
    color: color-mix(in srgb, var(--text-color) 38%, transparent);
    margin-top: 6px;
    font-style: italic;
}

/* CARDS */

.section-card,
.combo-card {
    background: var(--secondary-background-color);
    border: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
    border-radius: var(--mg-radius);
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.04);
}

.combo-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
}

.combo-id {
    background: color-mix(in srgb, var(--secondary-background-color) 75%, var(--background-color) 25%);
    border: 1px solid color-mix(in srgb, var(--text-color) 12%, transparent);
    border-radius: 50%;
    width: 28px;
    height: 28px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 900;
    color: color-mix(in srgb, var(--text-color) 60%, transparent);
}

/* BADGES */

.waste-badge-red {
    background: #7f1d1d22;
    border: 1px solid #ef444433;
    color: var(--mg-danger);
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 900;
}

.waste-badge-orange {
    background: #1a0e0022;
    border: 1px solid #f59e0b44;
    color: var(--mg-warning);
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 900;
}

.waste-badge-green {
    background: #05150e22;
    border: 1px solid #10b98133;
    color: var(--mg-success);
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 900;
}

.slu-neg-badge {
    background: #1a0e0022;
    border: 1px solid #f59e0b44;
    color: var(--mg-warning);
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 900;
}

.otif-green {
    background: #05150e;
    color: var(--mg-success);
    border: 1px solid #10b98122;
    padding: 2px 8px;
    border-radius: 5px;
    font-size: 10px;
    font-weight: 900;
}

.otif-orange {
    background: #1a0e00;
    color: var(--mg-warning);
    border: 1px solid #f59e0b22;
    padding: 2px 8px;
    border-radius: 5px;
    font-size: 10px;
    font-weight: 900;
}

.otif-red {
    background: #1a0000;
    color: var(--mg-danger);
    border: 1px solid #ef444422;
    padding: 2px 8px;
    border-radius: 5px;
    font-size: 10px;
    font-weight: 900;
}

/* MAPA DE CORTE */

.cut-map {
    display: flex;
    height: 56px;
    background: color-mix(in srgb, var(--secondary-background-color) 76%, var(--background-color) 24%);
    border: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
    border-radius: 10px;
    overflow: hidden;
    padding: 4px;
    gap: 3px;
    margin-bottom: 14px;
}

.cut-segment {
    background: rgba(124,58,237,0.12);
    border: 1px solid rgba(124,58,237,0.25);
    border-radius: 7px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-width: 20px;
}

.cut-segment-waste {
    background: rgba(239,68,68,0.08);
    border: 1px dashed rgba(239,68,68,0.20);
    border-radius: 7px;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 10px;
}

.cut-label {
    font-size: 10px;
    font-weight: 900;
    color: var(--mg-accent);
}

.cut-count {
    font-size: 8px;
    color: color-mix(in srgb, var(--mg-accent) 60%, transparent);
    margin-top: 2px;
}

.cut-waste-label {
    font-size: 9px;
    color: color-mix(in srgb, var(--mg-danger) 55%, transparent);
    writing-mode: vertical-rl;
}

/* PROGRESS */

.progress-wrap {
    margin-bottom: 14px;
}

.progress-label {
    display: flex;
    justify-content: space-between;
    font-size: 9px;
    font-weight: 900;
    color: color-mix(in srgb, var(--text-color) 50%, transparent);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
}

.progress-track {
    height: 6px;
    background: color-mix(in srgb, var(--secondary-background-color) 70%, var(--background-color) 30%);
    border-radius: 99px;
    border: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, var(--mg-danger), var(--mg-accent));
}

/* MINI MÉTRICAS */

.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}

.metric-mini {
    background: color-mix(in srgb, var(--secondary-background-color) 76%, var(--background-color) 24%);
    border: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
    border-radius: 10px;
    padding: 12px;
}

.metric-mini-label {
    font-size: 8px;
    font-weight: 900;
    color: color-mix(in srgb, var(--text-color) 40%, transparent);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
}

.metric-mini-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 18px;
    font-weight: 700;
}

/* ALERTAS */

.warn-box {
    background: #1a0e00;
    border: 1px solid #f59e0b44;
    border-left: 4px solid var(--mg-warning);
    border-radius: 10px;
    padding: 16px 20px;
    margin: 16px 0;
}

.info-box {
    background: color-mix(in srgb, var(--secondary-background-color) 75%, var(--background-color) 25%);
    border: 1px solid #3b82f644;
    border-left: 4px solid var(--mg-info);
    border-radius: 10px;
    padding: 14px 18px;
    margin: 12px 0;
    font-size: 12px;
    color: color-mix(in srgb, var(--text-color) 70%, transparent);
}

/* MATRIZES */

.matrix-ok {
    background: #052010;
    border: 1px solid #10b98155;
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 11px;
    color: var(--mg-success);
    font-weight: 700;
    margin-bottom: 8px;
}

.matrix-none {
    background: color-mix(in srgb, var(--secondary-background-color) 76%, var(--background-color) 24%);
    border: 1px dashed color-mix(in srgb, var(--text-color) 14%, transparent);
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 11px;
    color: color-mix(in srgb, var(--text-color) 38%, transparent);
    font-weight: 700;
    margin-bottom: 8px;
}

/* BOTÕES */

.stButton > button {
    background: linear-gradient(135deg, var(--mg-accent-2), var(--mg-accent)) !important;
    color: white !important;
    font-weight: 900 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    font-size: 12px !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 32px !important;
    box-shadow: 0 0 20px rgba(139,92,246,0.28) !important;
}

.stButton > button:hover {
    transform: scale(1.02) !important;
    box-shadow: 0 0 28px rgba(139,92,246,0.38) !important;
}

/* INPUTS */

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    background-color: var(--secondary-background-color);
    border: 1px solid color-mix(in srgb, var(--text-color) 12%, transparent);
    border-radius: 8px;
}

input, textarea, select {
    color: var(--text-color) !important;
    background-color: transparent !important;
}

[data-baseweb="select"] input,
[data-testid="stSelectbox"] input {
    caret-color: transparent !important;
    cursor: default !important;
}

.stNumberInput button {
    background-color: transparent;
}

/* TABELAS */

table {
    width: 100%;
    border-collapse: collapse;
    background: var(--secondary-background-color);
    color: var(--text-color);
    border: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
    border-radius: 12px;
    overflow: hidden;
}

th, td {
    padding: 10px 12px;
    border-bottom: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
    text-align: center;
    font-size: 12px;
}

th {
    background: color-mix(in srgb, var(--secondary-background-color) 76%, var(--background-color) 24%);
    color: color-mix(in srgb, var(--text-color) 65%, transparent);
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: 10px;
}

tr:hover {
    background: color-mix(in srgb, var(--secondary-background-color) 82%, var(--background-color) 18%);
}

/* RESPONSIVO */

@media (max-width: 1100px) {
    .kpi-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    .metric-row {
        grid-template-columns: repeat(2, 1fr);
    }
}

</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)

def safe_num(val, fallback=0):
    try:
        n = float(val)
        return fallback if math.isnan(n) else n
    except Exception:
        return fallback


K_VOLUME_EXTRUSAO = 1_250_000


def run_optimization(df_config, df_pedidos_raw, df_lu, df_arr):
    config = dict(zip(df_config.iloc[:, 0].astype(str).str.strip(), df_config.iloc[:, 1]))

    G = float(config["Gramatura_GSM"])
    METRAGEM = float(config["Metragem_mL"])
    MAX_FACAS = int(config["Qtde_facas"])
    DIFF_LIMIT = float(config.get("Limitação_dif_larg", 30))
    OTIF_MAX = float(config.get("Meta_OTIF", 1.01))
    FOLGA = abs(OTIF_MAX - 1.0)
    MAX_SETUPS = int(config.get("Max_Setups", 10))
    MAX_LARG_ESQUEMA = int(config.get("Max_Larguras_Esquema", 2))
    L_MIN_FATOR = float(config.get("Fator_LU_Minima", 0.9))
    L1_TIRADAS = float(config.get("Custo_por_Tirada", config.get("Lambda_Tiradas", 50)))
    L2_SETUPS = float(config.get("Custo_Troca_Faca", config.get("Lambda_Setups", 8000)))
    L3_OVER = float(config.get("Custo_Estoque_Parado", config.get("Lambda_Excesso", 5)))
    PREMIO_AVANCO = float(config.get("Bonus_Engenharia", config.get("Premio_Avanco", 15)))
    CUSTO_FALTA = float(config.get("Custo_Falta_Pedido", 50.0))
    SETUP_MIN_PCT = float(config.get("Setup_Min_Eixo_Pct", 0.0))
    TOL_VAL = float(config.get("Tolerancia_LU", -0.30))

    M = str(config["Maquina"]).strip()
    T = str(config["Tecnologia"]).strip()
    S = str(config["Surfactante"]).strip()
    C = str(config["Calandra"]).strip()
    IS_ZEB = (S.upper() == "ZEB")

    col_larg = col_val = None
    for col in df_pedidos_raw.columns:
        nc = str(col).lower()
        if "largura" in nc:
            col_larg = col
        elif any(x in nc for x in ["valor", "peso", "pedido", "demanda", "kg"]):
            col_val = col
    if not col_larg:
        col_larg = df_pedidos_raw.columns[0]
    if not col_val:
        col_val = df_pedidos_raw.columns[1]

    df_ped = df_pedidos_raw[[col_larg, col_val]].copy()
    df_ped.columns = ["Largura_mm", "Valor_Kg"]
    df_ped["Largura_mm"] = pd.to_numeric(df_ped["Largura_mm"], errors="coerce")
    df_ped["Valor_Kg"] = pd.to_numeric(df_ped["Valor_Kg"], errors="coerce")
    df_ped = df_ped.dropna()
    if df_ped.empty:
        return None, "Aba 'Pedidos' não contém dados válidos."

    chave_lu = f"{M}{T}{S}{C}"
    gsm_col = None
    for col in df_lu.columns:
        try:
            if math.isclose(float(str(col).replace(",", ".")), float(G)):
                gsm_col = col
                break
        except ValueError:
            if re.search(rf"\b{int(G)}\b", str(col)):
                gsm_col = col
                break
    if gsm_col is None:
        return None, f"Gramatura {G} não encontrada na Matriz_LU."
    try:
        LU_NOMINAL = float(
            df_lu[df_lu.iloc[:, 0].astype(str).str.strip().str.upper() == chave_lu.upper()][gsm_col].values[0]
        )
    except Exception:
        return None, f"Chave de máquina não encontrada: {chave_lu}"

    LU_MAX = LU_NOMINAL * (1 + abs(TOL_VAL) / 100)

    col_kerf_idx = 1
    for i, cn in enumerate(df_arr.columns):
        if any(w in str(cn).lower() for w in ["arruela", "kerf", "valor", "mm"]):
            col_kerf_idx = i
            break

    dicionario_kerfs = {}

    def auditoria_kerf(largura):
        try:
            chave_k = f"{M}{T}{S}{C}{int(float(largura))}{int(G)}".upper()
            chaves = df_arr.iloc[:, 0].astype(str).str.strip().str.upper()
            res = df_arr[chaves == chave_k]
            if not res.empty:
                val_raw = str(res.iloc[:, col_kerf_idx].values[0])
                val_clean = re.sub(r"[^\d.]", "", val_raw.replace(",", "."))
                v = float(val_clean) if val_clean else 0.0
                dicionario_kerfs[largura] = v
                return v
        except Exception:
            pass
        dicionario_kerfs[largura] = 0.0
        return 0.0

    larguras = df_ped["Largura_mm"].tolist()
    larguras_efetivas = [l + auditoria_kerf(l) for l in larguras]
    demandas_rolos = [
        max(1, int(round(v / ((l * METRAGEM * G) / 1e6)))) for l, v in zip(larguras, df_ped["Valor_Kg"])
    ]

    MAX_METROS_TEORICO = K_VOLUME_EXTRUSAO / G
    RUNS_MAX_POR_RJ = max(1, math.floor(MAX_METROS_TEORICO / METRAGEM))
    min_runs_raw = RUNS_MAX_POR_RJ * (SETUP_MIN_PCT / 100.0)
    MIN_RUNS_SETUP = max(1, int(math.floor(min_runs_raw + 0.5)))

    def minerar_pool():
        pool = []
        L_MIN_BRUTA = LU_NOMINAL * L_MIN_FATOR

        def varredura(idx, qtd, l_acum, vetor):
            if idx == len(larguras):
                if L_MIN_BRUTA <= l_acum <= LU_MAX:
                    pool.append({"vetor": list(vetor), "l_real": l_acum})
                return
            max_q = min(MAX_FACAS - qtd, int((LU_MAX - l_acum) // larguras_efetivas[idx]))
            for q in range(max_q + 1):
                vetor[idx] = q
                varredura(idx + 1, qtd + q, l_acum + q * larguras_efetivas[idx], vetor)
                vetor[idx] = 0

        varredura(0, 0, 0.0, [0] * len(larguras))
        final_pool = []
        for p in pool:
            usadas = [larguras[i] for i in range(len(larguras)) if p["vetor"][i] > 0]
            if not (0 < len(usadas) <= MAX_LARG_ESQUEMA):
                continue
            if len(usadas) > 1 and any(round(abs(w1 - w2), 1) < DIFF_LIMIT for w1, w2 in itertools.combinations(usadas, 2)):
                continue
            p["slu"] = ((LU_NOMINAL - p["l_real"]) / LU_NOMINAL) * 100
            p["tipo"] = "Mono" if len(usadas) == 1 else "Duo" if len(usadas) == 2 else "Trio"
            final_pool.append(p)
        return final_pool

    pool_detalhado = minerar_pool()
    if not pool_detalhado:
        return None, "Pool vazio. Nenhum esquema válido encontrado. Verifique Fator_LU_Minima ou larguras."

    if not ORTOOLS_OK:
        return None, "OR-Tools não instalado. Execute: pip install ortools"

    solver = pywraplp.Solver.CreateSolver("SCIP")
    if solver is None:
        return None, "Solver SCIP indisponível."

    NJ = len(pool_detalhado)
    NI = len(larguras)
    x = [solver.IntVar(0, 10000, f"x_{j}") for j in range(NJ)]
    y = [solver.IntVar(0, 1, f"y_{j}") for j in range(NJ)]
    underfill = [solver.IntVar(0, 100000, f"under_{i}") for i in range(NI)]

    for i in range(NI):
        prod = sum(pool_detalhado[j]["vetor"][i] * x[j] for j in range(NJ))
        solver.Add(prod + underfill[i] >= demandas_rolos[i])
        solver.Add(prod <= math.ceil(demandas_rolos[i] * OTIF_MAX))
        solver.Add(underfill[i] <= math.ceil(demandas_rolos[i] * FOLGA))
    for j in range(NJ):
        solver.Add(x[j] <= 10000 * y[j])
        solver.Add(x[j] >= y[j] * MIN_RUNS_SETUP)
    solver.Add(sum(y) <= MAX_SETUPS)

    total_prod_kg_runs = sum(x[j] * ((pool_detalhado[j]["l_real"] * METRAGEM * G) / 1e6) for j in range(NJ))
    peso_dem_rolos = sum(demandas_rolos[i] * ((larguras[i] * METRAGEM * G) / 1e6) for i in range(NI))
    excesso_kg = total_prod_kg_runs - peso_dem_rolos
    custos_final = [
        (LU_NOMINAL - p["l_real"]) * PREMIO_AVANCO if (LU_NOMINAL - p["l_real"]) < 0 else (LU_NOMINAL - p["l_real"]) * 10
        for p in pool_detalhado
    ]
    peso_falta_kg = sum(underfill[i] * ((larguras[i] * METRAGEM * G) / 1e6) for i in range(NI))
    solver.Minimize(
        sum(x[j] * custos_final[j] for j in range(NJ))
        + sum(x) * L1_TIRADAS
        + sum(y) * L2_SETUPS
        + excesso_kg * L3_OVER
        + peso_falta_kg * CUSTO_FALTA
    )
    solver.SetTimeLimit(30_000)
    status = solver.Solve()

    if status not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        diag = []
        L_MIN_BRUTA = LU_NOMINAL * L_MIN_FATOR
        diag.append(f"Pool de esquemas: {len(pool_detalhado)} válidos (L_MIN={L_MIN_BRUTA:.1f}mm, LU_MAX={LU_MAX:.1f}mm)")
        for i, larg in enumerate(larguras):
            esq = sum(1 for p in pool_detalhado if p["vetor"][i] > 0)
            diag.append(f"  • {int(larg)}mm → demanda={demandas_rolos[i]} rolos, esquemas disponíveis={esq}")
        diag.append(f"MAX_SETUPS={MAX_SETUPS} | MIN_RUNS_SETUP={MIN_RUNS_SETUP} | SETUP_MIN_PCT={SETUP_MIN_PCT}%")
        return None, "Solver inviável. Auto-diagnóstico:\n" + "\n".join(diag)

    plano = []
    prod_rolos = [0] * NI
    t_runs = t_kg_lreal = t_kg_extrusado = t_kg_slu = 0
    kpi_rjs_cheios = kpi_rjs_parciais = 0
    tem_slu_negativo = False

    for j in range(NJ):
        runs = int(round(x[j].solution_value()))
        if runs <= 0:
            continue
        p = pool_detalhado[j]

        p_kg_lreal = (p["l_real"] * METRAGEM * G * runs) / 1e6
        l_ext = max(LU_NOMINAL, p["l_real"])
        kg_ext_setup = (l_ext * METRAGEM * G * runs) / 1e6
        kg_slu_setup = kg_ext_setup - p_kg_lreal

        t_kg_extrusado += kg_ext_setup
        t_kg_slu += kg_slu_setup
        t_runs += runs
        t_kg_lreal += p_kg_lreal

        jumbos_cheios = runs // RUNS_MAX_POR_RJ
        runs_resto = runs % RUNS_MAX_POR_RJ

        if IS_ZEB:
            kpi_rjs_cheios += jumbos_cheios
            kpi_rjs_parciais += 1 if runs_resto > 0 else 0

        if p["slu"] < -0.001:
            tem_slu_negativo = True

        widths_in = [larguras[i] for i in range(NI) if p["vetor"][i] > 0]
        cnts_in = [p["vetor"][i] for i in range(NI) if p["vetor"][i] > 0]
        kerfs_in = [dicionario_kerfs.get(larguras[i], 0) for i in range(NI) if p["vetor"][i] > 0]

        plano.append(
            {
                "id": str(len(plano) + 1),
                "tipo": p["tipo"],
                "widths": widths_in,
                "rollCounts": cnts_in,
                "kerfs": kerfs_in,
                "l_real": p["l_real"],
                "slu": p["slu"],
                "runs": runs,
                "kg_lreal": p_kg_lreal,
                "kg_extrusado": kg_ext_setup,
                "kg_slu": kg_slu_setup,
                "jumbos_cheios": jumbos_cheios,
                "runs_resto": runs_resto,
            }
        )
        for i in range(NI):
            prod_rolos[i] += p["vetor"][i] * runs

    if not IS_ZEB:
        kpi_rjs_cheios = t_runs // RUNS_MAX_POR_RJ
        kpi_rjs_parciais = 1 if (t_runs % RUNS_MAX_POR_RJ) > 0 else 0

    balanco = []
    t_kg_vend = t_un_dem = t_un_prod = t_kg_prod_liq = t_kg_sobra = 0
    t_kg_estoque = t_kg_falta = 0
    for i, larg in enumerate(larguras):
        p_d_kg = (larg * METRAGEM * G * demandas_rolos[i]) / 1e6
        p_p_kg = (larg * METRAGEM * G * prod_rolos[i]) / 1e6
        sobra = p_p_kg - p_d_kg
        infull = (prod_rolos[i] / demandas_rolos[i] * 100) if demandas_rolos[i] > 0 else 0
        t_kg_vend += p_d_kg
        t_un_dem += demandas_rolos[i]
        t_un_prod += prod_rolos[i]
        t_kg_prod_liq += p_p_kg
        t_kg_sobra += sobra
        if sobra > 0:
            t_kg_estoque += sobra
        elif sobra < 0:
            t_kg_falta += abs(sobra)
        balanco.append(
            {
                "largura": larg,
                "kerf": dicionario_kerfs.get(larg, 0),
                "dem_rolos": demandas_rolos[i],
                "prod_rolos": prod_rolos[i],
                "infull": infull,
                "kg_dem": p_d_kg,
                "kg_prod": p_p_kg,
                "sobra_kg": sobra,
            }
        )

    t_kg_kerf = t_kg_lreal - t_kg_prod_liq
    slu_final_pct = (t_kg_slu / t_kg_extrusado * 100) if t_kg_extrusado > 0 else 0
    total_infull = (t_un_prod / t_un_dem * 100) if t_un_dem > 0 else 0

    return {
        "M": M,
        "T": T,
        "S": S,
        "C": C,
        "IS_ZEB": IS_ZEB,
        "G": G,
        "METRAGEM": METRAGEM,
        "LU_NOMINAL": LU_NOMINAL,
        "LU_MAX": LU_MAX,
        "OTIF_MAX": OTIF_MAX,
        "SETUP_MIN_PCT": SETUP_MIN_PCT,
        "MIN_RUNS_SETUP": MIN_RUNS_SETUP,
        "RUNS_MAX_POR_RJ": RUNS_MAX_POR_RJ,
        "MAX_SETUPS": MAX_SETUPS,
        "L1_TIRADAS": L1_TIRADAS,
        "L2_SETUPS": L2_SETUPS,
        "L3_OVER": L3_OVER,
        "CUSTO_FALTA": CUSTO_FALTA,
        "pool_size": len(pool_detalhado),
        "plano": plano,
        "balanco": balanco,
        "t_runs": t_runs,
        "kpi_rjs_cheios": kpi_rjs_cheios,
        "kpi_rjs_parciais": kpi_rjs_parciais,
        "kpi_rjs_total": kpi_rjs_cheios + kpi_rjs_parciais,
        "t_kg_extrusado": t_kg_extrusado,
        "t_kg_prod_liq": t_kg_prod_liq,
        "t_kg_kerf": t_kg_kerf,
        "t_kg_slu": t_kg_slu,
        "slu_final_pct": slu_final_pct,
        "t_kg_vend": t_kg_vend,
        "t_kg_estoque": t_kg_estoque,
        "t_kg_falta": t_kg_falta,
        "total_infull": total_infull,
        "tem_slu_negativo": tem_slu_negativo,
    }, None


_defaults = {
    "df_lu": None,
    "df_arr": None,
    "result": None,
    "simulated": False,
    "orders": [
        {"id": "1", "largura": 235, "kg": 6000.0},
        {"id": "2", "largura": 270, "kg": 10000.0},
        {"id": "3", "largura": 400, "kg": 8500.0},
    ],
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# Mantenha aqui o mesmo _LOGO original do seu arquivo.
_LOGO = "COLE_AQUI_O_MESMO_BASE64_ORIGINAL_DO_SEU_ARQUIVO"

st.markdown(
    f'<div class="magnera-header">'
    f'<img src="data:image/png;base64,{_LOGO}" style="height:48px;object-fit:contain;" />'
    f'<div style="margin-left:auto;display:flex;align-items:center;gap:8px;">'
    f'<span style="width:8px;height:8px;background:#10b981;border-radius:50%;display:inline-block;"></span>'
    f'<span style="font-size:10px;color:#10b981;font-weight:900;text-transform:uppercase;">Online</span>'
    f'</div></div>',
    unsafe_allow_html=True,
)

import io as _io
import os as _os
import hashlib as _hashlib

_CACHE_DIR = _os.path.join(_os.path.expanduser("~"), ".magnera_cache")
_os.makedirs(_CACHE_DIR, exist_ok=True)


def _cache_path(key):
    return _os.path.join(_CACHE_DIR, f"{key}.parquet")


def _hash_bytes(b):
    return _hashlib.md5(b).hexdigest()


def _save_cache(key, df):
    try:
        df.to_parquet(_cache_path(key), index=False)
    except Exception:
        pass


def _load_cache(key):
    p = _cache_path(key)
    if _os.path.exists(p):
        try:
            return pd.read_parquet(p)
        except Exception:
            pass
    return None


def _read_any_excel(raw_bytes, filename, sheet_hint=None):
    _h = _hash_bytes(raw_bytes)
    _ck = f"{sheet_hint or 'sheet0'}_{_h}"
    _cached = _load_cache(_ck)
    if _cached is not None:
        return _cached

    buf = _io.BytesIO(raw_bytes)
    magic = raw_bytes[:4]
    is_xlsb = (magic == b'\xd0\xcf\x11\xe0') or filename.lower().endswith('.xlsb')

    if is_xlsb:
        try:
            import pyxlsb  # noqa: F401
        except ImportError:
            raise ImportError("pyxlsb não instalado. Adicione 'pyxlsb' ao requirements.txt.")
        if sheet_hint:
            try:
                df = pd.read_excel(buf, sheet_name=sheet_hint, engine='pyxlsb')
                _save_cache(_ck, df)
                return df
            except Exception:
                buf = _io.BytesIO(raw_bytes)
        df = pd.read_excel(buf, sheet_name=0, engine='pyxlsb')
    else:
        if sheet_hint:
            try:
                df = pd.read_excel(buf, sheet_name=sheet_hint)
                _save_cache(_ck, df)
                return df
            except Exception:
                buf = _io.BytesIO(raw_bytes)
        df = pd.read_excel(buf, sheet_name=0)

    _save_cache(_ck, df)
    return df


if st.session_state.df_lu is None:
    _df_cached = _load_cache("df_lu_active")
    if _df_cached is not None:
        st.session_state.df_lu = _df_cached

if st.session_state.df_arr is None:
    _df_cached = _load_cache("df_arr_active")
    if _df_cached is not None:
        st.session_state.df_arr = _df_cached

st.markdown(
    """
<style>
[data-testid="stFileUploaderDropzoneInstructions"] small { display: none !important; }
</style>
""",
    unsafe_allow_html=True,
)

_lu_ok = st.session_state.df_lu is not None
_arr_ok = st.session_state.df_arr is not None

with st.expander(
    ("✅ Tabelas carregadas" if (_lu_ok and _arr_ok) else "⚠️  Matrizes de Referência — clique para carregar"),
    expanded=not (_lu_ok and _arr_ok),
):
    st.markdown(
        '<div class="info-box" style="margin-top:0">📁 Aceita <b>.xlsb</b> e <b>.xlsx</b>.</div>',
        unsafe_allow_html=True,
    )

    _uc1, _uc2 = st.columns(2)

    with _uc1:
        st.markdown('<div class="param-box-title">TABELA — Largura útil</div>', unsafe_allow_html=True)
        if _lu_ok:
            _df = st.session_state.df_lu
            st.markdown(
                f'<div class="matrix-ok">✅ Carregada — {len(_df)} linhas x {len(_df.columns)} colunas</div>',
                unsafe_allow_html=True,
            )
            with st.expander('Visualizar'):
                st.dataframe(_df.head(100), use_container_width=True)
                st.caption(f'Exibindo 100 de {len(_df)} linhas')
        else:
            st.markdown('<div class="matrix-none">Aguardando arquivo</div>', unsafe_allow_html=True)
        _f_lu = st.file_uploader('Largura Util (.xlsx ou .xlsb)', key='up_lu', label_visibility='collapsed')

    with _uc2:
        st.markdown('<div class="param-box-title">TABELA — Arruelas</div>', unsafe_allow_html=True)
        if _arr_ok:
            _df = st.session_state.df_arr
            st.markdown(
                f'<div class="matrix-ok">✅ Carregada — {len(_df)} linhas x {len(_df.columns)} colunas</div>',
                unsafe_allow_html=True,
            )
            with st.expander('Visualizar'):
                st.dataframe(_df.head(200), use_container_width=True)
                st.caption(f'Exibindo 200 de {len(_df)} linhas')
        else:
            st.markdown('<div class="matrix-none">Aguardando arquivo</div>', unsafe_allow_html=True)
        _f_arr = st.file_uploader('Arruelas (.xlsx ou .xlsb)', key='up_arr', label_visibility='collapsed')

if _f_lu is not None:
    _fname_lu = _f_lu.name
    if not any(_fname_lu.lower().endswith(e) for e in ('.xlsx', '.xlsb', '.xls', '.bin')):
        st.error(f'Formato nao suportado: {_fname_lu}')
    else:
        _raw_lu = _f_lu.read()
        _h_lu = _hash_bytes(_raw_lu)
        if st.session_state.get('_last_lu_hash') != _h_lu:
            with st.spinner('Lendo Matriz LU...'):
                try:
                    _df_new = _read_any_excel(_raw_lu, _fname_lu, sheet_hint='Matriz_LU')
                    st.session_state.df_lu = _df_new
                    st.session_state['_last_lu_hash'] = _h_lu
                    _save_cache('df_lu_active', _df_new)
                    st.rerun()
                except Exception as _e:
                    st.error(f'Erro ao ler Matriz LU: {_e}')

if _f_arr is not None:
    _fname_arr = _f_arr.name
    if not any(_fname_arr.lower().endswith(e) for e in ('.xlsx', '.xlsb', '.xls', '.bin')):
        st.error(f'Formato nao suportado: {_fname_arr}')
    else:
        _raw_arr = _f_arr.read()
        _h_arr = _hash_bytes(_raw_arr)
        if st.session_state.get('_last_arr_hash') != _h_arr:
            with st.spinner('Lendo Matriz Arruelas... (arquivo grande, aguarde)'):
                try:
                    _df_new = _read_any_excel(_raw_arr, _fname_arr, sheet_hint='Matriz_Arruelas')
                    st.session_state.df_arr = _df_new
                    st.session_state['_last_arr_hash'] = _h_arr
                    _save_cache('df_arr_active', _df_new)
                    st.rerun()
                except Exception as _e:
                    st.error(f'Erro ao ler Matriz Arruelas: {_e}')

_lu_ok = st.session_state.df_lu is not None
_arr_ok = st.session_state.df_arr is not None

st.markdown('<div class="orange-divider"></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Especificações do Material</div>', unsafe_allow_html=True)
st.markdown('<div class="param-box">', unsafe_allow_html=True)
st.markdown('<div class="param-box-title">Identificação da Máquina</div>', unsafe_allow_html=True)
_c1, _c2, _c3, _c4 = st.columns(4)
machine = _c1.selectbox('Máquina', ['PAL01', 'PAL02', 'SJP05', 'SJP06', 'SJP07', 'SJP08', 'SJP09'], key='machine')
technology = _c2.selectbox('Tecnologia', ['SMS', 'SSS'], key='technology')
surfactant = _c3.selectbox('Surfactante', ['HFO', 'HFL', 'ZEB'], key='surfactant')
calender = _c4.selectbox('Calandra', ['OVAL', 'ESTRELA'], key='calender')
st.markdown('</div>', unsafe_allow_html=True)

_cm1, _cm2 = st.columns(2)
with _cm1:
    st.markdown('<div class="param-box">', unsafe_allow_html=True)
    st.markdown('<div class="param-box-title">Material</div>', unsafe_allow_html=True)
    _mc1, _mc2 = st.columns(2)
    grammage = _mc1.number_input('Gramatura (g/m²)', value=10.0, step=0.5, format='%.1f', min_value=1.0)
    linear_meters = _mc2.number_input('Metragem (m)', value=10000, step=100, min_value=100)
    st.markdown('</div>', unsafe_allow_html=True)
with _cm2:
    st.markdown('<div class="param-box">', unsafe_allow_html=True)
    st.markdown('<div class="param-box-title">Largura Útil & Refile</div>', unsafe_allow_html=True)
    _tc1, _tc2 = st.columns(2)
    fator_lu_min = _tc1.number_input('%Utilização da LU', value=0.93, step=0.01, format='%.2f', min_value=0.5, max_value=1.0)
    tol_lu = _tc2.number_input('Avanço de Refile (%)', value=0.30, step=0.05, format='%.2f', min_value=0.0)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Restrições de Corte & Solver</div>', unsafe_allow_html=True)

_rc1, _rc2 = st.columns(2)
with _rc1:
    st.markdown('<div class="param-box">', unsafe_allow_html=True)
    st.markdown('<div class="param-box-title">Configuração Rebobinadeira</div>', unsafe_allow_html=True)
    _rr1, _rr2, _rr3 = st.columns(3)
    max_facas = _rr1.number_input('Qtde Facas', value=40, step=1, min_value=1)
    max_larg_esq = _rr2.number_input('Max Larguras/Esquema', value=2, step=1, min_value=1, max_value=5)
    diff_limit = _rr3.number_input('Dif. Mín. Larg. (mm)', value=30.0, step=5.0, min_value=0.0)
    st.markdown('</div>', unsafe_allow_html=True)

with _rc2:
    st.markdown('<div class="param-box">', unsafe_allow_html=True)
    st.markdown('<div class="param-box-title">In Full & Setups</div>', unsafe_allow_html=True)
    _rs1, _rs2, _rs3 = st.columns(3)
    meta_otif = _rs1.number_input('Meta In Full (%)', value=105.0, step=0.5, format='%.1f', min_value=100.0, max_value=115.0)
    max_setups = _rs2.number_input('Max Setups', value=10, step=1, min_value=1)
    setup_min_pct = _rs3.number_input('Ocup. Mín. Eixo (%)', value=70.0, step=1.0, format='%.1f', min_value=0.0)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="param-box">', unsafe_allow_html=True)
st.markdown('<div class="param-box-title">Custos & Penalidades</div>', unsafe_allow_html=True)
_cp1, _cp2, _cp3, _cp4, _cp5 = st.columns(5)
custo_tirada = _cp1.number_input('Custo Tirada', value=0.0, step=10.0)
custo_setup = _cp2.number_input('Custo Troca Faca', value=0.0, step=500.0)
custo_estoque = _cp3.number_input('Custo Excesso Estoque', value=0.0, step=1.0)
custo_falta = _cp4.number_input('Custo Falta Material', value=100.0, step=5.0)
bonus_eng = _cp5.number_input('Custo Avanço Refile', value=100.0, step=1.0)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="orange-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Diagnóstico de Regras de Negócio</div>', unsafe_allow_html=True)
_dstr_setup = 'BAIXA — Prioridade: Reduzir SLU' if custo_setup < 3000 else 'ALTA — Prioridade: Evitar paradas da rebobinadeira'
_dstr_estoque = 'FLEXÍVEL — Gera sobras para salvar SLU' if custo_estoque <= 5 else 'RÍGIDA — Evita sobras a todo custo'
_dstr_falta = 'PERMITIDA — Pode entregar a menos' if custo_falta <= 10 else 'PROIBIDA — Força In-Full de 100%'
_dpct_over = meta_otif - 100.0
_dzeb = surfactant == 'ZEB'
_dextrusao = f'ZEBRADO ({surfactant})' if _dzeb else f'HOMOGÊNEO ({surfactant})'
_diag_html = (
    '<div class="info-box">'
    f'<b>Máquina:</b> {machine} | {technology} | {surfactant} | {calender} &nbsp;|&nbsp;'
    f'<b>Fator LU Min:</b> {fator_lu_min:.2f} &nbsp;|&nbsp;'
    f'<b>Tolerância LU:</b> {tol_lu:.2f}%<br>'
    f'<b>Extrusão:</b> {_dextrusao} &nbsp;|&nbsp;'
    f'<b>Max Facas:</b> {max_facas} &nbsp;|&nbsp;'
    f'<b>Max Larg/Esquema:</b> {max_larg_esq} &nbsp;|&nbsp;'
    f'<b>Dif. Mín. Larg:</b> {diff_limit:.0f}mm<br>'
    f'<b>Meta In Full (%):</b> {meta_otif:.1f}% (tolerância overstock: {_dpct_over:.1f}%) &nbsp;|&nbsp;'
    f'<b>Max Setups:</b> {max_setups} &nbsp;|&nbsp;'
    f'<b>Ocup. Mín. Eixo:</b> {setup_min_pct:.1f}%<br>'
    f'<b>Troca Faca:</b> {_dstr_setup}<br>'
    f'<b>Estoque:</b> {_dstr_estoque}<br>'
    f'<b>Faltas:</b> {_dstr_falta}'
    '</div>'
)
st.markdown(_diag_html, unsafe_allow_html=True)
st.markdown('<div class="orange-divider"></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Demandas de Venda</div>', unsafe_allow_html=True)

_hc1, _hc2, _hc3 = st.columns([3, 3, 1])
_hc1.markdown('**Largura Líquida (mm)**')
_hc2.markdown('**Demanda (kg)**')

_to_delete = []
for _i, _order in enumerate(st.session_state.orders):
    _oc1, _oc2, _oc3 = st.columns([3, 3, 1])
    _new_larg = _oc1.number_input('', value=int(_order['largura']), step=1, min_value=1, key=f"larg_{_order['id']}", label_visibility='collapsed')
    _new_kg = _oc2.number_input('', value=float(_order['kg']), step=100.0, min_value=0.0, key=f"kg_{_order['id']}", label_visibility='collapsed')
    if _oc3.button('🗑', key=f"del_{_order['id']}"):
        _to_delete.append(_order['id'])
    st.session_state.orders[_i]['largura'] = _new_larg
    st.session_state.orders[_i]['kg'] = _new_kg

for _did in _to_delete:
    st.session_state.orders = [o for o in st.session_state.orders if o['id'] != _did]
    st.rerun()

if st.button('＋ Adicionar Largura'):
    _new_id = str(max((int(o['id']) for o in st.session_state.orders), default=0) + 1)
    st.session_state.orders.append({'id': _new_id, 'largura': 300, 'kg': 1000.0})
    st.rerun()

st.markdown('<div class="orange-divider"></div>', unsafe_allow_html=True)

_ready = (
    _lu_ok
    and _arr_ok
    and len(st.session_state.orders) > 0
    and all(o['largura'] > 0 and o['kg'] > 0 for o in st.session_state.orders)
)

if st.button('⚡  OTIMIZAR ESQUEMA DE CORTE', disabled=not _ready):
    _config_data = {
        'Maquina': machine,
        'Tecnologia': technology,
        'Surfactante': surfactant,
        'Calandra': calender,
        'Gramatura_GSM': grammage,
        'Metragem_mL': linear_meters,
        'Qtde_facas': max_facas,
        'Max_Larguras_Esquema': max_larg_esq,
        'Limitação_dif_larg': diff_limit,
        'Fator_LU_Minima': fator_lu_min,
        'Tolerancia_LU': -tol_lu,
        'Meta_OTIF': meta_otif / 100.0,
        'Max_Setups': max_setups,
        'Setup_Min_Eixo_Pct': setup_min_pct,
        'Custo_por_Tirada': custo_tirada,
        'Custo_Troca_Faca': custo_setup,
        'Custo_Estoque_Parado': custo_estoque,
        'Custo_Falta_Pedido': custo_falta,
        'Bonus_Engenharia': bonus_eng,
    }
    _df_cfg = pd.DataFrame(list(_config_data.items()), columns=['param', 'value'])
    _df_ped = pd.DataFrame([{'Largura_mm': o['largura'], 'Valor_Kg': o['kg']} for o in st.session_state.orders])
    with st.spinner('⏳ Minerando esquemas e resolvendo ILP com SCIP...'):
        _t0 = time.time()
        _result, _err = run_optimization(_df_cfg, _df_ped, st.session_state.df_lu, st.session_state.df_arr)
        _elapsed = time.time() - _t0
    if _err:
        st.error(_err)
    else:
        _result['elapsed'] = _elapsed
        st.session_state.result = _result
        st.session_state.simulated = True
elif not _ready and (_lu_ok and _arr_ok):
    st.info('Preencha todas as demandas para habilitar o otimizador.')


if st.session_state.simulated and st.session_state.result:
    r = st.session_state.result

    if r["tem_slu_negativo"]:
        st.markdown(
            """
        <div class="warn-box">
        ⚠️ <b>ATENÇÃO: PLANO COM SLU NEGATIVO (AVANÇO DE CALANDRA) IDENTIFICADO</b><br>
        <span style="font-size:12px;color:#94a3b8;">
        Requer validação e assinatura obrigatória da Engenharia de Processos antes da produção.
        </span>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="orange-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 KPI Final da Campanha</div>', unsafe_allow_html=True)

    slu_color = "#10b981" if r["slu_final_pct"] < 1.0 else ("#f59e0b" if r["slu_final_pct"] < 1.5 else "#ef4444")
    inf_color = "#10b981" if r["total_infull"] >= 98 else "#ef4444"
    ext_color = "#3b82f6"
    rj_color = "#7c3aed"
    est_color = "#f59e0b" if r["t_kg_estoque"] > 0 else "#10b981"
    falt_color = "#ef4444" if r["t_kg_falta"] > 0 else "#10b981"

    _k1 = (
        '<div class="kpi-grid">'
        f'<div class="kpi-card" style="border-top-color:{slu_color}">'
        '<div class="kpi-label">SLU Global</div>'
        f'<div class="kpi-value" style="color:{slu_color}">{r["slu_final_pct"]:.2f}%</div>'
        '<div class="kpi-desc">Perda lateral s/ extrusão</div></div>'
        f'<div class="kpi-card" style="border-top-color:{ext_color}">'
        '<div class="kpi-label">Massa Extrusada</div>'
        f'<div class="kpi-value" style="color:{ext_color}">{r["t_kg_extrusado"]:,.0f} kg</div>'
        f'<div class="kpi-desc">Líquida: {r["t_kg_prod_liq"]:,.0f} kg</div></div>'
        f'<div class="kpi-card" style="border-top-color:{rj_color}">'
        '<div class="kpi-label">Jumbos Físicos</div>'
        f'<div class="kpi-value" style="color:{rj_color}">{r["kpi_rjs_total"]}</div>'
        f'<div class="kpi-desc">{r["kpi_rjs_cheios"]} completos + {r["kpi_rjs_parciais"]} fração</div></div>'
        f'<div class="kpi-card" style="border-top-color:{inf_color}">'
        '<div class="kpi-label">In-Full Global</div>'
        f'<div class="kpi-value" style="color:{inf_color}">{r["total_infull"]:.1f}%</div>'
        f'<div class="kpi-desc">{r["t_runs"]} tiradas totais</div></div>'
        '</div>'
    )
    st.markdown(_k1, unsafe_allow_html=True)

    _k2 = (
        '<div class="kpi-grid">'
        '<div class="kpi-card" style="border-top-color:#64748b">'
        '<div class="kpi-label">Massa Pedida</div>'
        f'<div class="kpi-value" style="color:#94a3b8">{r["t_kg_vend"]:,.0f} kg</div>'
        '<div class="kpi-desc">Demanda total</div></div>'
        '<div class="kpi-card" style="border-top-color:#ef4444">'
        '<div class="kpi-label">Refugo Facas</div>'
        f'<div class="kpi-value" style="color:#ef4444">{r["t_kg_kerf"]:,.0f} kg</div>'
        '<div class="kpi-desc">Arruelas / Kerf</div></div>'
        f'<div class="kpi-card" style="border-top-color:{est_color}">'
        '<div class="kpi-label">Estoque Gerado</div>'
        f'<div class="kpi-value" style="color:{est_color}">{r["t_kg_estoque"]:,.0f} kg</div>'
        '<div class="kpi-desc">Sobra acima da demanda</div></div>'
        f'<div class="kpi-card" style="border-top-color:{falt_color}">'
        '<div class="kpi-label">Falta em Pedidos</div>'
        f'<div class="kpi-value" style="color:{falt_color}">{r["t_kg_falta"]:,.0f} kg</div>'
        '<div class="kpi-desc">Dívida com clientes</div></div>'
        '</div>'
    )
    st.markdown(_k2, unsafe_allow_html=True)

    st.markdown('<div class="orange-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Plano de Corte — Esquemas Ativos</div>', unsafe_allow_html=True)

    cols_combo = st.columns(2)
    for ci, setup in enumerate(r["plano"]):
        with cols_combo[ci % 2]:
            slu = setup["slu"]
            if slu < -0.001:
                badge = f'<span class="slu-neg-badge">SLU {slu:.2f}% ⚠️ Avanço</span>'
            elif slu > 1.3:
                badge = f'<span class="waste-badge-red">SLU {slu:.2f}%</span>'
            elif slu > 1.0:
                badge = f'<span class="waste-badge-orange">SLU {slu:.2f}%</span>'
            else:
                badge = f'<span class="waste-badge-green">SLU {slu:.2f}%</span>'

            LU_NOM = r["LU_NOMINAL"]
            waste_mm = round(LU_NOM - setup["l_real"], 2)
            map_html = '<div class="cut-map">'
            for k, w in enumerate(setup["widths"]):
                flex = w * setup["rollCounts"][k]
                map_html += f'<div class="cut-segment" style="flex:{flex}"><span class="cut-label">{int(w)}</span><span class="cut-count">{setup["rollCounts"][k]}x</span></div>'
            waste_flex = max(abs(waste_mm), 5)
            map_html += f'<div class="cut-segment-waste" style="flex:{waste_flex}"><span class="cut-waste-label">{waste_mm:+.1f}</span></div>'
            map_html += '</div>'

            prog_w = min(max(abs(slu), 0), 100)
            progress_html = (
                '<div class="progress-wrap">'
                '<div class="progress-label"><span>SLU</span>'
                f'<span style="color:#ef4444;">{slu:.2f}%</span></div>'
                '<div class="progress-track">'
                f'<div class="progress-fill" style="width:{prog_w}%"></div>'
                '</div></div>'
            )

            _runs = setup["runs"]
            _lreal = setup["l_real"]
            _kglr = setup["kg_lreal"]
            _jcheios = setup["jumbos_cheios"]
            metrics_html = (
                '<div class="metric-row">'
                '<div class="metric-mini">'
                '<div class="metric-mini-label">Tiradas</div>'
                f'<div class="metric-mini-value" style="color:white">{_runs}</div></div>'
                '<div class="metric-mini">'
                '<div class="metric-mini-label">L. Real</div>'
                f'<div class="metric-mini-value" style="color:#7c3aed">{_lreal:.1f}<span style="font-size:10px">mm</span></div></div>'
                '<div class="metric-mini">'
                '<div class="metric-mini-label">Kg Setup</div>'
                f'<div class="metric-mini-value" style="color:#3b82f6">{_kglr:,.0f}<span style="font-size:10px">kg</span></div></div>'
                '<div class="metric-mini">'
                '<div class="metric-mini-label">Jumbos</div>'
                f'<div class="metric-mini-value" style="color:#94a3b8">{_jcheios}<span style="font-size:10px">+frac</span></div></div>'
                '</div>'
            )

            detail_rows = ""
            for k, w in enumerate(setup["widths"]):
                kerf = setup["kerfs"][k]
                cnt = setup["rollCounts"][k]
                detail_rows += (
                    '<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 12px;background:#0f172a;border:1px solid #1e293b;border-radius:8px;margin-bottom:6px;">'
                    '<div>'
                    f'<div style="font-size:11px;font-weight:900;color:#e2e8f0">{int(w)} mm</div>'
                    f'<div style="font-size:9px;color:#475569">Kerf: +{kerf:g}mm</div>'
                    '</div>'
                    f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:13px;font-weight:700;color:#7c3aed">{cnt}x</div>'
                    '<div style="text-align:right">'
                    f'<div style="font-size:11px;font-weight:700;color:#94a3b8">{int(w + kerf)} mm bruto</div>'
                    '</div>'
                    '</div>'
                )

            jumbo_str = f"{setup['jumbos_cheios']} RJ(s) completo(s)"
            if setup["runs_resto"] > 0:
                jumbo_str += f" + 1 fração ({setup['runs_resto']} tiradas)"

            _sid = setup["id"]
            _stipo = setup["tipo"]
            _card_html = (
                '<div class="combo-card">'
                '<div class="combo-header">'
                '<div style="display:flex;align-items:center;gap:10px;">'
                f'<span class="combo-id">{_sid}</span>'
                f'<span style="font-size:11px;font-weight:900;color:#94a3b8;text-transform:uppercase;letter-spacing:2px;">{_stipo}</span>'
                '</div>'
                f'{badge}'
                '</div>'
                f'{map_html}'
                f'{progress_html}'
                f'{metrics_html}'
                '<div style="margin-top:12px;padding:10px 12px;background:#0f172a;border:1px solid #1e293b;border-radius:8px;font-size:10px;color:#64748b;">'
                f'🏭 Consumo Extrusão: <b style="color:#94a3b8">{jumbo_str}</b>'
                '</div>'
                '<div style="margin-top:16px;padding-top:16px;border-top:1px solid #1e293b;">'
                '<div style="font-size:9px;font-weight:900;color:#475569;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px">Larguras do Esquema</div>'
                f'{detail_rows}'
                '</div>'
                '</div>'
            )
            st.markdown(_card_html, unsafe_allow_html=True)

    st.markdown('<div class="orange-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Resumo de Atendimento — Balanço de Massa</div>', unsafe_allow_html=True)

    if "balanco" not in r or not r["balanco"]:
        st.warning("Nenhum dado de balanço de massa foi gerado.")
    else:
        rows = []
        for b in r["balanco"]:
            infull = float(b.get("infull", 0))
            if 98 <= infull <= 102:
                badge_otif = f'<span class="otif-green">{infull:.1f}%</span>'
            elif infull > 102:
                badge_otif = f'<span class="otif-orange">{infull:.1f}%</span>'
            else:
                badge_otif = f'<span class="otif-red">{infull:.1f}%</span>'

            sobra = float(b.get("sobra_kg", 0))
            sobra_str = f'+{sobra:,.0f}' if sobra >= 0 else f'{sobra:,.0f}'
            rows.append(
                {
                    "Largura": f'{int(float(b.get("largura", 0)))} mm',
                    "Kerf": f'+{float(b.get("kerf", 0)):g}mm',
                    "Dem (un)": int(float(b.get("dem_rolos", 0))),
                    "Prod (un)": int(float(b.get("prod_rolos", 0))),
                    "In-Full": badge_otif,
                    "Dem (kg)": f'{float(b.get("kg_dem", 0)):,.0f}',
                    "Prod (kg)": f'{float(b.get("kg_prod", 0)):,.0f}',
                    "Sobra (kg)": sobra_str,
                }
            )

        df_bal = pd.DataFrame(rows)
        st.markdown(df_bal.to_html(escape=False, index=False), unsafe_allow_html=True)

    elapsed_str = f"{r.get('elapsed', 0):.2f}s"
    st.markdown(
        '<div style="text-align:center;padding:40px 0 20px;">'
        '<p style="color:#1e293b;font-size:10px;font-weight:900;text-transform:uppercase;letter-spacing:4px;">'
        f'MAGNERA INDUSTRIAL ENGINE · V10.22 · Tempo de processamento: {elapsed_str}'
        '</p></div>',
        unsafe_allow_html=True,
    )
