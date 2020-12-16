import pandas as pd
import numpy as np
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import datetime
import plotly.graph_objects as go
import plotly.express as px
import gunicorn

from collections import defaultdict
from dash.dependencies import Input, Output, State
from datetime import datetime as dt
from jupyter_dash import JupyterDash
from plotly.subplots import make_subplots
from datetime import date
from datetime import datetime

pd.set_option("max_columns", None)
pd.set_option("max_rows", None)
pd.set_option("max_rows", None)
pd.set_option("display.max_columns", None)

df_prod_med = pd.read_csv('./Produtividade_medico.csv', delimiter = ';')
df_prod_med.drop(413, inplace=True)
df_prod_med['Datas'] = pd.to_datetime(df_prod_med['Datas'], format = '%d/%m/%y')
#print(df_prod_med.head())


dt_inicial = df_prod_med['Datas'].head(1)
# print(dt_inicial)

# colocar dinamico no front end
df_prod_med_semanal = df_prod_med.groupby('Dia da semana')[df_prod_med.columns[3:]].mean()
df_prod_med_semanal["new_index"]=['3','4','1','5','2']
df_prod_med_semanal = df_prod_med_semanal.sort_values(by='new_index')
df_prod_med_semanal.reset_index(inplace = True)
df_prod_med_semanal.drop(columns = 'new_index', inplace = True)
df_prod_med_semanal = round(df_prod_med_semanal,2)
df_prod_med_semanal.rename(columns = {'Pacientes novos':'Quantidade de pacientes'}, inplace=True)
#print(df_prod_med_semanal)

df_prod_med_ultima = df_prod_med.tail(1)
df_prod_med_ultima = df_prod_med_ultima[['Datas','Quantidade de pacientes']]
df_prod_med_ultima.reset_index(inplace = True, drop= True)
df_prod_med_ultima['Quantidade de consultas'] = sum(df_prod_med['Quantidade de consultas'])
df_prod_med_ultima['Quantidade de exames solicitados'] = sum(df_prod_med['Quantidade de exames solicitados'])
#print(df_prod_med_ultima)

df_prod_med3 = df_prod_med.tail(1)
dt_final = df_prod_med3['Datas'].values[0]
#print(dt_final)

df_prod_anual = df_prod_med[['Datas','Pacientes novos','Quantidade de consultas','Quantidade de exames solicitados']]
df_prod_anual = pd.DataFrame(df_prod_anual)
df_prod_anual.rename(columns={'Pacientes novos':'Quantidade de pacientes'}, inplace=True)
#print(df_prod_anual.head())

df_atendimentos = pd.read_csv('./df_atendimentos.csv', delimiter = ';')
#print(df_atendimentos)

df_cadastro = pd.read_csv('./informacoescadastraisjosebonifacio.csv', delimiter = ';',na_filter = False, nrows = 1)
#print(df_cadastro)
df_cadastro2 = df_cadastro.copy()
df_cadastro2.drop(columns={"Data de nascimento","Gênero","Etnia"},inplace=True)
df_tabela_cadastro2 = df_cadastro2.T
df_tabela_cadastro2.reset_index(inplace=True)
df_tabela_cadastro2 = df_tabela_cadastro2.astype({"index": str, 0: str})
df_tabela_cadastro2.rename(columns={0:"Respostas"},inplace=True)
df_tabela_cadastro2.rename(columns={"index":"Perguntas"},inplace=True)
df_tabela_cadastro2 =pd.DataFrame(df_tabela_cadastro2)
#print(df_tabela_cadastro2)

app = JupyterDash(__name__, title="PLENI")
server = app.server

app = JupyterDash(
    external_stylesheets=[dbc.themes.LUX],
    meta_tags=[
        {
            "name": "viewport", 
            "content": "width=device-width, initial-scale=1"
         }
    ],
     title="PLENI",
)


#-----------------------------------------SEARCH BAR ------------------------------------------------------------------------

# make a reuseable navitem for the different examples
nav_pacientes = dbc.NavItem(dbc.NavLink('Pacientes',id='id_pacientes' , href="/Pacientes"))
nav_protocolos = dbc.NavItem(dbc.NavLink('Protocolos',id='id_protocolos' , href="/Protocolos"))
nav_agendamentos = dbc.NavItem(dbc.NavLink('Agendamentos',id='id_agendamentos' , href="/Agendamentos"))

