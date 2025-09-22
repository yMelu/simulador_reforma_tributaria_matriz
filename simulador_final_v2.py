import streamlit as st
from class_reforma_evento2026 import SimuladorReforma  
from reforma_27_c1_c2_c3 import SimuladorReforma2027
import pandas as pd
st.set_page_config(layout='wide')
#st.logo('logo_matriz_red.png',size='large',link='https://www.matrizcontabil.com.br/')


def entrada_dados_sidebar(ATIVIDADE):
    ALIQ_ISS = 0
    ALIQ_ICMS = 0
    CRED_ICMS = 0
    PCT_IRCS = 0
    PCT_BASE_IR = 0
    ADD_IR = False
    PCT_BASE_CS = 0

    with st.sidebar:
        st.divider()
        st.subheader('Input de informações')

        MARGEM = st.number_input('Indique sua margem desejada (%)', value=20.0, step=0.5, min_value=0.0,max_value=71.0) / 100

        if ATIVIDADE == 'Serviço':
            CUSTO = st.number_input('Indique o custo do serviço prestado', value=6200.0, min_value=1.0, step=1.0)
            ALIQ_ISS = st.number_input('Indique sua Alíquota de ISS (%)', value=5.0, step=1.0, min_value=2.0, max_value=5.0) / 100
            despesas = montar_despesas_creditos()
        else:
            CUSTO = st.number_input('Indique o custo da mercadoria vendida', value=10000.0, min_value=1.0, step=1.0)
            ALIQ_ICMS = st.number_input('Indique sua Alíquota de ICMS (%)', value=20.5, step=1.0, min_value=0.0) / 100
            CRED_ICMS = st.number_input('Indique seu crédito sob ICMS (%)', value=7.0, step=1.0, min_value=0.0) / 100
            despesas = montar_despesas_creditos()

        with st.expander('Indique suas alíquotas'):
            col1, col2 = st.columns(2)
            with col1:
                ALIQ_IRPJ = st.number_input('Alíquota IRPJ (%)', value=15.0, step=1.0) / 100
                ALIQ_CBS  = st.number_input('Alíquota CBS (%)', value=9.0, step=1.0) / 100
            with col2:
                ADD_IR = st.checkbox('Adicional de IR?')
                ALIQ_CSLL = st.number_input('Alíquota CSLL (%)', value=9.0, step=1.0) / 100

        with st.expander('Indique Percentuais Base'):
            if ATIVIDADE == 'Comércio':
                PCT_BASE_IR = st.number_input('Percentual Base IR (%)', value=8.0, step=1.0) / 100
                PCT_BASE_CS = st.number_input('Percentual Base CSLL (%)', value=12.0, step=1.0) / 100
            else:
                PCT_IRCS = st.number_input('Percentual Base IR CSLL (%)', value=32.0, step=1.0) / 100

        with st.expander('Contorle de tolerância - C3'):
            TOLERANCIA = st.number_input('Indique a tolerância máxima para C3',value=100.0,step=1.0,min_value=10.0,max_value=float(CUSTO/5),help="Menor = Mais preciso")

        if ATIVIDADE == 'Serviço' and ADD_IR:
            ADD_IR = 3.2 / 100

        elif ATIVIDADE == 'Comércio' and ADD_IR:
            ADD_IR = .8 / 100

        else:
            ADD_IR = 0

    return {
        "MARGEM": MARGEM,
        "CUSTO": CUSTO,
        "ALIQ_ISS": ALIQ_ISS,
        "ALIQ_ICMS": ALIQ_ICMS,
        "CRED_ICMS": CRED_ICMS,
        "ALIQ_CBS": ALIQ_CBS,
        "ALIQ_IRPJ": ALIQ_IRPJ,
        "ADD_IR": ADD_IR,
        "ALIQ_CSLL": ALIQ_CSLL,
        "PCT_BASE_IR": PCT_BASE_IR,
        "PCT_BASE_CS": PCT_BASE_CS,
        "PCT_IRCS": PCT_IRCS,
        "TOL":TOLERANCIA,
        "DESPESAS_CRED":despesas
    }

