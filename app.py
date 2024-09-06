import pandas as pd
from datetime import datetime, timedelta
import ta.momentum
import fundamentus
import yfinance as yf
import panel as pn

import hvplot.pandas

pn.extension()

##### BASE DE DADOS ####

# Carrega a lista de ações
stocklist = pd.read_csv('acoes-listada-b3.csv', header=None)
listagem = stocklist.values.flatten().tolist()

# Função para buscar os dados da ação com yfinance
def df_acoes(ticker_symbol):
    df_tecnico = yf.download(f'{ticker_symbol}.SA', start='2023-01-01', end=datetime.now())
    df_tecnico['RSI'] = ta.momentum.rsi(close = df_tecnico['Close'], window=14)
    df_tecnico['ma9'] = df_tecnico['Close'].rolling(window=9).mean()
    df_tecnico['ma20'] = df_tecnico['Close'].rolling(window=20).mean()
    df_tecnico['ma200'] = df_tecnico['Close'].rolling(window=200).mean()
    

    return df_tecnico


#Funcao para buscar os fundamentos
def df_fund(ticker_symbol):
    df_fundamentos = fundamentus.get_papel(ticker_symbol)
    
    return df_fundamentos

# Variável global para armazenar o valor selecionado
selected_value = listagem[0]  # Valor padrão inicial

# Função para atualizar o gráfico com base na seleção
def update_and_fetch(event):
    global selected_value
    selected_value = select.value  # Atualiza a variável com a escolha
    df_tecnico = df_acoes(selected_value)  # Busca dados com yfinance
    df_tecnico['Date'] = pd.to_datetime(df_tecnico.index)
    
    # Atualiza o gráfico
    #plot_pane.object = df_tecnico['Close'].hvplot(title=f"Cotação de {selected_value}")
    plot_pane.object = df_tecnico[data_select.value[0]:data_select.value[1]].hvplot.ohlc('Date', ['Open', 'Low', 'High', 'Close'], grid=True, 
                                                                                         ylabel='Preço (R$)', xlabel='Período', responsive = True, height = 500)

    #Prepara os dados fundamentalistas
    df_fundamentos = df_fund(selected_value)

    ebitda_1 = 0 if df_fundamentos['EV_EBITDA'].iloc[0] == '-'  else df_fundamentos['EV_EBITDA'].iloc[0]
    pvp_1 = 0 if df_fundamentos['PVP'].iloc[0] == '-'  else df_fundamentos['PVP'].iloc[0]
    pl_1 = 0 if df_fundamentos['PL'].iloc[0] == '-'  else df_fundamentos['PL'].iloc[0]
    df_fundamentos['Marg_Liquida'] = df_fundamentos['Marg_Liquida'].str.replace('%', '') 
    df_fundamentos['Div_Yield'] = df_fundamentos['Div_Yield'].str.replace('%', '') 
    margem_liq_1 = 0 if df_fundamentos['Marg_Liquida'].iloc[0] == '-'  else df_fundamentos['Marg_Liquida'].iloc[0]
    dy_1 = 0 if df_fundamentos['Div_Yield'].iloc[0] == '-'  else df_fundamentos['Div_Yield'].iloc[0]
    liq_corr_1 = 0 if df_fundamentos['Liquidez_Corr'].iloc[0] == '-'  else df_fundamentos['Liquidez_Corr'].iloc[0]
    ebitda.value = float(ebitda_1)/100
    pvp.value =float(pvp_1)/100
    pl.value = float(pl_1)/100
    margem_liq.value = float(margem_liq_1)
    dy.value = float(dy_1)
    liq_corr.value = float(liq_corr_1)/100
  




    
    # Prepara os dados para o Trend indicator como DataFrame
    trend_data = pd.DataFrame({
        'Date': df_tecnico.index,
        'Close': df_tecnico['Close'],
        'RSI': df_tecnico['RSI'],
        'ma9': df_tecnico['ma9'],
        'ma20': df_tecnico['ma20'],
        'ma200': df_tecnico['ma200']

    }).reset_index(drop=True)
    
    # Atualiza o Trend Indicator com o DataFrame

    plot_trend.data = trend_data
    ifr.data = trend_data
    ma9.data = trend_data
    ma20.data = trend_data
    mav3.data = trend_data
    plot_trend.visible = True
    ifr.visible = True
    ma9.visible = True
    ma20.visible = True
    mav3.visible = True
    bootstrap_template.main[1] = plot_trend