# make a reuseable dropdown for the different examples
dropdown = dbc.DropdownMenu(
    children=[
              html.Div([
                        dbc.DropdownMenuItem("Alterações cadastrais", id='id_altera_cadast'),
                        dbc.Modal(
            [
                dbc.ModalHeader("Alterações cadastrais"),
                dbc.ModalBody(
                    dbc.Form(
                        [
                            dbc.FormGroup(
                                [
                                    dbc.Label("Nome completo", className="mr-2"),
                                    dbc.Input(type="text", placeholder=""f"{df_cadastro.iloc[0,0]}",id='nome_preenchido'),
                                ],
                                className="mr-3",
                            ),
                            dbc.FormGroup(
                                [
                                    dbc.Label("Data de nascimento", className="mr-2"),
                                    dbc.Input(type="text", placeholder=""f"{df_cadastro.iloc[0,1]}",id='dn_preenchido'),
                                ],
                                className="mr-3",
                            ),
                            dbc.FormGroup(
                                [
                                    dbc.Label("Bairro de residência", className="mr-2"),
                                    dbc.Input(type="text", placeholder=""f"{df_cadastro.iloc[0,2]}",id='bairro_preenchido'),
                                ],
                                className="mr-3",
                            ),
                            dbc.FormGroup(
                                [
                                    dbc.Label("Email", className="mr-2"),
                                    dbc.Input(type="text", placeholder=""f"{df_cadastro.iloc[0,3]}",id='email_preenchido'),
                                ],
                                className="mr-3",
                            ),
                            dbc.FormGroup(
                                [
                                    dbc.Label("Profissão", className="mr-2"),
                                    dbc.Input(type="text", placeholder=""f"{df_cadastro.iloc[0,4]}",id='profissao_preenchido'),
                                ],
                                className="mr-3",
                            ),
                            dbc.FormGroup(
                                [
                                    dbc.Label("Especialidade", className="mr-2"),
                                    dbc.Input(type="text", placeholder=""f"{df_cadastro.iloc[0,5]}",id='especialidade_preenchido'),
                                ],
                                className="mr-3",
                            ),
                            dbc.FormGroup(
                                [
                                    dbc.Label("Conselho", className="mr-2"),
                                    dbc.Input(type="text", placeholder=""f"{df_cadastro.iloc[0,6]}",id='conselho_preenchido'),
                                ],
                                className="mr-3",
                            ),
                            dbc.FormGroup(
                                [
                                    dbc.Label("Registro", className="mr-2"),
                                    dbc.Input(type="text", placeholder=""f"{df_cadastro.iloc[0,7]}",id='registro_preenchido'),
                                ],
                                className="mr-3",
                            ),
                            dbc.FormGroup(
                                [
                                    dbc.Label("Nome da equipe", className="mr-2"),
                                    dbc.Input(type="text", placeholder=""f"{df_cadastro.iloc[0,8]}",id='nequipe_preenchido'),
                                ],
                                className="mr-3",
                            ),
                            dbc.FormGroup(
                                [
                                    dbc.Label("Gênero", className="mr-2"),
                                    dbc.Input(type="text", placeholder=""f"{df_cadastro.iloc[0,9]}",id='genero_preenchido'),
                                ],
                                className="mr-3",
                            ),
                            dbc.FormGroup(
                                [
                                    dbc.Label("Etnia", className="mr-2"),
                                    dbc.Input(type="text",placeholder=""f"{df_cadastro.iloc[0,10]}",id='etnia_preenchido'),
                                ],
                                className="mr-3",
                            ),

                            dbc.Button("Salvar", color="#38a3a5", id="button_salvar_cadastro"),
                        ],
                        inline=False,
                    )
                ),
                dbc.ModalFooter(
                    dbc.Button("Fechar", id="close_alteracoes", className="ml-auto")
                ),
            ],
            id="modal_alteracoes",
            is_open=False,
            size="x1",
            backdrop=True,
            scrollable=True,
            centered=True,
            fade=True
        ),
        ]
        ),
        html.Div(
    [
        dbc.DropdownMenuItem("Sugestões de melhoria", id='id_sugst_melh'),
        dbc.Modal(
            [
                dbc.ModalHeader("Conte-nos como poderíamos melhorar!"),
                dbc.ModalBody(
                    dbc.Form(
                        [
                            dbc.FormGroup(
                                [
                                    dbc.Label("Nome Completo", className="mr-2"),
                                    dbc.Input(type="text", placeholder="Informe seu nome completo"),
                                ],
                                className="mr-3",
                            ),

                            dbc.FormGroup(
                                [
                                    dbc.Label("Email", className="mr-2"),
                                    dbc.Input(type="text", placeholder="Informe seu email"),
                                ],
                                className="mr-3",
                            ),

                            dbc.FormGroup(
                                [
                                    dbc.Label("Melhoria protosta", className="mr-2"),
                                    dbc.Input(type="text", placeholder="Descreva"),
                                ],
                                className="mr-3",
                            ),

                            dbc.Button("Enviar", color="#38a3a5"),
                        ],
                        inline=False,
                    )
                ),
                dbc.ModalFooter(
                    dbc.Button("Fechar", id="close_feedback", className="ml-auto")
                ),
            ],
            id="modal_feedback",
            is_open=False,
            size="x1",
            backdrop=True,
            scrollable=True,
            centered=True,
            fade=True
        ),
    ]
    ),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Logout", id= 'id_logout'),

    ],
    nav=True,
    in_navbar=True,
    label="Opções",
)