# Função para criar uma tabela HTML
def gerar_tabela_html(dados, cor_customizada):
    df = pd.DataFrame(dados)
    tabela_html = df.to_html(classes='table table-striped', index=False, escape=False)

    if cor_customizada:
        for campo, cor in cor_customizada.items():
            # Substituindo o valor das células específicas por HTML com estilos
            tabela_html = tabela_html.replace(
                f'>{campo}<', f' style="background-color: {cor};">{campo}<'
            )
    
    
    return tabela_html

def calc_creditos(dict_despesas, aliq_cbs):
    for c in dict_despesas.keys():
        dict_despesas[c]['cred'] = round(dict_despesas[c]['base'] * aliq_cbs, 2)
        dict_despesas[c]['custo'] = round(dict_despesas[c]['bruto'] - dict_despesas[c]['cred'], 2)

    return dict_despesas

def montar_despesas_creditos():
    DESPESAS_LOCACAO = 0.0
    DESPESAS_ALIM_HOSP = 0.0
    DESPESAS_SERV_PROF = 0.0
    DESPESAS_DEMAIS = 0.0
    DESPESAS_SIMPLES = 0.0
    TRABALHISTAS = 0.0
    DESPESAS_SAUDE_EDUCACAO = 0.0 

    with st.sidebar.expander("Inputs pós reforma"):
        st.subheader("Atualizando dados de despesas")
        col1, col2 = st.columns(2)
        with col1:
            DESPESAS_LOCACAO = st.number_input('Locação (70%)', min_value=0.0, step=1.0, format="%.2f",help='Informe aqui o total de despesas com locação. Será descontado 70% para cálculo de IBS/CBS.')
            DESPESAS_ALIM_HOSP = st.number_input('Alim./Hosp. (40%)', min_value=0.0, step=1.0, format="%.2f", help='Informe aqui o total de despesas com Alimentação e Hopedagem. Será descontado 40% para cálculo de IBS/CBS.')
            DESPESAS_SERV_PROF = st.number_input('Serv. Prof. (30%)', min_value=0.0, step=1.0, format="%.2f", help='Informe aqui o total de despesas com Serviçoes de profissionais regulados. Será descontado 30% para cálculo de IBS/CBS.')
        
        with col2:
            DESPESAS_DEMAIS = st.number_input('Demais Serviços (0%)', min_value=0.0, step=1.0, format="%.2f", help='Informe aqui o total de despesas com demais servicos que não se enquadram em outras janelas. Será Considerado 100% para cálculo de IBS/CBS.')
            DESPESAS_SIMPLES = st.number_input('Simples (96%)', min_value=0.0, step=1.0, format="%.2f", help='Informe aqui o total de despesas com Serviçoes de profissionais/empresas do Simples nacional. Será descontado 96% para cálculo de IBS/CBS.')
            TRABALHISTAS = st.number_input('Trabalhistas (100%)', min_value=0.0, step=1.0, format="%.2f", help='Informe aqui o total de despesas trabalhistas.')

        DESPESAS_SAUDE_EDUCACAO = st.number_input('Saúde e Educação (60%)', min_value=0.0, step=1.0, format="%.2f", help='Informe aqui o total de despesas com Súde e educação. Será descontado 60% para cálculo de IBS/CBS.')
    
    despesas_dict = {
        "locacao": {
            "bruto": DESPESAS_LOCACAO,
            "base": DESPESAS_LOCACAO * 0.30
        },
        "alim_hosp": {
            "bruto": DESPESAS_ALIM_HOSP,
            "base": DESPESAS_ALIM_HOSP * 0.60
        },
        "serv_prof": {
            "bruto": DESPESAS_SERV_PROF,
            "base": DESPESAS_SERV_PROF * 0.70
        },
        "demais": {
            "bruto": DESPESAS_DEMAIS,
            "base": DESPESAS_DEMAIS * 1.00
        },
        "simples": {
            "bruto": DESPESAS_SIMPLES,
            "base": DESPESAS_SIMPLES * 0.04  # 96% descontado → sobra 4%
        },
        "trabalhistas": {
            "bruto": TRABALHISTAS,
            "base": TRABALHISTAS * 0.00
        },
        "saude_educacao": {
            "bruto": DESPESAS_SAUDE_EDUCACAO,
            "base": DESPESAS_SAUDE_EDUCACAO * 0.40
        }
    }
    
    return despesas_dict

