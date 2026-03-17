import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
from datetime import datetime

# 1. Configuração de Página e Layout Dark Luxo
st.set_page_config(page_title="CASH FLOW | AP", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    /* Global Style */
    .main { background-color: #0B0E14; }
    div[data-testid="stMetricValue"] { color: #00D1FF; font-weight: 700; font-size: 1.8rem !important; }
    div[data-testid="stMetricLabel"] { color: #94A3B8; font-weight: 400; }
    
    /* Containers das Métricas */
    div[data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    /* Estilização das Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #1E293B;
        border-radius: 8px 8px 0 0;
        color: #94A3B8;
        padding: 10px 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #00D1FF !important; 
        color: #0B0E14 !important; 
    }

    /* Sidebar Custom */
    .css-1d391kg { background-color: #111827; }
    </style>
    """, unsafe_allow_html=True)

def format_brl(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- FUNÇÃO ADICIONADA: GERAÇÃO DE PDF ESTRATÉGICO ---
def generate_pdf(df_saidas, df_entradas, resumo_grupos, meses_selecionados):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Estilizado
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "RELATORIO ESTRATEGICO DE FLUXO DE CAIXA", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(190, 7, f"Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
    pdf.cell(190, 7, f"Periodos: {', '.join(meses_selecionados)}", ln=True, align='C')
    pdf.ln(10)

    # 1. Resumo Executivo
    total_in = df_entradas['Valor categoria/centro de custo'].sum()
    total_out = abs(df_saidas['Valor categoria/centro de custo'].sum())
    saldo = total_in - total_out
    
    pdf.set_fill_color(30, 41, 59)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 10, " 1. RESUMO EXECUTIVO (CASH FLOW)", ln=True, fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 11)
    pdf.ln(2)
    pdf.cell(95, 8, "Total de Entradas (Cash In):", 0); pdf.cell(95, 8, format_brl(total_in), 0, ln=True)
    pdf.cell(95, 8, "Total de Saidas (Cash Out):", 0); pdf.cell(95, 8, format_brl(total_out), 0, ln=True)
    
    if saldo < 0: pdf.set_text_color(200, 0, 0)
    else: pdf.set_text_color(0, 120, 0)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(95, 8, "SALDO LIQUIDO FINAL:", 0); pdf.cell(95, 8, format_brl(saldo), 0, ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    # 2. Top 10 Gastos (Vilões do Caixa)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(190, 10, " 2. TOP 10 CATEGORIAS (MAIORES GASTOS)", ln=True, fill=True)
    pdf.ln(2)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(100, 8, "Categoria", 1); pdf.cell(45, 8, "Valor", 1); pdf.cell(45, 8, "% do Total", 1, ln=True)
    
    pdf.set_font("Arial", '', 9)
    top_10 = df_saidas.groupby('Categoria')['Valor categoria/centro de custo'].sum().abs().sort_values(ascending=False).head(10)
    for cat, valor in top_10.items():
        perc = (valor / total_out * 100) if total_out > 0 else 0
        pdf.cell(100, 8, str(cat), 1)
        pdf.cell(45, 8, format_brl(valor), 1)
        pdf.cell(45, 8, f"{perc:.1f}%", 1, ln=True)
    pdf.ln(10)

    # 3. Composição por Grupo
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(190, 10, " 3. IMPACTO POR GRUPO ESTRATEGICO", ln=True, fill=True)
    pdf.ln(2)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(80, 8, "Grupo", 1); pdf.cell(55, 8, "Valor Total", 1); pdf.cell(55, 8, "% de Saida", 1, ln=True)
    
    pdf.set_font("Arial", '', 10)
    for _, row in resumo_grupos.iterrows():
        perc_g = (row['Valor R$'] / total_out * 100) if total_out > 0 else 0
        pdf.cell(80, 8, str(row['Grupo']), 1)
        pdf.cell(55, 8, format_brl(row['Valor R$']), 1)
        pdf.cell(55, 8, f"{perc_g:.1f}%", 1, ln=True)

    return pdf.output(dest='S')

MAPA_GRUPOS = {
    "Administrativo": ["ALUGUEL", "COMPRA DE ATIVO FIXO", "CONDOMÍNIO", "COWORKING", "CUSTO OPERACIONAL", "DESPESAS FINANCEIRAS", "ENERGIA ELÉTRICA", "ESTORNO", "EVENTOS FUNCIONÁRIOS", "DESPESAS VIAGEM", "MANUTENÇÃO ESCRITÓRIO", "MATERIAIS DE TI", "MATERIAL DE COPA", "MATERIAL DE ESCRITÓRIO", "MATERIAL DE LIMPEZA", "Multas Pagas","LOCOMOÇÃO", "OUTRAS DESPESAS", "PAGAMENTO DE EMPRÉSTIMO", "REPRESENTAÇÃO", "SEGUROS", "SERVIÇOS CONTÁBEIS","REPRESENTAÇÃO", "SERVIÇOS CONTRATADOS", "SERVIÇOS DE E-MAIL", "SERVIÇOS DE ENTREGA", "SERVIÇOS DE PUBLICIDADE", "SERVIÇOS JURÍDICOS", "SERVIÇOS TI", "SISTEMAS", "TAXAS E CONTRIBUIÇÕES", "TELEFONIA/INTERNET", "TREINAMENTOS", "VAGAS GARAGEM - SÓCIOS","SERVIÇOS DE PUBLICIDADE"],
    "Despesa de pessoal": ["13º SALÁRIO", "ADIANTAMENTO AO FUNCIONÁRIO", "ANTECIPAÇÃO DE RESULTADOS", "ASSISTÊNCIA MÉDICA", "ASSISTÊNCIA ODONTO", "BÔNUS CLT", "BÔNUS PERFORMANCE - G", "CONSULTORIA ESPECIALIZADA - G", "CONSULTORIA ESPECIALIZADA - TI", "DESPESA EVENTUAL DE PESSOAL", "ESTAGIÁRIO FOLHA", "EXAMES OCUPACIONAIS", "FÉRIAS", "FGTS", "GRATIFICAÇÕES CLT", "GRATIFICAÇÕES PJ - G", "INSS", "IRRF", "PRO LABORE", "RESCISÃO", "SALÁRIOS CLT", "SEGURO DE VIDA", "SERVIÇOS CONTRATADOS", "VA/VR", "VT"],
    "Operacional": ["BÔNUS - TERCEIROS", "COMISSÕES SEGUROS", "CUSTO OPERACIONAL", "Descontos Recebidos", "EVENTOS CLIENTES", "Multas Pagas", "REBATE COMISSÕES", "REPRESENTAÇÃO"],
    "Tributário": ["COFINS", "COFINS Retido sobre Pagamentos", "CSLL", "CSLL Retido sobre Pagamentos", "DESPESAS FINANCEIRAS", "ESTORNO", "INSS Retido sobre Pagamentos", "Juros Pagos", "IPTU", "IRPJ", "IRPJ Retido sobre Pagamentos", "ISS", "ISS Retido sobre Pagamentos", "Juros Pagos", "Multas Pagas", "Pagamento de ISS Retido", "PARCELAMENTO RECEITA FEDERAL", "PERT CSLL", "PERT IRPJ", "PERT IRRF", "PERT SN", "Multas Pagas", "PIS", "PIS Retido sobre Pagamentos"]
}

@st.cache_data(ttl=600)
def load_and_process():
    url_saidas = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT7KV7hi8lJHEleaPoPyAKWo7ChUTlLuorbLX9v4aZGXPKI6aeudpF06eUc60hmIPX8Pkz5BrZOhc1G/pub?gid=1959056339&single=true&output=csv"
    url_recebidos = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT7KV7hi8lJHEleaPoPyAKWo7ChUTlLuorbLX9v4aZGXPKI6aeudpF06eUc60hmIPX8Pkz5BrZOhc1G/pub?gid=58078527&single=true&output=csv"
    
    def clean_val(v):
        if isinstance(v, str):
            v = v.replace('R$', '').replace('.', '').replace(' ', '').replace(',', '.')
            try: return float(v)
            except: return 0.0
        return v

    col_v = 'Valor categoria/centro de custo'

    # Processar Saídas
    df_s = pd.read_csv(url_saidas)
    df_s[col_v] = df_s[col_v].apply(clean_val)
    df_s['Data de pagamento'] = pd.to_datetime(df_s['Data de pagamento'], dayfirst=True, errors='coerce')
    df_s = df_s.dropna(subset=['Data de pagamento']).sort_values('Data de pagamento')
    df_s['Mes_Ano'] = df_s['Data de pagamento'].dt.strftime('%m/%Y')
    
    def atribuir_grupo(cat):
        for grupo, categorias in MAPA_GRUPOS.items():
            if cat in categorias: return grupo
        return "Outros"
    df_s['Grupo_Filtro'] = df_s['Categoria'].apply(atribuir_grupo)

    # Processar Recebidos
    df_r = pd.read_csv(url_recebidos)
    df_r[col_v] = df_r[col_v].apply(clean_val)
    df_r['Data de pagamento'] = pd.to_datetime(df_r['Data de pagamento'], dayfirst=True, errors='coerce')
    df_r = df_r.dropna(subset=['Data de pagamento'])
    df_r['Mes_Ano'] = df_r['Data de pagamento'].dt.strftime('%m/%Y')

    return df_s, df_r

try:
    df_raw, df_rec_raw = load_and_process()
    col_v = 'Valor categoria/centro de custo'
    
    # Consolidação de meses de AMBAS as planilhas para o filtro
    meses_s = df_raw['Mes_Ano'].unique()
    meses_r = df_rec_raw['Mes_Ano'].unique()
    lista_meses = sorted(list(set(meses_s) | set(meses_r)), key=lambda x: pd.to_datetime(x, format='%m/%Y'))

    with st.sidebar:
        st.markdown("<h2 style='color: #00D1FF;'>💎 DASHBOARD</h2>", unsafe_allow_html=True)
        if st.button("🔄 Atualizar Dados", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        st.write("---")
        
        default_mes = [lista_meses[-1]] if lista_meses else []
        meses_sel = st.multiselect("📅 Períodos:", options=lista_meses, default=default_mes)
        grupos_sel = st.multiselect("📂 Grupos:", options=list(MAPA_GRUPOS.keys()), default=list(MAPA_GRUPOS.keys()))
        
        cats_dinamicas = [cat for g in grupos_sel for cat in MAPA_GRUPOS[g]]
        cats_sel = st.multiselect("🏷️ Categorias:", options=sorted(list(set(cats_dinamicas))), default=sorted(list(set(cats_dinamicas))))

        # --- BOTÃO ADICIONADO: EXPORTAÇÃO DE RELATÓRIO PDF ---
        st.write("---")
        st.markdown("### 📄 Exportar Relatório")
        if st.button("Gerar Base PDF", use_container_width=True):
            # Filtra dados conforme seleção atual para o PDF
            df_pdf = df_raw[df_raw['Mes_Ano'].isin(meses_sel)] if meses_sel else df_raw
            df_rec_pdf = df_rec_raw[df_rec_raw['Mes_Ano'].isin(meses_sel)] if meses_sel else df_rec_raw
            res_pdf = df_pdf[df_pdf[col_v] < 0].groupby('Grupo_Filtro')[col_v].sum().abs().reset_index()
            res_pdf.columns = ['Grupo', 'Valor R$']
            
            pdf_output = generate_pdf(df_pdf, df_rec_pdf, res_pdf, meses_sel)
            st.download_button(
                label="📥 Baixar Relatório PDF",
                data=bytes(pdf_output),
                file_name=f"Relatorio_Financeiro_AP_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    # Filtros Saídas
    df = df_raw.copy()
    if meses_sel: df = df[df['Mes_Ano'].isin(meses_sel)]
    if grupos_sel: df = df[df['Grupo_Filtro'].isin(grupos_sel)]
    if cats_sel: df = df[df['Categoria'].isin(cats_sel)]

    # Filtros Recebidos
    df_rec = df_rec_raw.copy()
    if meses_sel: df_rec = df_rec[df_rec['Mes_Ano'].isin(meses_sel)]

    # --- HEADER PRINCIPAL ---
    st.title("💸 Cash Flow | Expenses and Receipts")
    
    # Linha Superior: Cash In (Entradas)
    total_recebidos_header = df_rec[col_v].sum()
    c_in_1, c_in_2 = st.columns([1, 3])
    with c_in_1:
        st.markdown(f"""
            <div style='background: rgba(0, 209, 255, 0.1); padding: 20px; border-radius: 15px; border: 1px solid #00D1FF;'>
                <p style='color: #00D1FF; margin: 0; font-weight: bold;'>💰 TOTAL CASH IN (ENTRADAS)</p>
                <h2 style='color: #00D1FF; margin: 0;'>{format_brl(total_recebidos_header)}</h2>
            </div>
        """, unsafe_allow_html=True)
    
    st.write("") # Espaçador

    # Linha das Saídas
    saidas_df = df[df[col_v] < 0]
    total_geral = saidas_df[col_v].sum()
    
    cols_m = st.columns(len(grupos_sel) + 1)
    with cols_m[0]:
        st.metric("CASH OUT TOTAL", format_brl(abs(total_geral)))
    
    for i, grupo in enumerate(grupos_sel):
        val_g = df[(df['Grupo_Filtro'] == grupo) & (df[col_v] < 0)][col_v].sum()
        with cols_m[i+1]:
            st.metric(grupo.upper(), format_brl(abs(val_g)))

    st.write("---")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📊 APRESENTAÇÃO", "🔥 CASH BURN", "🎯 PARETO", "📋 DADOS", 
        "💰 RECEBIDOS", "📈 ANÁLISE MENSAL", "💎 LUCRATIVIDADE", "📖 GUIA DO DASHBOARD"
    ])

    with tab1:
        st.markdown("### 🏛️ Visão Executiva e Estrutura de Dados")
        st.markdown("---")
        
        pres_col1, pres_col2 = st.columns(2)
        
        with pres_col1:
            st.markdown(f"""
            #### 🎯 Objetivo da Ferramenta
            Este ecossistema foi projetado para converter dados brutos de faturamento e despesas em **Inteligência Financeira**.
            
            **Como os dados fluem:**
            1. **Ingestão:** Conexão direta com as planilhas de Saídas e Recebidos.
            2. **Processamento:** Limpeza de caracteres, padronização de datas e conversão monetária automática.
            3. **Categorização:** Mapeamento inteligente de categorias em 4 grandes grupos estratégicos:
                - **Administrativo**: Manutenção da infraestrutura.
                - **Pessoal**: Capital humano e encargos.
                - **Operacional**: Custo direto da prestação de serviço.
                - **Tributário**: Obrigações governamentais.
            """)
            
        with pres_col2:
            st.markdown("#### 🛠️ Pilares de Análise")
            st.info("**Fluxo de Caixa (Realizado):** Diferença exata entre o que entrou e o que saiu, sem projeções, focado no saldo bancário.")
            st.warning("**Eficiência de Custos:** Identificação de gargalos através da análise de Pareto (80/20) e impacto percentual por grupo.")
            st.success("**Saúde Líquida:** Visibilidade imediata de lucro ou prejuízo com alertas visuais por cores.")

        st.markdown("---")
        st.markdown("#### 📊 Hierarquia Financeira Atual")
        # Pequena tabela didática simplificada
        resumo_pres = pd.DataFrame({
            "Nível": ["1. Receita Bruta", "2. Despesas Totais", "3. Resultado Líquido"],
            "Descrição": ["Total de entradas (Cash In)", "Soma de todos os grupos de saída", "O que sobra no caixa da empresa"],
            "Foco": ["Crescimento", "Controle", "Sustentabilidade"]
        })
        st.table(resumo_pres)

    with tab2:
        st.subheader("Queima de Caixa Diária (Acumulada)")
        if not saidas_df.empty:
            burn = saidas_df.groupby('Data de pagamento')[col_v].sum().abs().cumsum().reset_index()
            burn.columns = ['Data', 'Gasto Acumulado']
            st.line_chart(burn.set_index('Data')['Gasto Acumulado'], color="#FF4B4B")
            st.write("#### Detalhamento de Saída Diária")
            diario = saidas_df.groupby('Data de pagamento')[col_v].sum().abs().reset_index()
            diario.columns = ['Data', 'Valor do Dia']
            st.dataframe(diario.style.format({'Valor do Dia': "R$ {:,.2f}"}), use_container_width=True, hide_index=True)
        else:
            st.info("Sem saídas registradas para este filtro.")

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Maiores Gastos por Grupo")
            g_pareto = saidas_df.groupby('Grupo_Filtro')[col_v].sum().abs().sort_values(ascending=False).reset_index()
            st.dataframe(g_pareto.style.format({col_v: "R$ {:,.2f}"}), use_container_width=True, hide_index=True)
            st.bar_chart(g_pareto.set_index('Grupo_Filtro')[col_v], color="#00D1FF")
        with c2:
            st.subheader("Top 10 Categorias")
            c_pareto = saidas_df.groupby('Categoria')[col_v].sum().abs().sort_values(ascending=False).head(10).reset_index()
            st.dataframe(c_pareto.style.format({col_v: "R$ {:,.2f}"}), use_container_width=True, hide_index=True)
            st.bar_chart(c_pareto.set_index('Categoria')[col_v], color="#00D1FF")

    with tab4:
        st.subheader("Explorador de Lançamentos")
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab5:
        st.subheader("Explorador de Recebidos")
        st.dataframe(df_rec, use_container_width=True, hide_index=True)

    with tab6:
        label_periodo = ", ".join(meses_sel) if meses_sel else "Nenhum período selecionado"
        st.subheader(f"Análise Financeira: {label_periodo}")
        curr_s = abs(df[df[col_v] < 0][col_v].sum())
        curr_e = df_rec[col_v].sum()
        resultado = curr_e - curr_s
        
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Entrou no Período", format_brl(curr_e))
        col_res2.metric("Saiu no Período", format_brl(curr_s))
        
        color_res = "#FF4B4B" if resultado < 0 else "#00D1FF"
        st.markdown(f"**Saldo Líquido**")
        st.markdown(f"<h2 style='color: {color_res}; margin-top: -15px;'>{format_brl(resultado)}</h2>", unsafe_allow_html=True)
        
        df_chart = pd.DataFrame({'Tipo': ['Entradas', 'Saídas'], 'Valores': [curr_e, curr_s]}).set_index('Tipo')
        st.bar_chart(df_chart, color="#00D1FF")

    with tab7:
        st.subheader("INDICADORES DE LUCRATIVIDADE")
        total_e = df_rec[col_v].sum()
        total_s = abs(df[df[col_v] < 0][col_v].sum())
        lucro_abs = total_e - total_s
        
        cl1, cl2 = st.columns(2)
        
        color_lucro = "#FF4B4B" if lucro_abs < 0 else "#00D1FF"
        with cl1:
            st.markdown(f"**LUCRO LÍQUIDO (CAIXA)**")
            st.markdown(f"<h2 style='color: {color_lucro}; margin-top: -15px;'>{format_brl(lucro_abs)}</h2>", unsafe_allow_html=True)
            
        st.write("#### Eficiência por Grupo (Lucro Líquido Caixa por Categoria)")
        if total_e > 0:
            grupo_valores = df[df[col_v] < 0].groupby('Grupo_Filtro')[col_v].sum().abs().reset_index()
            grupo_valores.columns = ['Grupo', 'Valor R$']
            
            st.bar_chart(grupo_valores.set_index('Grupo'), color="#00D1FF")
            
            st.write("📊 **Detalhamento de Impacto no Faturamento:**")
            total_saidas_filtradas = grupo_valores['Valor R$'].sum()
            if total_saidas_filtradas > 0:
                grupo_impacto = grupo_valores.copy()
                grupo_impacto['% Total Gastos'] = (grupo_impacto['Valor R$'] / total_saidas_filtradas * 100)
                st.dataframe(
                    grupo_impacto.assign(
                        Porcentagem=grupo_impacto['% Total Gastos'].apply(lambda x: f"{x:.1f}%"),
                        Valor=grupo_impacto['Valor R$'].apply(format_brl)
                    )[['Grupo', 'Valor', 'Porcentagem']], 
                    use_container_width=True, hide_index=True
                )
        else:
            st.info("Aguardando dados de receita para calcular impacto por grupo.")

    with tab8:
        st.header("📖 Guia Didático do Dashboard")
        st.markdown("""
        Este guia explica a lógica de funcionamento de cada seção e como os números são interpretados para ajudar na tomada de decisão.

        ---
        ### 1. Visão Geral (Cards Superiores)
        * **CASH IN TOTAL:** Total de entradas registradas. Posicionado no topo para indicar o fôlego inicial do caixa.
        * **CASH OUT TOTAL:** A soma absoluta de todos os valores negativos (saídas) no período selecionado.
        * **Métricas por Grupo:** Exibe o gasto total em cada grande área.

        ---
        ### 2. Explicação das Abas

        #### 📈 ANÁLISE MENSAL (Fluxo de Caixa Líquido)
        * **Saldo Líquido:** O valor numérico fica vermelho para prejuízo e verde/azul para lucro.

        #### 💎 LUCRATIVIDADE (Eficiência Operacional)
        * **Lucro Líquido (Caixa):** O valor numérico reflete a cor do resultado (Vermelho para negativo).
        """)

except Exception as e:
    st.error(f"Erro ao carregar layout: {e}")