# this example that adds a logo to the navbar brand
logo = dbc.Navbar(
    dbc.Container(
        [
            #html.A(
            #    # Use row and col to control vertical alignment of logo / brand
            #    dbc.Row(
            #        [
            #            dbc.Col(
            #                html.Img(
            #                    src="/assets/logo_medme.png", 
            #                    height="45px", 
            #                    #style={"offset": -2},
            #                    ),                                
            #                ),
            #        ],
            #        align="center",
            #        justify="start",
            #        no_gutters=True,
            #    ),
            #    #href="https://plot.ly",
            #),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                dbc.Nav(
                    [
                        nav_protocolos, 
                        nav_pacientes,
                        nav_agendamentos,
                        dropdown
                      ], 
                      className="ml-auto", 
                      navbar=True,
                      horizontal=True,                      
                ),
                id="navbar-collapse",
                navbar=True,
            ),
        ]
    ),
    dark=True,
    className="mb-1",
    #light=True
)

#--------------------Modals ----------------------------------------------------------------------------------
#--------------------------------------SIDEBAR -----------------------------------------------------------------------------
#-----------------------------------------CARDS --------------------------------------------------------------------------------
first_card = dbc.Card(
    html.Img(
                src="/assets/medico2.png", 
                className="rounded-circle",
                height="360px", 
                ),
                color="light",
                style={'textAlign': 'center','border': '0px'}
)

second_card = dbc.Card(
    dbc.CardBody(
        [
            html.H1("Bem vindo à"),
            html.Img(
                src="/assets/logo_pleni.png", 
                #height="360px", 
                width="480px"
                ),
            html.H1(""f"{df_cadastro.iloc[0,0]}"),#children={},id="nome_medico"),
        ],
        style={'textAlign': 'center', 'border': '0px'}
    ),
    style={"border":'0px'}
)

tabela_cadastral = dash_table.DataTable(
    id="id_tabela_cadastral",
    columns=[{'id': c, 'name': "Informações Cadastrais"} for c in df_tabela_cadastro2.columns],
    data=df_tabela_cadastro2.to_dict('records'),
    merge_duplicate_headers=True,
    style_cell={'textAlign': 'center'},
    selected_cells=[],
    style_cell_conditional=[
                          {
                              'if': {'column_id': c},
                              'textAlign': 'center'                              
                          } for c in df_atendimentos.columns
                      ],
                      style_data_conditional=[
                          {                            
                              'if': {'row_index': 'odd'},
                              'backgroundColor': 'rgb(237, 245, 253)',
                              'textAlign': 'center'
                          },
                          { 
                              "if": {"state": "selected"},              # 'active' | 'selected'
                              "backgroundColor": "rgba(0, 116, 217, 0.3)",
                              "border": "1px solid blue",   
                              'textAlign': 'center' 
                          },
                      ],
                      style_header={
                          'backgroundColor': 'rgb(221, 239, 248)',
                          'fontWeight': 'bold'
                      },
)