def buscar_margem_por_lucro_liquido(simulador_class, lucro_desejado, atividade, entradas, #c3
                                     ano=2027, tol=100.0, max_iter=1000):
    """
    Busca binária para encontrar a margem que resulte no lucro líquido desejado.
    
    Parâmetros:
    - simulador_class: classe simuladora (como SimuladorReforma2027)
    - lucro_desejado: valor-alvo de lucro líquido
    - atividade: "Serviço" ou "Comércio"
    - entradas: dicionário contendo alíquotas, custo, etc.
    - ano: ano de referência (default: 2027)
    - tol: tolerância para erro em R$ (default: 1.0)
    - max_iter: número máximo de iterações

    Retorna:
    - instância do simulador ajustada
    - margem encontrada
    - número de tentativas realizadas
    """

    margem_min = 0.0
    margem_max = 1.0  # até 100%
    iteracoes = 0

    while iteracoes < max_iter:
        margem_meio = (margem_min + margem_max) / 2

        simulador = simulador_class(
            ano=ano,
            atividade=atividade,
            margem=margem_meio,
            custo=entradas["CUSTO"],
            aliq_iss=entradas["ALIQ_ISS"] if atividade == 'Serviço' else 0,
            aliq_icms=entradas["ALIQ_ICMS"] if atividade != 'Serviço' else 0,
            cred_icms=entradas["CRED_ICMS"] if atividade != 'Serviço' else 0,
            aliq_cbs=entradas["ALIQ_CBS"],
            aliq_irpj=entradas["ALIQ_IRPJ"],
            add_ir=entradas["ADD_IR"],
            aliq_csll=entradas["ALIQ_CSLL"],
            pct_base_ir=entradas["PCT_BASE_IR"] if atividade != 'Serviço' else 0,
            pct_base_cs=entradas["PCT_BASE_CS"] if atividade != 'Serviço' else 0,
            pct_base_ircs=entradas["PCT_IRCS"] if atividade != 'Comércio' else 0,
            despesas_cred = entradas['DESPESAS_CRED']
        )

        dre = simulador.calcular_DRE()
        lucro_calculado = dre["Lucro Líquido"]
        erro = lucro_calculado - lucro_desejado

        if abs(erro) <= tol:
            return simulador, margem_meio, iteracoes

        if lucro_calculado > lucro_desejado:
            margem_max = margem_meio
        else:
            margem_min = margem_meio

        iteracoes += 1

    return None, None, iteracoes

def criar_simulador(ano, atividade, entradas, classe_simulador):
          
    return classe_simulador(
        ano=ano,
        atividade=atividade,
        margem=entradas["MARGEM"],
        custo=entradas["CUSTO"],
        aliq_iss=entradas["ALIQ_ISS"] if atividade == 'Serviço' else 0,
        aliq_icms=entradas["ALIQ_ICMS"] if atividade != 'Serviço' else 0,
        cred_icms=entradas["CRED_ICMS"] if atividade != 'Serviço' else 0,
        aliq_cbs=entradas["ALIQ_CBS"],
        aliq_irpj=entradas["ALIQ_IRPJ"],
        add_ir=entradas["ADD_IR"],
        aliq_csll=entradas["ALIQ_CSLL"],
        pct_base_ir=entradas["PCT_BASE_IR"] if atividade != 'Serviço' else 0,
        pct_base_cs=entradas["PCT_BASE_CS"] if atividade != 'Serviço' else 0,
        pct_base_ircs=entradas["PCT_IRCS"] if atividade != 'Comércio' else 0,
        despesas_cred = entradas['DESPESAS_CRED']
    )

