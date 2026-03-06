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

st.set_page_config(page_title="Otimizador de Corte", page_icon="⚙️", layout="wide")

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700;900&family=JetBrains+Mono:wght@400;700&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; background-color: #0d0f1f; color: #e2e8f0; }
.main { background-color: #0d0f1f; }
.block-container { padding-top: 1rem; max-width: 1400px; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; font-weight: 900; }
.magnera-header { background: linear-gradient(135deg, #13153a 0%, #0d0f1f 100%); border: 1px solid #1e293b; border-radius: 16px; padding: 20px 28px; margin-bottom: 24px; display: flex; align-items: center; gap: 16px; }
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 20px 0; }
.kpi-card { background: #111827; border: 1px solid #1e293b; border-radius: 14px; padding: 18px; border-top: 3px solid; }
.kpi-label { font-size: 9px; font-weight: 900; color: #64748b; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 8px; }
.kpi-value { font-family: 'JetBrains Mono', monospace; font-size: 26px; font-weight: 700; line-height: 1; }
.kpi-desc { font-size: 9px; color: #475569; margin-top: 6px; font-style: italic; }
.section-card { background: #111827; border: 1px solid #1e293b; border-radius: 14px; padding: 20px; margin-bottom: 16px; }
.section-title { font-size: 11px; font-weight: 900; color: white; text-transform: uppercase; letter-spacing: 2px; border-left: 3px solid #7c3aed; padding-left: 10px; margin-bottom: 16px; }
.combo-card { background: #111827; border: 1px solid #1e293b; border-radius: 14px; padding: 20px; margin-bottom: 16px; }
.combo-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #1e293b; }
.combo-id { background: #0f172a; border: 1px solid #334155; border-radius: 50%; width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 900; color: #94a3b8; }
.waste-badge-red { background: #7f1d1d22; border: 1px solid #ef444433; color: #ef4444; padding: 3px 8px; border-radius: 6px; font-size: 10px; font-weight: 900; }
.waste-badge-orange { background: #7c2d1222; border: 1px solid #7c3aed33; color: #7c3aed; padding: 3px 8px; border-radius: 6px; font-size: 10px; font-weight: 900; }
.waste-badge-green { background: #05150e22; border: 1px solid #10b98133; color: #10b981; padding: 3px 8px; border-radius: 6px; font-size: 10px; font-weight: 900; }
.slu-neg-badge { background: #1a0e0022; border: 1px solid #f59e0b44; color: #f59e0b; padding: 3px 8px; border-radius: 6px; font-size: 10px; font-weight: 900; }
.cut-map { display: flex; height: 52px; background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; overflow: hidden; padding: 4px; gap: 3px; margin-bottom: 14px; }
.cut-segment { background: rgba(124,58,237,0.12); border: 1px solid rgba(124,58,237,0.25); border-radius: 7px; display: flex; flex-direction: column; align-items: center; justify-content: center; min-width: 20px; }
.cut-segment-waste { background: rgba(239,68,68,0.08); border: 1px dashed rgba(239,68,68,0.2); border-radius: 7px; display: flex; align-items: center; justify-content: center; min-width: 10px; }
.cut-label { font-size: 10px; font-weight: 900; color: #7c3aed; }
.cut-count { font-size: 8px; color: rgba(124,58,237,0.6); margin-top: 2px; }
.cut-waste-label { font-size: 9px; color: rgba(239,68,68,0.5); writing-mode: vertical-rl; }
.progress-wrap { margin-bottom: 14px; }
.progress-label { display: flex; justify-content: space-between; font-size: 9px; font-weight: 900; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
.progress-track { height: 6px; background: #0f172a; border-radius: 99px; border: 1px solid #1e293b; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 99px; background: linear-gradient(90deg, #dc2626, #7c3aed); }
.metric-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.metric-mini { background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 12px; }
.metric-mini-label { font-size: 8px; font-weight: 900; color: #475569; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.metric-mini-value { font-family: 'JetBrains Mono', monospace; font-size: 18px; font-weight: 700; }
.otif-green { background: #05150e; color: #10b981; border: 1px solid #10b98122; padding: 2px 8px; border-radius: 5px; font-size: 10px; font-weight: 900; }
.otif-orange { background: #1a0e00; color: #7c3aed; border: 1px solid #7c3aed22; padding: 2px 8px; border-radius: 5px; font-size: 10px; font-weight: 900; }
.otif-red { background: #1a0000; color: #ef4444; border: 1px solid #ef444422; padding: 2px 8px; border-radius: 5px; font-size: 10px; font-weight: 900; }
.orange-divider { height: 2px; background: linear-gradient(90deg, #8b5cf6, transparent); border-radius: 99px; margin: 24px 0; }
.warn-box { background: #1a0e00; border: 1px solid #f59e0b44; border-left: 4px solid #f59e0b; border-radius: 10px; padding: 16px 20px; margin: 16px 0; }
.info-box { background: #0f172a; border: 1px solid #3b82f644; border-left: 4px solid #3b82f6; border-radius: 10px; padding: 14px 18px; margin: 12px 0; font-size: 12px; color: #94a3b8; }
.matrix-ok   { background:#052010; border:1px solid #10b98155; border-radius:10px; padding:10px 16px; font-size:11px; color:#10b981; font-weight:700; margin-bottom:8px; }
.matrix-none { background:#0f172a; border:1px dashed #334155;   border-radius:10px; padding:10px 16px; font-size:11px; color:#475569; font-weight:700; margin-bottom:8px; }
.param-box { background:#111827; border:1px solid #1e293b; border-radius:12px; padding:16px; margin-bottom:12px; }
.param-box-title { font-size:9px; font-weight:900; color:#7c3aed; text-transform:uppercase; letter-spacing:2px; margin-bottom:12px; }
.stButton > button { background: linear-gradient(135deg, #ec4899, #8b5cf6) !important; color: white !important; font-weight: 900 !important; font-family: 'Space Grotesk', sans-serif !important; text-transform: uppercase !important; letter-spacing: 2px !important; font-size: 12px !important; border: none !important; border-radius: 10px !important; padding: 12px 32px !important; box-shadow: 0 0 20px rgba(139,92,246,0.35) !important; }
.stButton > button:hover { transform: scale(1.02) !important; box-shadow: 0 0 30px rgba(139,92,246,0.55) !important; }
input, select { background-color: #0f172a !important; color: #e2e8f0 !important; border-color: #1e293b !important; }
[data-baseweb="select"] input { caret-color: transparent !important; }
[data-testid="stSelectbox"] input { caret-color: transparent !important; cursor: default !important; }
</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)

def safe_num(val, fallback=0):
    try:
        n = float(val)
        return fallback if math.isnan(n) else n
    except:
        return fallback

K_VOLUME_EXTRUSAO = 1_250_000

# ─────────────────────────────────────────────
# MOTOR DE OTIMIZAÇÃO — VERSÃO V10 COMPLETA
# ─────────────────────────────────────────────
def run_optimization(df_config, df_pedidos_raw, df_lu, df_arr):
    """
    Recebe os 4 DataFrames do Excel e devolve:
      (result_dict, error_str)
    result_dict tem tudo que o relatório precisa.
    """
    # ── Config ───────────────────────────────────────────────────────────────
    config = dict(zip(df_config.iloc[:, 0].astype(str).str.strip(),
                      df_config.iloc[:, 1]))

    G        = float(config["Gramatura_GSM"])
    METRAGEM = float(config["Metragem_mL"])
    MAX_FACAS= int(config["Qtde_facas"])
    DIFF_LIMIT = float(config.get("Limitação_dif_larg", 30))
    OTIF_MAX   = float(config.get("Meta_OTIF", 1.01))
    FOLGA      = abs(OTIF_MAX - 1.0)
    MAX_SETUPS = int(config.get("Max_Setups", 10))
    MAX_LARG_ESQUEMA = int(config.get("Max_Larguras_Esquema", 2))
    L_MIN_FATOR = float(config.get("Fator_LU_Minima", 0.9))
    L1_TIRADAS  = float(config.get("Custo_por_Tirada",   config.get("Lambda_Tiradas", 50)))
    L2_SETUPS   = float(config.get("Custo_Troca_Faca",   config.get("Lambda_Setups",  8000)))
    L3_OVER     = float(config.get("Custo_Estoque_Parado", config.get("Lambda_Excesso", 5)))
    PREMIO_AVANCO = float(config.get("Bonus_Engenharia",  config.get("Premio_Avanco", 15)))
    CUSTO_FALTA = float(config.get("Custo_Falta_Pedido", 50.0))
    SETUP_MIN_PCT = float(config.get("Setup_Min_Eixo_Pct", 0.0))
    TOL_VAL    = float(config.get("Tolerancia_LU", -0.30))

    M = str(config["Maquina"]).strip()
    T = str(config["Tecnologia"]).strip()
    S = str(config["Surfactante"]).strip()
    C = str(config["Calandra"]).strip()
    IS_ZEB = (S.upper() == "ZEB")

    # ── Pedidos ──────────────────────────────────────────────────────────────
    col_larg = col_val = None
    for col in df_pedidos_raw.columns:
        nc = str(col).lower()
        if "largura" in nc: col_larg = col
        elif any(x in nc for x in ["valor", "peso", "pedido", "demanda", "kg"]): col_val = col
    if not col_larg: col_larg = df_pedidos_raw.columns[0]
    if not col_val:  col_val  = df_pedidos_raw.columns[1]

    df_ped = df_pedidos_raw[[col_larg, col_val]].copy()
    df_ped.columns = ["Largura_mm", "Valor_Kg"]
    df_ped["Largura_mm"] = pd.to_numeric(df_ped["Largura_mm"], errors="coerce")
    df_ped["Valor_Kg"]   = pd.to_numeric(df_ped["Valor_Kg"],   errors="coerce")
    df_ped = df_ped.dropna()
    if df_ped.empty:
        return None, "Aba 'Pedidos' não contém dados válidos."

    # ── LU Nominal da planilha ────────────────────────────────────────────────
    chave_lu = f"{M}{T}{S}{C}"
    gsm_col = None
    for col in df_lu.columns:
        try:
            if math.isclose(float(str(col).replace(",", ".")), float(G)):
                gsm_col = col; break
        except ValueError:
            if re.search(rf"\b{int(G)}\b", str(col)):
                gsm_col = col; break
    if gsm_col is None:
        return None, f"Gramatura {G} não encontrada na Matriz_LU."
    try:
        LU_NOMINAL = float(df_lu[df_lu.iloc[:, 0].astype(str).str.strip().str.upper() == chave_lu.upper()][gsm_col].values[0])
    except:
        return None, f"Chave de máquina não encontrada: {chave_lu}"

    LU_MAX = LU_NOMINAL * (1 + abs(TOL_VAL) / 100)

    # ── Kerf por largura ──────────────────────────────────────────────────────
    col_kerf_idx = 1
    for i, cn in enumerate(df_arr.columns):
        if any(w in str(cn).lower() for w in ["arruela", "kerf", "valor", "mm"]):
            col_kerf_idx = i; break

    dicionario_kerfs = {}
    def auditoria_kerf(largura):
        try:
            chave_k = f"{M}{T}{S}{C}{int(float(largura))}{int(G)}".upper()
            chaves  = df_arr.iloc[:, 0].astype(str).str.strip().str.upper()
            res = df_arr[chaves == chave_k]
            if not res.empty:
                val_raw = str(res.iloc[:, col_kerf_idx].values[0])
                val_clean = re.sub(r"[^\d.]", "", val_raw.replace(",", "."))
                v = float(val_clean) if val_clean else 0.0
                dicionario_kerfs[largura] = v
                return v
        except:
            pass
        dicionario_kerfs[largura] = 0.0
        return 0.0

    larguras = df_ped["Largura_mm"].tolist()
    larguras_efetivas = [l + auditoria_kerf(l) for l in larguras]
    demandas_rolos = [max(1, int(round(v / ((l * METRAGEM * G) / 1e6))))
                      for l, v in zip(larguras, df_ped["Valor_Kg"])]

    # ── Física de extrusão ────────────────────────────────────────────────────
    MAX_METROS_TEORICO = K_VOLUME_EXTRUSAO / G
    RUNS_MAX_POR_RJ = max(1, math.floor(MAX_METROS_TEORICO / METRAGEM))
    min_runs_raw = RUNS_MAX_POR_RJ * (SETUP_MIN_PCT / 100.0)
    MIN_RUNS_SETUP = max(1, int(math.floor(min_runs_raw + 0.5)))

    # ── ETAPA 3: MINERAÇÃO ────────────────────────────────────────────────────
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
                varredura(idx+1, qtd+q, l_acum + q*larguras_efetivas[idx], vetor)
                vetor[idx] = 0
        varredura(0, 0, 0.0, [0]*len(larguras))
        final_pool = []
        for p in pool:
            usadas = [larguras[i] for i in range(len(larguras)) if p["vetor"][i] > 0]
            if not (0 < len(usadas) <= MAX_LARG_ESQUEMA): continue
            if len(usadas) > 1 and any(
                round(abs(w1-w2),1) < DIFF_LIMIT
                for w1,w2 in itertools.combinations(usadas, 2)
            ): continue
            p["slu"]  = ((LU_NOMINAL - p["l_real"]) / LU_NOMINAL) * 100
            p["tipo"] = "Mono" if len(usadas)==1 else "Duo" if len(usadas)==2 else "Trio"
            final_pool.append(p)
        return final_pool

    pool_detalhado = minerar_pool()
    if not pool_detalhado:
        return None, "Pool vazio. Nenhum esquema válido encontrado. Verifique Parâmetros de corte."

    if not ORTOOLS_OK:
        return None, "OR-Tools não instalado. Execute: pip install ortools"

    # ── ETAPA 4: SOLVER ───────────────────────────────────────────────────────
    solver = pywraplp.Solver.CreateSolver("SCIP")
    if solver is None:
        return None, "Solver SCIP indisponível."

    NJ = len(pool_detalhado)
    NI = len(larguras)
    x         = [solver.IntVar(0, 10000,  f"x_{j}")     for j in range(NJ)]
    y         = [solver.IntVar(0, 1,       f"y_{j}")     for j in range(NJ)]
    underfill = [solver.IntVar(0, 100000,  f"under_{i}") for i in range(NI)]

    for i in range(NI):
        prod = sum(pool_detalhado[j]["vetor"][i] * x[j] for j in range(NJ))
        solver.Add(prod + underfill[i] >= demandas_rolos[i])
        solver.Add(prod <= math.ceil(demandas_rolos[i] * OTIF_MAX))
        solver.Add(underfill[i] <= math.ceil(demandas_rolos[i] * FOLGA))
    for j in range(NJ):
        solver.Add(x[j] <= 10000 * y[j])
        solver.Add(x[j] >= y[j] * MIN_RUNS_SETUP)
    solver.Add(sum(y) <= MAX_SETUPS)

    total_prod_kg_runs = sum(x[j]*((pool_detalhado[j]["l_real"]*METRAGEM*G)/1e6) for j in range(NJ))
    peso_dem_rolos = sum(demandas_rolos[i]*((larguras[i]*METRAGEM*G)/1e6) for i in range(NI))
    excesso_kg = total_prod_kg_runs - peso_dem_rolos
    custos_final = [(LU_NOMINAL-p["l_real"])*PREMIO_AVANCO if (LU_NOMINAL-p["l_real"])<0
                    else (LU_NOMINAL-p["l_real"])*10 for p in pool_detalhado]
    peso_falta_kg = sum(underfill[i]*((larguras[i]*METRAGEM*G)/1e6) for i in range(NI))
    solver.Minimize(
        sum(x[j]*custos_final[j] for j in range(NJ))
        + sum(x)*L1_TIRADAS + sum(y)*L2_SETUPS
        + excesso_kg*L3_OVER + peso_falta_kg*CUSTO_FALTA
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

    # ── ETAPA 5: COLETA DE RESULTADOS ─────────────────────────────────────────
    plano = []         # lista de setups ativos
    prod_rolos = [0]*NI
    t_runs = t_kg_lreal = t_kg_extrusado = t_kg_slu = 0
    kpi_rjs_cheios = kpi_rjs_parciais = 0
    tem_slu_negativo = False

    for j in range(NJ):
        runs = int(round(x[j].solution_value()))
        if runs <= 0: continue
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
        runs_resto    = runs % RUNS_MAX_POR_RJ

        if IS_ZEB:
            kpi_rjs_cheios   += jumbos_cheios
            kpi_rjs_parciais += 1 if runs_resto > 0 else 0

        if p["slu"] < -0.001: tem_slu_negativo = True

        widths_in = [larguras[i] for i in range(NI) if p["vetor"][i] > 0]
        cnts_in   = [p["vetor"][i] for i in range(NI) if p["vetor"][i] > 0]
        kerfs_in  = [dicionario_kerfs.get(larguras[i], 0) for i in range(NI) if p["vetor"][i] > 0]

        plano.append({
            "id": str(len(plano)+1),
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
        })
        for i in range(NI):
            prod_rolos[i] += p["vetor"][i] * runs

    if not IS_ZEB:
        kpi_rjs_cheios   = t_runs // RUNS_MAX_POR_RJ
        kpi_rjs_parciais = 1 if (t_runs % RUNS_MAX_POR_RJ) > 0 else 0

    # balanço de massa por largura
    balanco = []
    t_kg_vend = t_un_dem = t_un_prod = t_kg_prod_liq = t_kg_sobra = 0
    t_kg_estoque = t_kg_falta = 0
    for i, larg in enumerate(larguras):
        p_d_kg = (larg*METRAGEM*G*demandas_rolos[i])/1e6
        p_p_kg = (larg*METRAGEM*G*prod_rolos[i])/1e6
        sobra  = p_p_kg - p_d_kg
        infull = (prod_rolos[i]/demandas_rolos[i]*100) if demandas_rolos[i] > 0 else 0
        t_kg_vend += p_d_kg; t_un_dem += demandas_rolos[i]
        t_un_prod += prod_rolos[i]; t_kg_prod_liq += p_p_kg; t_kg_sobra += sobra
        if sobra > 0: t_kg_estoque += sobra
        elif sobra < 0: t_kg_falta += abs(sobra)
        balanco.append({
            "largura": larg,
            "kerf": dicionario_kerfs.get(larg, 0),
            "dem_rolos": demandas_rolos[i],
            "prod_rolos": prod_rolos[i],
            "infull": infull,
            "kg_dem": p_d_kg,
            "kg_prod": p_p_kg,
            "sobra_kg": sobra,
        })

    t_kg_kerf = t_kg_lreal - t_kg_prod_liq
    slu_final_pct = (t_kg_slu / t_kg_extrusado * 100) if t_kg_extrusado > 0 else 0
    total_infull = (t_un_prod / t_un_dem * 100) if t_un_dem > 0 else 0

    return {
        # meta
        "M": M, "T": T, "S": S, "C": C, "IS_ZEB": IS_ZEB,
        "G": G, "METRAGEM": METRAGEM, "LU_NOMINAL": LU_NOMINAL, "LU_MAX": LU_MAX,
        "OTIF_MAX": OTIF_MAX, "SETUP_MIN_PCT": SETUP_MIN_PCT,
        "MIN_RUNS_SETUP": MIN_RUNS_SETUP, "RUNS_MAX_POR_RJ": RUNS_MAX_POR_RJ,
        "MAX_SETUPS": MAX_SETUPS, "L1_TIRADAS": L1_TIRADAS,
        "L2_SETUPS": L2_SETUPS, "L3_OVER": L3_OVER, "CUSTO_FALTA": CUSTO_FALTA,
        "pool_size": len(pool_detalhado),
        # plano
        "plano": plano,
        "balanco": balanco,
        # KPIs
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


# SESSION STATE
_defaults = {
    "df_lu":     None,
    "df_arr":    None,
    "result":    None,
    "simulated": False,
    "orders": [
        {"id": "1", "largura": 0, "kg": 0.0},
        {"id": "2", "largura": 0, "kg": 0.0},
    ],
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

_LOGO = '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'

st.markdown(
    f'<div class="magnera-header">'
    f'<img src="data:image/png;base64,{_LOGO}" style="height:48px;object-fit:contain;" />'
    f'<div style="margin-left:auto;display:flex;align-items:center;gap:8px;">'
    f'<span style="width:8px;height:8px;background:#10b981;border-radius:50%;display:inline-block;"></span>'
    f'<span style="font-size:10px;color:#10b981;font-weight:900;text-transform:uppercase;">Online</span>'
    f'</div></div>',
    unsafe_allow_html=True
)

# ── HELPERS: leitura e cache em disco ────────────────────────────────────────
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
        pass  # cache opcional — não quebra o app

def _load_cache(key):
    p = _cache_path(key)
    if _os.path.exists(p):
        try:
            return pd.read_parquet(p)
        except Exception:
            pass
    return None

def _read_any_excel(raw_bytes, filename, sheet_hint=None):
    """
    Lê bytes de .xlsx/.xlsb/.xls.
    Detecta formato pelos magic bytes (independe da extensão).
    Usa cache MD5 em parquet para evitar releitura.
    """
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
            import pyxlsb  # noqa
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

# ── Carregar caches do disco no session_state ao iniciar ─────────────────────
if st.session_state.df_lu is None:
    _df_cached = _load_cache("df_lu_active")
    if _df_cached is not None:
        st.session_state.df_lu = _df_cached

if st.session_state.df_arr is None:
    _df_cached = _load_cache("df_arr_active")
    if _df_cached is not None:
        st.session_state.df_arr = _df_cached

# ── PÁGINA ÚNICA — OTIMIZADOR ─────────────────────────────────────────────────

st.markdown("""
<style>
[data-testid="stFileUploaderDropzoneInstructions"] small { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Bloco de uploads das matrizes ─────────────────────────────────────────────
_lu_ok  = st.session_state.df_lu  is not None
_arr_ok = st.session_state.df_arr is not None

with st.expander(
    ("✅ Tabelas carregadas" if (_lu_ok and _arr_ok)
     else "⚠️  Matrizes de Referência — clique para carregar"),
    expanded=not (_lu_ok and _arr_ok)
):
    st.markdown(
        '<div class="info-box" style="margin-top:0">'
        '📁 Aceita <b>.xlsb</b> e <b>.xlsx</b>.'
        '</div>',
        unsafe_allow_html=True)

    _uc1, _uc2 = st.columns(2)

    with _uc1:
        st.markdown('<div class="param-box-title">TABELA — Largura útil</div>', unsafe_allow_html=True)
        if _lu_ok:
            _df = st.session_state.df_lu
            st.markdown(f'<div class="matrix-ok">✅ Carregada — {len(_df)} linhas x {len(_df.columns)} colunas</div>', unsafe_allow_html=True)
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
            st.markdown(f'<div class="matrix-ok">✅ Carregada — {len(_df)} linhas x {len(_df.columns)} colunas</div>', unsafe_allow_html=True)
            with st.expander('Visualizar'):
                st.dataframe(_df.head(100), use_container_width=True)
                st.caption(f'Exibindo 100 de {len(_df)} linhas')
        else:
            st.markdown('<div class="matrix-none">Aguardando arquivo</div>', unsafe_allow_html=True)
        _f_arr = st.file_uploader('Arruelas (.xlsx ou .xlsb)', key='up_arr', label_visibility='collapsed')

# Processar uploads FORA do expander - evita conflito rerun dentro de contextos aninhados
if _f_lu is not None:
    _fname_lu = _f_lu.name
    if not any(_fname_lu.lower().endswith(e) for e in ('.xlsx','.xlsb','.xls','.bin')):
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
    if not any(_fname_arr.lower().endswith(e) for e in ('.xlsx','.xlsb','.xls','.bin')):
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

_lu_ok  = st.session_state.df_lu  is not None
_arr_ok = st.session_state.df_arr is not None

st.markdown('<div class="orange-divider"></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Especificações do Material</div>', unsafe_allow_html=True)
st.markdown('<div class="param-box">', unsafe_allow_html=True)
st.markdown('<div class="param-box-title">Identificação da Máquina</div>', unsafe_allow_html=True)
_c1, _c2, _c3, _c4 = st.columns(4)
machine    = _c1.selectbox('Máquina',     ['PAL01','PAL02','SJP05','SJP06','SJP07','SJP08','SJP09'], key='machine')
technology = _c2.selectbox('Tecnologia',  ['SMS','SSS'],  key='technology')
surfactant = _c3.selectbox('Surfactante', ['HFO','HFL','ZEB'],  key='surfactant')
calender   = _c4.selectbox('Calandra',    ['OVAL','ESTRELA'], key='calender')
st.markdown('</div>', unsafe_allow_html=True)

_cm1, _cm2 = st.columns(2)
with _cm1:
    st.markdown('<div class="param-box">', unsafe_allow_html=True)
    st.markdown('<div class="param-box-title">Material</div>', unsafe_allow_html=True)
    _mc1, _mc2 = st.columns(2)
    grammage      = _mc1.number_input('Gramatura (g/m²)', value=0.0, step=0.5,   format='%.1f', min_value=1.0)
    linear_meters = _mc2.number_input('Metragem (m)',     value=0, step=100,  min_value=100)
    st.markdown('</div>', unsafe_allow_html=True)
with _cm2:
    st.markdown('<div class="param-box">', unsafe_allow_html=True)
    st.markdown('<div class="param-box-title">Largura Útil & Refile</div>', unsafe_allow_html=True)
    _tc1, _tc2 = st.columns(2)
    fator_lu_min = _tc1.number_input('%Utilização da LU', value=0.93, step=0.01, format='%.2f', min_value=0.5, max_value=1.0)
    tol_lu       = _tc2.number_input('Avanço de Refile (%)', value=0.30, step=0.05, format='%.2f', min_value=0.0)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Restrições de Corte & Solver</div>', unsafe_allow_html=True)

_rc1, _rc2 = st.columns(2)
with _rc1:
    st.markdown('<div class="param-box">', unsafe_allow_html=True)
    st.markdown('<div class="param-box-title">Configuração Rebobinadeira</div>', unsafe_allow_html=True)
    _rr1, _rr2, _rr3 = st.columns(3)
    max_facas    = _rr1.number_input('Qtde Facas',           value=8,    step=1,   min_value=1)
    max_larg_esq = _rr2.number_input('Max Larguras/Esquema', value=2,    step=1,   min_value=1, max_value=5)
    diff_limit   = _rr3.number_input('Dif. Mín. Larg. (mm)', value=30.0, step=5.0, min_value=0.0)
    st.markdown('</div>', unsafe_allow_html=True)

with _rc2:
    st.markdown('<div class="param-box">', unsafe_allow_html=True)
    st.markdown('<div class="param-box-title">In Full & Setups</div>', unsafe_allow_html=True)
    _rs1, _rs2, _rs3 = st.columns(3)
    meta_otif     = _rs1.number_input('Meta In Full (%)',       value=105.0, step=0.5,  format='%.1f', min_value=100.0, max_value=115.0)
    max_setups    = _rs2.number_input('Max Setups',          value=10,    step=1,    min_value=1)
    setup_min_pct = _rs3.number_input('Ocup. Mín. Eixo (%)', value=70.0,  step=1.0,  format='%.1f', min_value=0.0)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="param-box">', unsafe_allow_html=True)
st.markdown('<div class="param-box-title">Custos & Penalidades</div>', unsafe_allow_html=True)
_cp1, _cp2, _cp3, _cp4, _cp5 = st.columns(5)
custo_tirada  = _cp1.number_input('Custo Tirada',      value=0.0,   step=10.0)
custo_setup   = _cp2.number_input('Custo Troca Faca',  value=0.0, step=500.0)
custo_estoque = _cp3.number_input('Custo Excesso Estoque',     value=0.0,    step=1.0)
custo_falta   = _cp4.number_input('Custo Falta Material',       value=100.0,   step=5.0)
bonus_eng     = _cp5.number_input('Custo Avanço Refile',  value=100.0,   step=1.0)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="orange-divider"></div>', unsafe_allow_html=True)
# ── DIAGNÓSTICO DE REGRAS (sempre visível, usa inputs atuais) ────────────────
st.markdown('<div class="section-title">Diagnóstico de Regras de Negócio</div>', unsafe_allow_html=True)
_dstr_setup   = 'BAIXA — Prioridade: Reduzir SLU' if custo_setup < 3000 else 'ALTA — Prioridade: Evitar paradas da rebobinadeira'
_dstr_estoque = 'FLEXÍVEL — Gera estoque para salvar SLU' if custo_estoque <= 5 else 'RÍGIDA — Evita estoque a todo custo'
_dstr_falta   = 'PERMITIDA — Pode entregar a menos' if custo_falta <= 10 else 'PROIBIDA — In-Full 100%'
_dpct_over    = meta_otif - 100.0
_dzeb         = surfactant == 'ZEB'
_dextrusao    = f'ZEBRADO ({surfactant})' if _dzeb else f'HOMOGÊNEO ({surfactant})'
_diag_html = (
    '<div class="info-box">'
    f'<b>Máquina:</b> {machine} | {technology} | {surfactant} | {calender} &nbsp;|&nbsp;'
    f'<b>%Utilização da LU:</b> {fator_lu_min:.2f} &nbsp;|&nbsp;'
    f'<b>Avanço de Refile (%):</b> {tol_lu:.2f}%<br>'
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
    _new_larg = _oc1.number_input('', value=int(_order['largura']), step=1, min_value=1,
                                   key=f"larg_{_order['id']}", label_visibility='collapsed')
    _new_kg   = _oc2.number_input('', value=float(_order['kg']),   step=100.0, min_value=0.0,
                                   key=f"kg_{_order['id']}",   label_visibility='collapsed')
    if _oc3.button('🗑', key=f"del_{_order['id']}"):
        _to_delete.append(_order['id'])
    st.session_state.orders[_i]['largura'] = _new_larg
    st.session_state.orders[_i]['kg']      = _new_kg

for _did in _to_delete:
    st.session_state.orders = [o for o in st.session_state.orders if o['id'] != _did]
    st.rerun()

if st.button('＋ Adicionar Largura'):
    _new_id = str(max((int(o['id']) for o in st.session_state.orders), default=0) + 1)
    st.session_state.orders.append({'id': _new_id, 'largura': 300, 'kg': 1000.0})
    st.rerun()

st.markdown('<div class="orange-divider"></div>', unsafe_allow_html=True)

_ready = (_lu_ok and _arr_ok
          and len(st.session_state.orders) > 0
          and all(o['largura'] > 0 and o['kg'] > 0 for o in st.session_state.orders))

if st.button('⚡  OTIMIZAR ESQUEMA DE CORTE', disabled=not _ready):
    _config_data = {
        'Maquina':              machine,
        'Tecnologia':           technology,
        'Surfactante':          surfactant,
        'Calandra':             calender,
        'Gramatura_GSM':        grammage,
        'Metragem_mL':          linear_meters,
        'Qtde_facas':           max_facas,
        'Max_Larguras_Esquema': max_larg_esq,
        'Limitação_dif_larg':   diff_limit,
        'Fator_LU_Minima':      fator_lu_min,
        'Tolerancia_LU':        -tol_lu,
        'Meta_OTIF':            meta_otif / 100.0,
        'Max_Setups':           max_setups,
        'Setup_Min_Eixo_Pct':   setup_min_pct,
        'Custo_por_Tirada':     custo_tirada,
        'Custo_Troca_Faca':     custo_setup,
        'Custo_Estoque_Parado': custo_estoque,
        'Custo_Falta_Pedido':   custo_falta,
        'Bonus_Engenharia':     bonus_eng,
    }
    _df_cfg = pd.DataFrame(list(_config_data.items()), columns=['param', 'value'])
    _df_ped = pd.DataFrame([
        {'Largura_mm': o['largura'], 'Valor_Kg': o['kg']}
        for o in st.session_state.orders
    ])
    with st.spinner('⏳ Minerando esquemas e resolvendo ILP com SCIP...'):
        _t0 = time.time()
        _result, _err = run_optimization(
            _df_cfg, _df_ped,
            st.session_state.df_lu,
            st.session_state.df_arr,
        )
        _elapsed = time.time() - _t0
    if _err:
        st.error(_err)
    else:
        _result['elapsed'] = _elapsed
        st.session_state.result    = _result
        st.session_state.simulated = True

elif not _ready and (_lu_ok and _arr_ok):
    st.info('Preencha todas as demandas para habilitar o otimizador.')

if st.session_state.simulated and st.session_state.result:
    r = st.session_state.result

    # ── ALERTA SLU NEGATIVO ───────────────────────────────────────────────────
    if r["tem_slu_negativo"]:
        st.markdown("""
        <div class="warn-box">
        ⚠️ <b>ATENÇÃO: PLANO COM SLU NEGATIVO (AVANÇO DA LARGURA ÚTIL) IDENTIFICADO</b><br>
        <span style="font-size:12px;color:#94a3b8;">
        Requer aprovação obrigatória da Engenharia de Processos antes da produção.
        </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="orange-divider"></div>', unsafe_allow_html=True)

    # ── KPI PRINCIPAL ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📊 KPI Final da Campanha</div>', unsafe_allow_html=True)

    slu_color  = "#10b981" if r["slu_final_pct"] < 1.0 else ("#f59e0b" if r["slu_final_pct"] < 1.5 else "#ef4444")
    inf_color  = "#10b981" if r["total_infull"] >= 98 else "#ef4444"
    ext_color  = "#3b82f6"
    rj_color   = "#7c3aed"
    est_color  = "#f59e0b" if r["t_kg_estoque"] > 0 else "#10b981"
    falt_color = "#ef4444" if r["t_kg_falta"] > 0 else "#10b981"

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card" style="border-top-color:{slu_color}">
        <div class="kpi-label">SLU Global</div>
        <div class="kpi-value" style="color:{slu_color}">{r["slu_final_pct"]:.2f}%</div>
        <div class="kpi-desc">Perda lateral s/ extrusão</div>
      </div>
      <div class="kpi-card" style="border-top-color:{ext_color}">
        <div class="kpi-label">Massa Extrusada</div>
        <div class="kpi-value" style="color:{ext_color}">{r["t_kg_extrusado"]:,.0f} kg</div>
        <div class="kpi-desc">Líquida: {r["t_kg_prod_liq"]:,.0f} kg</div>
      </div>
      <div class="kpi-card" style="border-top-color:{rj_color}">
        <div class="kpi-label">Jumbos Físicos</div>
        <div class="kpi-value" style="color:{rj_color}">{r["kpi_rjs_total"]}</div>
        <div class="kpi-desc">{r["kpi_rjs_cheios"]} completos + {r["kpi_rjs_parciais"]} fração</div>
      </div>
      <div class="kpi-card" style="border-top-color:{inf_color}">
        <div class="kpi-label">In-Full Global</div>
        <div class="kpi-value" style="color:{inf_color}">{r["total_infull"]:.1f}%</div>
        <div class="kpi-desc">{r["t_runs"]} tiradas totais</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # segunda linha de KPIs
    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card" style="border-top-color:#64748b">
        <div class="kpi-label">Massa Pedida</div>
        <div class="kpi-value" style="color:#94a3b8">{r["t_kg_vend"]:,.0f} kg</div>
        <div class="kpi-desc">Demanda total</div>
      </div>
      <div class="kpi-card" style="border-top-color:#ef4444">
        <div class="kpi-label">Refugo Facas</div>
        <div class="kpi-value" style="color:#ef4444">{r["t_kg_kerf"]:,.0f} kg</div>
        <div class="kpi-desc">Arruelas / Kerf</div>
      </div>
      <div class="kpi-card" style="border-top-color:{est_color}">
        <div class="kpi-label">Estoque Gerado</div>
        <div class="kpi-value" style="color:{est_color}">{r["t_kg_estoque"]:,.0f} kg</div>
        <div class="kpi-desc">Sobra acima da demanda</div>
      </div>
      <div class="kpi-card" style="border-top-color:{falt_color}">
        <div class="kpi-label">Falta em Pedidos</div>
        <div class="kpi-value" style="color:{falt_color}">{r["t_kg_falta"]:,.0f} kg</div>
        <div class="kpi-desc">Dívida com clientes</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="orange-divider"></div>', unsafe_allow_html=True)

    # ── PLANO DE CORTE (Cards) ────────────────────────────────────────────────
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

            # Mapa visual de corte
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
            progress_html = f"""
            <div class="progress-wrap">
              <div class="progress-label"><span>SLU</span><span style="color:#ef4444;">{slu:.2f}%</span></div>
              <div class="progress-track"><div class="progress-fill" style="width:{prog_w}%"></div></div>
            </div>"""

            metrics_html = f"""
            <div class="metric-row">
              <div class="metric-mini">
                <div class="metric-mini-label">Tiradas</div>
                <div class="metric-mini-value" style="color:white">{setup["runs"]}</div>
              </div>
              <div class="metric-mini">
                <div class="metric-mini-label">L. Real</div>
                <div class="metric-mini-value" style="color:#7c3aed">{setup["l_real"]:.1f}<span style="font-size:10px">mm</span></div>
              </div>
              <div class="metric-mini">
                <div class="metric-mini-label">Kg Setup</div>
                <div class="metric-mini-value" style="color:#3b82f6">{setup["kg_lreal"]:,.0f}<span style="font-size:10px">kg</span></div>
              </div>
              <div class="metric-mini">
                <div class="metric-mini-label">Jumbos</div>
                <div class="metric-mini-value" style="color:#94a3b8">{setup["jumbos_cheios"]}<span style="font-size:10px">+frac</span></div>
              </div>
            </div>"""

            detail_rows = ""
            for k, w in enumerate(setup["widths"]):
                kerf = setup["kerfs"][k]
                cnt  = setup["rollCounts"][k]
                detail_rows += (
                    '<div style="display:flex;justify-content:space-between;align-items:center;'
                    'padding:10px 12px;background:#0f172a;border:1px solid #1e293b;'
                    'border-radius:8px;margin-bottom:6px;">'
                    '<div>'
                    f'<div style="font-size:11px;font-weight:900;color:#e2e8f0">{int(w)} mm</div>'
                    f'<div style="font-size:9px;color:#475569">Kerf: +{kerf:g}mm</div>'
                    '</div>'
                    f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:13px;font-weight:700;color:#7c3aed">{cnt}x</div>'
                    '<div style="text-align:right">'
                    f'<div style="font-size:11px;font-weight:700;color:#94a3b8">{int(w+kerf)} mm bruto</div>'
                    '</div>'
                    '</div>'
                )

            jumbo_str = f"{setup['jumbos_cheios']} RJ(s) completo(s)"
            if setup["runs_resto"] > 0:
                jumbo_str += f" + 1 fração ({setup['runs_resto']} tiradas)"

            _sid   = setup["id"]
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

    # ── BALANÇO DE MASSA ──────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Resumo de Atendimento — Balanço de Massa</div>', unsafe_allow_html=True)

    rows = []
    for b in r["balanco"]:
        infull = b["infull"]
        if 98 <= infull <= 102:
            badge_otif = f'<span class="otif-green">{infull:.1f}%</span>'
        elif infull > 102:
            badge_otif = f'<span class="otif-orange">{infull:.1f}%</span>'
        else:
            badge_otif = f'<span class="otif-red">{infull:.1f}%</span>'

        sobra_str = f'+{b["sobra_kg"]:,.0f}' if b["sobra_kg"] >= 0 else f'{b["sobra_kg"]:,.0f}'
        rows.append({
            "Largura": f'{int(b["largura"])} mm',
            "Kerf": f'+{b["kerf"]:g}mm',
            "Dem (un)": int(b["dem_rolos"]),
            "Prod (un)": int(b["prod_rolos"]),
            "In-Full": badge_otif,
            "Dem (kg)": f'{b["kg_dem"]:,.0f}',
            "Prod (kg)": f'{b["kg_prod"]:,.0f}',
            "Sobra (kg)": sobra_str,
        })

    df_bal = pd.DataFrame(rows)
    st.write(df_bal.to_html(escape=False, index=False), unsafe_allow_html=True)

    # ── FOOTER ────────────────────────────────────────────────────────────────
    elapsed_str = f"{r.get('elapsed', 0):.2f}s"
    st.markdown(f"""
    <div style="text-align:center;padding:40px 0 20px;">
      <p style="color:#1e293b;font-size:10px;font-weight:900;text-transform:uppercase;letter-spacing:4px;">
        MAGNERA INDUSTRIAL ENGINE · V10.22 · Tempo de processamento: {elapsed_str}
      </p>
    </div>
    """, unsafe_allow_html=True)