tabela_atendimentos = dash_table.DataTable(
    id="id_tabela_atendimentos",
    columns=[
             
             {'id': 'Unidades', 'name': 'Unidades', 'presentation': 'dropdown'},
             {'id': 'Dias da Semana', 'name': 'Dias da Semana', 'presentation': 'dropdown'},
             {'id':'Horários','name':'Horários'},
             {'id':'Qtd. de consultas','name':'Qtd. de consultas', 'presentation': 'dropdown'}
             ],
    data=pd.read_csv('./df_atendimentos.csv',delimiter = ';').to_dict('records'),
    merge_duplicate_headers=True,
    style_cell={'textAlign': 'center'},
    filter_action="native",
    sort_action="native",
    editable=True,
    row_deletable=True,
    style_table={'marginBottom':5},
    selected_cells=[],
    page_size=6,
    style_cell_conditional=[
                          {
                              'if': {'column_id': c},
                              'textAlign': 'center'                              
                          } for c in df_atendimentos.columns
                      ],
                      style_data_conditional=[
                          {                            
                              'if': {'row_index': 'odd'},
                              'backgroundColor': 'rgb(237, 245, 253)',
                              'textAlign': 'center'
                          },
                          { 
                              "if": {"state": "selected"},              # 'active' | 'selected'
                              "backgroundColor": "rgba(0, 116, 217, 0.3)",
                              "border": "1px solid blue",   
                              'textAlign': 'center' 
                          },
                      ],
                      style_header={
                          'backgroundColor': 'rgb(221, 239, 248)',
                          'fontWeight': 'bold'
                      },
                      dropdown={
                      'Unidades': {
                          'options': [
                              {'label': i, 'value': i}
                              for i in df_atendimentos['Unidades'].unique()
                          ]
                      },
                      'Dias da Semana': {
                          'options': [
                            {'label': i, 'value': i}
                            for i in [
                                      'Segunda-Feira',
                                      'Terça-Feira',  
                                      'Quarta-Feira', 
                                      'Quinta-Feira', 
                                      'Sexta-Feira',  
                            ]
                        ] 
                      }
        },
    data_previous=pd.read_csv('./df_atendimentos.csv', delimiter = ';').to_dict('records'),
    page_action='native',
    persistence=True,
    persisted_props=['columns.name', 'data','filter_query', 'hidden_columns', 'selected_columns', 'selected_rows', 'sort_by'],
    persistence_type='local',
)

cards_1 = dbc.Row(
    [
     dbc.Col(
         first_card, 
         width=3, 
         style={'marginLeft':5}
         ), 
     dbc.Col(
         second_card, 
         width=8,
         style={'marginLeft':-20, 'marginTop':20} 
         )
     ],
     justify="center",
     className="mb-1",
)

cards_2 = dbc.Row(
    [
     dbc.Col(
         tabela_cadastral, 
         width=5, 
         style={'marginRight':1,'marginLeft':-120}
         ), 
     dbc.Col(
         [
            tabela_atendimentos,
          dbc.Row(
              [
                  dbc.Button(
                      'Adicionar Nova Linha', 
                       id='editing-rows-button', 
                       n_clicks=0,
                       style={'marginRight':1},
                       outline=True,
                       color='blue',
                       size='sm'
                         ),
                  dbc.Button(
                      'Salvar', 
                       id='salvar-rows-button',
                       n_clicks=0, 
                       outline=True, 
                       color="blue",
                       size='sm'
                         ),
               html.P(id='save-button-hidden', style={'display':'none'}),
              ]
          )
            
         ],
         width=5, 
         style={'marginLeft':1}
         )
     ],
     justify="center",
     className="mb-1",
)

card_3 = dbc.Card(
              dbc.CardBody(
                  [
                       
                   dbc.Row(
                       [
                       dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                     html.H1("Análise histórica"),
                                    dcc.Dropdown(
                                        id="dropdown_prod_indicador",
                                        options=[
                                            {"label": indicador, "value": indicador}
                                            for indicador in df_prod_anual.columns[1:8]
                                        ],
                                        value="Quantidade de pacientes",
                                        className='mb-3'
                                        ),
                                    dcc.Dropdown(
                                          id="dropdown_prod_tempo",
                                          options=[
                                              {"label": 'Dias de semana (média)', "value": 'Dias de semana (média)'},
                                              {"label": 'Tempo corrido', "value": 'Tempo corrido'}                        
                                          ],
                                          value='Tempo corrido',
                                          ), 
                                    ]
                                ),
                                style={"border":'0px'}
                            ),
                            width=8,  
                       ),
                        dbc.Col(
                            [
                             dbc.Row(
                                 dbc.Card(
                                [
                                    dbc.CardHeader(children={}, id='header_cart_medico'),
                                    dbc.CardBody(
                                        [
                                            html.H1(
                                                children={},
                                                id='cartao_total_medico',
                                                style={'color':'White'},
                                            ),
                                         dbc.Row(
                                             [
                                             dbc.Col(
                                                 html.H5(
                                                     children={},#"Primeiro atendimento: "f"{dt_inicial}",
                                                     id='id_dt_primeiro_atendimento',
                                                     style={'color':'White','fontSize':10,'marginBottom':0,' marginRight':30},
                                                 ),
                                             ),
                                              dbc.Col(html.H5(
                                                     children={},
                                                     id='id_dt_ultimo_atendimento',
                                                     style={'color':'White','marginBottom':0,'fontSize':10},
                                              ),
                                             ),
                                             ],
                                         ) 
                                        ]
                                    ),
                                ],
                                color="info",
                                inverse=True,
                                style={'textAlign': 'center','marginLeft':-10,'marginBottom':10},
                                
                                ),
                                justify='center'
                             ),
                             dbc.Row(
                                 dcc.DatePickerRange(
                                        end_date=df_prod_med_ultima.at[0,'Datas'],
                                        start_date=df_prod_med.at[0,'Datas'],
                                        display_format='DD/MM/YY',
                                        start_date_placeholder_text='DD/MM/YY',
                                        id='datepickerrange_id'
                                    ),
                                      justify="center",
                             className="mb-2",
                             style={'textAlign': 'center', 'border': '0px'}
                                     
                             )
                            ],
                             width=4,
                        )
                       ]
                   ),
                    dcc.Graph(
                        id="grafico_produtividade_medico",
                        figure={},
                    )
                  ]
              ),
              style={"marginLeft": 0,"border":'0px'},
              className="w-95, mb-2",
)
                    
            