def buscar_margem_por_preco_dre(
    simulador_class,
    preco_dre26,
    atividade,
    entradas,
    ano=2027,
    tol=100.0,
    max_iter=1000
):
    margem_min = 0.0
    margem_max = 1.0  # até 1000% de margem
    iteracoes = 0

    while iteracoes < max_iter:
        margem = (margem_min + margem_max) / 2

        simulador = simulador_class(
            ano=ano,
            atividade=atividade,
            margem=margem,
            custo=entradas["CUSTO"],
            aliq_iss=entradas["ALIQ_ISS"] if atividade == 'Serviço' else 0,
            aliq_icms=entradas["ALIQ_ICMS"] if atividade != 'Serviço' else 0,
            cred_icms=entradas["CRED_ICMS"] if atividade != 'Serviço' else 0,
            aliq_cbs=entradas["ALIQ_CBS"],
            aliq_irpj=entradas["ALIQ_IRPJ"],
            add_ir=entradas["ADD_IR"],
            aliq_csll=entradas["ALIQ_CSLL"],
            pct_base_ir=entradas["PCT_BASE_IR"] if atividade != 'Serviço' else 0,
            pct_base_cs=entradas["PCT_BASE_CS"] if atividade != 'Serviço' else 0,
            pct_base_ircs=entradas["PCT_IRCS"] if atividade != 'Comércio' else 0,
            despesas_cred = entradas['DESPESAS_CRED']
        )

        dre = simulador.calcular_DRE()
        preco = dre["Preço de venda"]
        erro = preco - preco_dre26

        if abs(erro) <= tol:
            return simulador, margem, iteracoes

        if preco > preco_dre26:
            margem_max = margem
        else:
            margem_min = margem

        iteracoes += 1

    return None, None, iteracoes


ATIVIDADE = st.sidebar.selectbox('Selecione sua atividade',['Comércio','Serviço'])
st.title(f"Simulador Matriz Contábil 2027 - {ATIVIDADE}")


VISAO = st.selectbox('Selecione a visão',['Resumo','Custo tomador',"DRE's Comparativas" ])
st.divider()

ENTRADAS = entrada_dados_sidebar(ATIVIDADE)

aliq_cbs = float(ENTRADAS['ALIQ_CBS'])
for _, item in ENTRADAS['DESPESAS_CRED'].items():
    # garante numéricos
    bruto = float(item['bruto'])
    base  = float(item['base'])

    cred  = round(base * aliq_cbs, 2)
    custo = round(bruto - cred, 2)

    item['cred']  = cred
    item['custo'] = custo

simulador2026 = criar_simulador(2026, ATIVIDADE, ENTRADAS, SimuladorReforma)
simulador2027 = criar_simulador(2027, ATIVIDADE, ENTRADAS, SimuladorReforma2027)

# Calcula a DRE
dre26 = simulador2026.calcular_DRE()
dre27 = simulador2027.calcular_DRE()

# Busca a margem que faça o preço de venda de 2027 bater com o de 2026
simuladorc2, margem_ajustada, tentativas = buscar_margem_por_preco_dre(
    SimuladorReforma2027,
    preco_dre26=dre26["Preço de venda"],
    atividade=ATIVIDADE,
    entradas=ENTRADAS,
    tol=ENTRADAS['TOL'],
)
simulador27_lucro, margem_lucro, tentativas = buscar_margem_por_lucro_liquido(
    SimuladorReforma2027,
    tol=ENTRADAS['TOL'],
    lucro_desejado=dre26["Lucro Líquido"],
    atividade=ATIVIDADE,
    entradas=ENTRADAS
)
c2 = simuladorc2.calcular_DRE()
if simulador27_lucro is not None:
    rc3 = simulador27_lucro.calcular_DRE()
else: 
    st.warning('Caso 3 não encontrado com os parametros apresentados.\n\n Modifique a margem desejada ou divergêcia maxima para convergir.')
    st.stop()