# Widget de seleção
select = pn.widgets.AutocompleteInput(
    name='Escolha uma ação', 
    options=listagem, 
    case_sensitive=False, 
    search_strategy='includes', 
    min_characters=2, 
    description='Papel'
)
data_select = pn.widgets.DateRangePicker(name = 'Data Análise')

# Pane de gráfico
plot_pane = pn.pane.HoloViews()

# Widget de tendência (Trend Indicator)

plot_trend = pn.indicators.Trend(
    name='Tendência de Fechamento',
    data=pd.DataFrame(),  # Inicialmente vazio, será atualizado pela função
    plot_x='Date',  # Eixo X para o gráfico de tendência
    plot_y='Close',
    plot_type = 'area',  # Eixo Y para o gráfico de tendência
    sizing_mode='stretch_width',
    height=200,
   
    visible=True
    )
mav3 = plot_trend.clone(name='Média móvel 200 dias', data=pd.DataFrame(), plot_y = 'ma200')
ifr = plot_trend.clone(name='Tendência IFR', data=pd.DataFrame(), plot_y = 'RSI')
ma9 = plot_trend.clone(name='Média móvel 9 dias', data=pd.DataFrame(), plot_y = 'ma9')
ma20 = plot_trend.clone(name='Média móvel 20 dias', data=pd.DataFrame(), plot_y = 'ma20')
card1 = pn.Card(plot_trend, collapsible=False, hide_header=True, sizing_mode='stretch_width')
card2 = pn.Card(mav3,collapsible=False, hide_header=True, sizing_mode='stretch_width')
card3 = pn.Card(ifr, collapsible=False, hide_header=True, sizing_mode='stretch_width')
card4 = pn.Card(ma9, collapsible=False, hide_header=True, sizing_mode='stretch_width')
card5 = pn.Card(ma20, collapsible=False, hide_header=True, sizing_mode='stretch_width')

indicadores = pn.Row(card1, card2, card3, card4, card5)


# Widget de fundamentos
pl = pn.indicators.Number(name = 'PL', value = 0, format='{value:,.2f}', font_size='2em', height=50, title_size='1em')
pvp = pn.indicators.Number(name = 'PVP', value = 0, format='{value:,.2f}',font_size='2em', height=50, title_size='1em')
dy = pn.indicators.Number(name = 'DY', value = 0, format='{value:,.2f}%',font_size='2em', height=50, title_size='1em')
ebitda = pn.indicators.Number(name = 'EV/EBITDA', value = 0, format = '{value:,.2f}',font_size='2em', height=50 , title_size='1em')
margem_liq = pn.indicators.Number(name = 'Margem Líquida', value = 0, format='{value:,.2f}',font_size='2em', height=50, title_size='1em')
liq_corr = pn.indicators.Number(name = 'Liquidez Corrente', value = 0, format='{value:,.2f}',font_size='2em', height=50, title_size='1em')
fcard1 = pn.Card(pl, collapsible=False, hide_header=True, sizing_mode='stretch_width')
fcard2 = pn.Card(pvp, collapsible=False, hide_header=True, sizing_mode='stretch_width')
fcard3 = pn.Card(dy, collapsible=False, hide_header=True, sizing_mode='stretch_width')
fcard4 = pn.Card(ebitda, collapsible=False, hide_header=True, sizing_mode='stretch_width')
fcard5 = pn.Card(margem_liq, collapsible=False, hide_header=True, sizing_mode='stretch_width')
fcard6 = pn.Card(liq_corr, collapsible=False, hide_header=True, sizing_mode='stretch_width')

fundamentalistas = pn.Row(fcard1, fcard2, fcard3, fcard4, fcard5, fcard6, height=100)

# Vincular a atualização do gráfico à mudança no select
select.param.watch(update_and_fetch, 'value')

# Atualizar uma vez para inicializar o gráfico e o trend indicator
#update_and_fetch(None)

# Titulos dos indicadores
tecnico_tit = pn.pane.Markdown('## Indicadores Técnicos')
fund_tit = pn.pane.Markdown(
    """ ## Indicadores Fundamentalistas
  --- """)


# Usando o template Bootstrap
bootstrap_template = pn.template.BootstrapTemplate(
    title='Painel de indicadores',
    sidebar=[data_select, select],
    main=[plot_pane, tecnico_tit, indicadores, fund_tit, fundamentalistas]
)

# Exibindo o dashboard
bootstrap_template.servable()