# fig_medicamento
content_home = html.Div(
    [
         logo,
         cards_1,
         cards_2,
         card_3           
      ],
    id="home-content",
    )

#---------------------------Modals-------------------------------------------------------------------------------------------------
#---------------------------LAYOUT ------------------------------------------------------------------------------------------

app.layout = html.Div(
    children=content_home,
    id="id_layout",
)

#----------------------------------------------------------------------------------------------------------------------------
# ****************Callbacks **************************************************************************************************

def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# the same function (toggle_navbar_collapse) is used in all three callbacks
    app.callback(
        Output(f"navbar-collapse", "is_open"),
        [Input(f"navbar-toggler", "n_clicks")],
        [State(f"navbar-collapse", "is_open")],
    )(toggle_navbar_collapse)


### add rows table
@app.callback(
    Output('id_tabela_atendimentos', 'data'),
    [Input('editing-rows-button', 'n_clicks')],
    [State('id_tabela_atendimentos', 'data'),
     State('id_tabela_atendimentos', 'columns')])
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows


########## Gráfico médico page home
@app.callback(
    Output("grafico_produtividade_medico", "figure"),
    [
     Input("dropdown_prod_indicador", "value"),
     Input("dropdown_prod_tempo", "value"),
     Input("datepickerrange_id","end_date"),
     Input("datepickerrange_id","start_date")
    ]  
)
def plotar_forecast(variavel,dropdown_prod_tempo,data_final,data_inicial):
    if dropdown_prod_tempo == "Dias de semana (média)":
       dff = df_prod_med.copy()
       dff = dff.loc[(dff['Datas'] >= data_inicial) & (dff['Datas'] <= data_final)]
       dff = dff.groupby('Dia da semana')[dff.columns[3:]].mean()
       dff["new_index"]=['3','4','1','5','2']
       dff = dff.sort_values(by='new_index')
       dff.reset_index(inplace = True)
       dff.drop(columns = 'new_index', inplace = True)
       dff = round(dff,2)
       dff.rename(columns = {'Pacientes novos':'Quantidade de pacientes'}, inplace=True)
       graf_prod = go.Figure()
       graf_prod.add_traces(
           go.Bar(
               x=dff['Dia da semana'], 
               y=dff[variavel], 
               showlegend=True,
               name=variavel,
               text=dff[variavel],
               textposition='auto',
           )
       )
       graf_prod.update_layout(
           paper_bgcolor='rgba(255,255,255,255)',
           plot_bgcolor='rgba(255,255,255,255)',
           legend = dict(
               orientation="h",
               yanchor="bottom",
               y=1.03,
               xanchor="right",
               x=0.93,         
               ),
               margin=dict(l=10, r=20, t=70, b=10),
            )
       graf_prod.update_traces(
           marker_color='rgb(158,202,225)', 
           marker_line_color='rgb(8,48,107)',
           marker_line_width=1.5, opacity=0.6
           )
       return graf_prod
    else:
      dff = df_prod_anual.copy()
      dff = dff.loc[(dff['Datas'] >= data_inicial) & (dff['Datas'] <= data_final)]
      graf_prod = go.Figure()
      graf_prod.add_traces(
          go.Scatter(
              x=dff['Datas'], 
              y=dff[variavel], 
              mode="lines", 
              showlegend=True,
              name=variavel,
              #name="Previsão", 
              #line={"color": "#03045e"}
        )
      )
      graf_prod.update_layout(
          xaxis_rangeslider_visible=True,
          paper_bgcolor='rgba(255,255,255,255)',
          plot_bgcolor='rgba(255,255,255,255)',
          legend = dict(
              orientation="h",
              yanchor="bottom",
              y=1.03,
              xanchor="right",
              x=0.93,         
              ),
              margin=dict(l=10, r=20, t=70, b=10),
              )
      return graf_prod