if VISAO == "DRE's Comparativas":
    col1, col2, col3, col4 = st.columns(4)
    # Dados de exemplo para cada conjunto (ajuste conforme necessário)
    dados_2026 = {
        'Métrica': ['Faturamento - NF', 'CBS', 'Receita Bruta (pré CBS)', 'PIS', 'COFINS', 'ICMS (C) / ISS (S)', 'Receita Líquida',
                    'CMV/CSV', 'Lucro antes IR/CS', 'IR','Adicional IR (R$)', 'CS', 'Lucro Líquido', 'Margem de Lucro'],
        'Valor': [
            f'R$ {dre26["Preço de venda"]:,.2f}',
            f'R$ {0:,.2f}',
            f'R$ {dre26["Preço de venda"]:,.2f}',
            f'R$ {dre26["pis"]:,.2f}',
            f'R$ {dre26["cofins"]:,.2f}',
            f'R$ {dre26["ICMS"] + dre26["ISS (R$)"]:,.2f}',
            f'R$ {dre26["receita liquida"]:,.2f}',
            f'R$ {dre26["Custo Mercadoria/Servico"]:,.2f}',
            f'R$ {dre26["Lucro antes IR/CS"]:,.2f}',
            f'R$ {dre26["IR Valor"]:,.2f}',
            f'R$ {dre26["Adicional IR (R$)"]:,.2f}',
            f'R$ {dre26["CS Valor"]:,.2f}',
            f'R$ {dre26["Lucro Líquido"]:,.2f}',
            f'{dre26["Margem de Lucro (%)"]:,.2%}'
        ]
    }
    cor_customizada_2026 = {
        'Receita Bruta (pré CBS)': '#a64d79',  # Ouro
        'Lucro Líquido': '#4682B4',  # Verde
        'Margem de Lucro': '#6B8E23',  # Azul claro
    }

    dados_2027 = {
        'Métrica': ['Faturamento - NF', 'CBS', 'Receita Bruta (pré CBS)', 'PIS', 'COFINS', 'ICMS', 'Receita Líquida',
                    'CMV/CSV', 'Lucro antes IR/CS', 'IR','Adicional IR (R$)','CS', 'Lucro Líquido', 'Margem de Lucro'],
        'Valor': [
            f'R$ {dre27["Nota fiscal"]:,.2f}',
            f'R$ {dre27["CBS VALOR"]:,.2f}',
            f'R$ {dre27["Preço de venda"]:,.2f}',
            f'R$ {0:,.2f}',
            f'R$ {0:,.2f}',
            f'R$ {dre27["ICMS"]:,.2f}',
            f'R$ {dre27["Receita Base CBS"]:,.2f}',
            f'R$ {dre27["Custo Mercadoria/Servico"]:,.2f}',
            f'R$ {dre27["Lucro antes IR/CS"]:,.2f}',
            f'R$ {dre27["IR Valor"]:,.2f}',
            f'R$ {dre27["Adicional IR (R$)"]:,.2f}',
            f'R$ {dre27["CS Valor"]:,.2f}',
            f'R$ {dre27["Lucro Líquido"]:,.2f}',
            f'{dre27["Margem de Lucro (%)"]:,.2%}'
        ]
    }

    cor_customizada_2027 = {
        'Margem de Lucro': '#6B8E23',  # Azul claro
    }


    dados_c2 = {
        'Métrica': ['Faturamento - NF', 'CBS', 'Receita Bruta (pré CBS)', 'PIS', 'COFINS', 'ICMS', 'Receita Líquida',
                    'CMV/CSV', 'Lucro antes IR/CS', 'IR','Adicional IR (R$)', 'CS', 'Lucro Líquido', 'Margem de Lucro'],
        'Valor': [
            f'R$ {c2["Nota fiscal"]:,.2f}',
            f'R$ {c2["CBS VALOR"]:,.2f}',
            f'R$ {c2["Preço de venda"]:,.2f}',
            f'R$ {0:,.2f}',
            f'R$ {0:,.2f}',
            f'R$ {c2["ICMS"]:,.2f}',
            f'R$ {c2["Receita Base CBS"]:,.2f}',
            f'R$ {c2["Custo Mercadoria/Servico"]:,.2f}',
            f'R$ {c2["Lucro antes IR/CS"]:,.2f}',
            f'R$ {c2["IR Valor"]:,.2f}',
            f'R$ {c2["Adicional IR (R$)"]:,.2f}',
            f'R$ {c2["CS Valor"]:,.2f}',
            f'R$ {c2["Lucro Líquido"]:,.2f}',
            f'{c2["Margem de Lucro (%)"]:,.2%}'
        ]
    }


    cor_customizada_c2 = {
        'Receita Bruta (pré CBS)': '#a64d79',  # Ouro
    }

    dados_rc3 = {
        'Métrica': ['Faturamento - NF', 'CBS', 'Receita Bruta (pré CBS)', 'PIS', 'COFINS', 'ICMS', 'Receita Líquida',
                    'CMV/CSV', 'Lucro antes IR/CS', 'IR','Adicional IR (R$)', 'CS', 'Lucro Líquido', 'Margem de Lucro'],
        'Valor': [
            f'R$ {rc3["Nota fiscal"]:,.2f}',
            f'R$ {rc3["CBS VALOR"]:,.2f}',
            f'R$ {rc3["Preço de venda"]:,.2f}',
            f'R$ {0:,.2f}',
            f'R$ {0:,.2f}',
            f'R$ {rc3["ICMS"]:,.2f}',
            f'R$ {rc3["Receita Base CBS"]:,.2f}',
            f'R$ {rc3["Custo Mercadoria/Servico"]:,.2f}',
            f'R$ {rc3["Lucro antes IR/CS"]:,.2f}',
            f'R$ {rc3["IR Valor"]:,.2f}',
            f'R$ {rc3["Adicional IR (R$)"]:,.2f}',
            f'R$ {rc3["CS Valor"]:,.2f}',
            f'R$ {rc3["Lucro Líquido"]:,.2f}',
            f'{rc3["Margem de Lucro (%)"]:,.2%}'
        ]
    }

    cor_customizada_c3 = {
        'Lucro Líquido': '#4682B4',  # Verde
    }

    # Exibindo as tabelas HTML
    with col1:
        st.subheader('2026')
        st.markdown(gerar_tabela_html(dados_2026,cor_customizada_2026), unsafe_allow_html=True)

    with col2:
        st.subheader('2027')
        st.markdown(gerar_tabela_html(dados_2027,cor_customizada_2027), unsafe_allow_html=True)

    with col3:
        st.subheader('2027 - C2')
        st.markdown(gerar_tabela_html(dados_c2,cor_customizada_c2), unsafe_allow_html=True)

    with col4:
        st.subheader('2027 - C3')
        st.markdown(gerar_tabela_html(dados_rc3,cor_customizada_c3), unsafe_allow_html=True)