########## Cartão médico page home
  ############### Título

@app.callback(
    Output("header_cart_medico", "children"),
    Input("dropdown_prod_indicador", "value"),
)
def retorno_titulo(variavel):
  variavel= str(variavel)+" | Total"
  return variavel

@app.callback(
    Output("id_dt_primeiro_atendimento", "children"),
    Input("datepickerrange_id", "start_date"),
)
def retorno_primeiro_atendimento(variavel):
  dff = str(variavel)
  dff =dff[:10]
  parts = dff.split('-')
  dff = parts[2] + '/' + parts[1] + '/' + parts[0]
  dff = str(dff)
  dff = "De: "f"{dff}",
  return dff

@app.callback(
    Output("id_dt_ultimo_atendimento", "children"),
    Input("datepickerrange_id", "end_date"),
)
def retorno_ultimo_atendimento(variavel):
  dff = str(variavel)
  dff =dff[:10]
  parts = dff.split('-')
  dff = parts[2] + '/' + parts[1] + '/' + parts[0]
  dff = str(dff)
  dff = "Até: "f"{dff}",
  return dff

@app.callback(
    Output("cartao_total_medico", "children"),
    [
     Input("dropdown_prod_indicador", "value"),
     Input("datepickerrange_id","end_date"),
     Input("datepickerrange_id","start_date")
    ]    
)
def retorno_corpo(variavel,data_final,data_inicial):
  dff = df_prod_anual.copy()
  dff = dff.loc[(dff['Datas'] >= data_inicial) & (dff['Datas'] <= data_final)]
  dff = dff[variavel].sum()
  return dff

###### Botao Salvar

#@app.callback(
#    Output('save-button-hidden', 'children'), 
#    [Input('salvar-rows-button', 'n_clicks'),
#     Input('id_tabela_atendimentos','data')],
#     )
#def clicks(n_clicks,data):
#    if n_clicks > 0:
#        data = pd.DataFrame(data)
#        data.to_excel('/content/drive/My Drive/df_atendimentos/df_atendimentos.xlsx', sheet_name='Atendimentos', index=False)
#        data.to_excel('df_atendimentos.xlsx', sheet_name='Atendimentos', index=False)
        #files.download('df_atendimentos.xlsx')

####modal alteracoes
# modal_alteracoes
@app.callback(
    Output("modal_alteracoes", "is_open"),
    [
        Input("id_altera_cadast", "n_clicks"),
        Input("close_alteracoes", "n_clicks")
    ], 
    [State("modal_alteracoes", "is_open")]
)
def toggle_modal(n1, n2, is_open):
    """
    Watches over the State of the open and close buttons
    and decides wether to open or close the the modal 
    """
    if n1 or n2: # if there's an n1 or an n2, equivalent to saying any button is clicked
        return not is_open # makes is_open equals to True, since it is False by default
    return is_open # no button is clicked, nothing happens (is_open remains False)


contend_protocolos = html.Div(
    [
         logo,
    ],
    id="protocolos-content",
)

#### modal melhorias
# modal_feedback
@app.callback(
    Output("modal_feedback", "is_open"),
    [
        Input("id_sugst_melh", "n_clicks"),
        Input("close_feedback", "n_clicks")
    ], 
    [State("modal_feedback", "is_open")]
)
def toggle_modal(n1, n2, is_open):
    """
    Watches over the State of the open and close buttons
    and decides wether to open or close the the modal 
    """
    if n1 or n2: # if there's an n1 or an n2, equivalent to saying any button is clicked
        return not is_open # makes is_open equals to True, since it is False by default
    return is_open # no button is clicked, nothing happens (is_open remains False)

if __name__ == "__main__":
  app.run_server(port=6060, debug=True)#mode="inline")