elif VISAO == "Custo tomador":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader('Nota fiscal')
        st.divider()
        st.metric(f'2026', f'R$ {dre26['Preço de venda']:,.2f}')
        st.divider()
        st.metric(f'2027 - Regime regular', f'R$ {dre27['Nota fiscal']:,.2f}')
        st.divider()
        st.metric(f'2027 - Fora do Regime ', f'R$ {dre27['Nota fiscal']:,.2f}')
        st.divider()
        pass

    
    with col2:
        st.subheader('Crédito')
        st.divider()
        st.metric(f'2026', f'R$ {0:,.2f}')
        st.divider()
        st.metric(f'2027 - Regime regular', f'R$ {dre27['CBS VALOR']:,.2f}')
        st.divider()
        st.metric(f'2027 - Fora do Regime ', f'R$ {0:,.2f}')
        st.divider()

    st.divider()

    with col3:
        st.subheader('Para o tomador')
        st.divider()
        
        st.metric(f'2026',f'R$ {dre26['Preço de venda']:,.2f}')
        st.divider()
        st.metric(f'2027 - Regime regular', f'R$ {(dre27['Nota fiscal'] - dre27['CBS VALOR']):,.2f}')
        st.divider()
        st.metric(f'2027 - Fora do Regime ', f'R$ {(dre27['Nota fiscal']):,.2f}')
        st.divider()

elif VISAO == "Resumo":
    col1, col2, col3, col4 = st.columns(4)
    # Dados de exemplo para cada conjunto (ajuste conforme necessário)
    dados_2026 = {
        'Métrica': ['Faturamento - NF', 'Variação PV 2026' , 'Receita Bruta (pré CBS)',   'Lucro Líquido', 'Margem de Lucro', 'Variação Lucro Líquido 2026'],
        'Valor': [
            f'R$ {dre26["Preço de venda"]:,.2f}',
            f'-',
            f'R$ {dre26["Preço de venda"]:,.2f}',
            f'R$ {dre26["Lucro Líquido"]:,.2f}',
            f'{dre26["Margem de Lucro (%)"]:,.2%}',
            f'-'
        ]
    }
    cor_customizada_2026 = {
        'Receita Bruta (pré CBS)': '#a64d79',  # Ouro
        'Lucro Líquido': '#4682B4',  # Verde
        'Margem de Lucro': '#6B8E23',  # Azul claro
    }

    dados_2027 = {
        'Métrica': ['Faturamento - NF', 'Variação PV 2026', 'Receita Bruta (pré CBS)',   'Lucro Líquido', 'Margem de Lucro','Variação Lucro Líquido 2026'],
        'Valor': [
            f'R$ {dre27["Nota fiscal"]:,.2f}',
            f'{(dre27["Nota fiscal"]/dre26["Preço de venda"]) -1:,.1%}',
            f'R$ {dre27["Preço de venda"]:,.2f}',
            f'R$ {dre27["Lucro Líquido"]:,.2f}',
            f'{dre27["Margem de Lucro (%)"]:,.2%}',
            f'{(dre27["Lucro Líquido"]/dre26["Lucro Líquido"]) -1:,.1%}'
        ]
    }

    cor_customizada_2027 = {
        'Margem de Lucro': '#6B8E23',  # Azul claro
    }


    dados_c2 = {
        'Métrica': ['Faturamento - NF', 'Variação PV 2026',  'Receita Bruta (pré CBS)',   'Lucro Líquido', 'Margem de Lucro','Variação Lucro Líquido 2026'],
        'Valor': [
            f'R$ {c2["Nota fiscal"]:,.2f}',
            f'{(c2["Nota fiscal"]/dre26["Preço de venda"]) -1:,.1%}',
            f'R$ {c2["Preço de venda"]:,.2f}',
            f'R$ {c2["Lucro Líquido"]:,.2f}',
            f'{c2["Margem de Lucro (%)"]:,.2%}',
            f'{(c2["Lucro Líquido"]/dre26["Lucro Líquido"]) -1:,.1%}'
        ]
    }


    cor_customizada_c2 = {
        'Receita Bruta (pré CBS)': '#a64d79',  # Ouro
    }

    dados_rc3 = {
        'Métrica': ['Faturamento - NF', 'Variação PV 2026', 'Receita Bruta (pré CBS)',   'Lucro Líquido', 'Margem de Lucro', 'Variação Lucro Líquido 2026'],
        'Valor': [
            f'R$ {rc3["Nota fiscal"]:,.2f}',
            f'{(rc3["Nota fiscal"]/dre26["Preço de venda"]) -1:,.1%}',
            f'R$ {rc3["Preço de venda"]:,.2f}',
            f'R$ {rc3["Lucro Líquido"]:,.2f}',
            f'{rc3["Margem de Lucro (%)"]:,.2%}',
            f'{(rc3["Lucro Líquido"]/dre26["Lucro Líquido"]) -1:,.1%}'
        ]
    }

    cor_customizada_c3 = {
        'Lucro Líquido': '#4682B4',  # Verde
    }

    # Exibindo as tabelas HTML
    with col1:
        st.subheader('2026')
        st.markdown(gerar_tabela_html(dados_2026,cor_customizada_2026), unsafe_allow_html=True)

    with col2:
        st.subheader('2027')
        st.markdown(gerar_tabela_html(dados_2027,cor_customizada_2027), unsafe_allow_html=True)

    with col3:
        st.subheader('2027 - C2')
        st.markdown(gerar_tabela_html(dados_c2,cor_customizada_c2), unsafe_allow_html=True)

    with col4:
        st.subheader('2027 - C3')
        st.markdown(gerar_tabela_html(dados_rc3,cor_customizada_c3), unsafe_allow_html=True)


df_creditos_mostrar = pd.DataFrame(simulador2026.despesas_cred)
df_creditos_mostrar = df_creditos_mostrar.to_html()
with st.expander('Créditos 2027'):
    st.markdown(df_creditos_mostrar, unsafe_allow_html=True)


