#Libraries
import pandas as pd
import plotly.express as px
from haversine import haversine, Unit
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
import numpy as np

st.set_page_config(page_title='Visão Restaurantes',layout='wide')

#--------------------------
#Funções
#--------------------------

# Função de Limpeza
def clean_code(df1):
    
    """ Esta função tem a responsabilidade de limpar o datframe
        Tipos de limpeza:
        1 - Remoção dos dados NaN
        2 - Mudança do tipo da coluna de dadois
        3 - Remoção dos espaços das variáveis de texto
        4 - Formatação da data
        5 - Limapeza da coluna de tempo (remoção do texto da variável numérica 
        
        Input : Dataframe
        Output: Dataframe
    """
    
    #Retirando linhas vazias
    linhas_vazias = df1['Delivery_person_ID'] != 'NaN'
    df1 = df1.loc[linhas_vazias, : ]

    linhas_vazias2 = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias2, :]

    linhas_vazias3 = df1['Delivery_person_Ratings'] != 'NaN '
    df1 = df1.loc[linhas_vazias3, :]

    linhas_vazias = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]

    linhas_vazias = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]


    linhas_vazias = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]

    #Convertendo os tipos das colunas de object para num/float
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    #Covetendo string para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y' )

    #Retirando espaços finais da coluns sem usar o for
    df1.loc[ : , 'ID'] = df1.loc[ : , 'ID'].str.strip()
    df1.loc[ : , 'Type_of_order'] = df1.loc[ : , 'Type_of_order'].str.strip()
    df1.loc[ : , 'City'] = df1.loc[ : , 'City'].str.strip()
    df1.loc[ : , 'Type_of_vehicle'] = df1.loc[ : , 'Type_of_vehicle'].str.strip()
    df1.loc[ : , 'Road_traffic_density'] = df1.loc[ : , 'Road_traffic_density'].str.strip()
    df1.loc[ : , 'Delivery_person_ID'] = df1.loc[ : , 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:,'Festival'].str.strip()

    # Limpando a coluna de time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )

    return df1

def distace_restaurant_order(df1, fig):
    if fig == False:

        cols = [ 'Restaurant_latitude' , 'Restaurant_longitude' , 'Delivery_location_latitude', 'Delivery_location_longitude']

        df1['Distance(Km)'] = df1.loc[:, cols].apply( lambda x : haversine( (x['Restaurant_latitude'], x['Restaurant_longitude'] ), (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis = 1)
        avg_distancia = np.round(df1['Distance(Km)'].mean(),2)
        
        return avg_distancia
        
    else:
        
        cols = [ 'Restaurant_latitude' , 'Restaurant_longitude' , 'Delivery_location_latitude', 'Delivery_location_longitude']

        df1['Distance(Km)'] = df1.loc[:, cols].apply( lambda x : haversine( (x['Restaurant_latitude'], x['Restaurant_longitude'] ), (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis = 1)
        avg_distancia = df1.loc[:,['City','Distance(Km)']].groupby(['City']).mean().reset_index()

        fig = go.Figure(data=[go.Pie(labels=avg_distancia['City'], values=avg_distancia['Distance(Km)'], pull=[0,0.1,0])])
        
        return fig

        

            
def avg_std_time_delivery(df1, festival ,op):
    
    """
       Essa função calcula o tempo médio e o desvio de padrão do tempo de entrega
       Parâmetros:
            Input:
                df : DataFrame
                op: Tipo de operação a ser calculada
                    'avg_time' - calcula tempo medio
                    'std_time' - calcula desvio padrão do tempo médio
                festival: Se está ou não ocorrendo festival na cidade
                    'Yes' - sim
                    'No' - não
            Output:
                df: datagrame com duas colunas e uma linha
    """
    df_aux = (df1.loc[:,[ 'Time_taken(min)','Festival']]
                 .groupby(['Festival'])
                 .agg(['mean','std'])
                 .reset_index())
    df_aux.columns = ['Festival', 'avg_time','std_time']
    linha = df_aux['Festival'] == festival
    df_aux = np.round(df_aux.loc[linha, op],2)


    return df_aux

def avg_std_time_graph(df1):

    cols = [ 'Time_taken(min)', 'City']
    df_aux = df1.loc[:,cols].groupby(['City']).agg(['mean','std']).reset_index()
    df_aux.columns = ['City', 'avg_time','std_time']

        #grafico de intervalos (barras com intervalo de std)

    fig = go.Figure()

    fig.add_trace(go.Bar( name = 'Control',x=df_aux['City'],y=df_aux['avg_time'],error_y=dict(type='data', array=df_aux['std_time'])))

    fig.update_layout(barmode='group',xaxis_showgrid=False, yaxis_showgrid=False,yaxis_range=[0,60])

    return fig

def avg_std_time_traffic(df1):
    cols = ['Time_taken(min)','City','Road_traffic_density']
    df_aux = df1.loc[:,cols].groupby(['City','Road_traffic_density']).agg(['mean','std']).reset_index()
    df_aux.columns = ['City', 'Road_traffic_density', 'avg_time','std_time']

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',color='std_time',color_continuous_scale='blues',color_continuous_midpoint=np.average(df_aux['std_time']))

    return fig




#importando dataset
#----------------------------------

df = pd.read_csv('train.csv')

#Limpando dados
df1 = df.copy()
df1 = clean_code(df1)


#=========================================================
#BARRA LATERAL
#========================================================
st.header('Marketplace - Visão Restaurante')

image = Image.open( 'foguetinho.png' )
st.sidebar.image( image , width=120 )

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('### Selecione uma data limite')
dataslider = st.sidebar.slider(
    'Até qual valor',
    value=pd.datetime( 2022, 4, 23 ),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD/MM/YYYY')


st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'])

weatherconditioons = st.sidebar.multiselect(
    'Quais as condições climáticas',
    ['conditions Cloudy','conditions Fog','conditions Sandstorms','conditions Stormy','conditions Sunny','conditions Windy'],
    default=['conditions Cloudy','conditions Fog','conditions Sandstorms','conditions Stormy','conditions Sunny','conditions Windy'])

st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered by Comunidade DS')

#filtro de data
linhas_selecionadas = df1['Order_Date'] < dataslider
df1 = df1.loc[linhas_selecionadas,:]

#filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)#está em
df1 = df1.loc[linhas_selecionadas,:]

#filtro de condições climáticas
linhas_selecionadas = df1['Weatherconditions'].isin(weatherconditioons)
df1 = df1.loc[linhas_selecionadas,:]
#=========================================================
#LAYOUT SREAMLIT
#========================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title( 'Métricas')
        
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        with col1:
            #Número de Entregadores
            delivery_unique = df1.loc[:,"Delivery_person_ID"].nunique()
            col1.metric('Entregadores', delivery_unique)
            
        with col2:
            #CALCULAR A DISTANCIA ENTRE OS PEDIDOS ENTREGUES E OS RESTAURANTES
            avg_distancia = distace_restaurant_order(df1, fig=False)
            col2.metric('Distância Média', avg_distancia)

            
        with col3:
            #Tempo médio gasto nas entregas durante o festival
            df_aux = avg_std_time_delivery(df1,'Yes','avg_time')
            col3.metric( 'T.Médio de Entrega Festival', df_aux)

        with col4:
            #Desvio padrão médio do tempo gasto nas entregas durante o festival
            df_aux = avg_std_time_delivery(df1,'Yes','std_time')
            col4.metric( 'Desv.Padrão Entrega Festival', df_aux)

        with col5:
            #Tempo médio gasto nas entregas sem festival
            df_aux = avg_std_time_delivery(df1,'No','avg_time')
            col5.metric( 'Tempo Médio Entrega', df_aux)
            
        with col6:
            #Desvio padrão médio gasto nas entregas sem festival
            df_aux = avg_std_time_delivery(df1,'No','std_time')
            col6.metric( 'Desvio Padrão Entrega', df_aux)

            
            
        
    with st.container():
        
        st.markdown("""___""")
        st.title('Tempo e Distâncias')
        col1,col2 = st.columns([3,2])
        
        with col1:
            #O tempo médio e o desvio padrão de entrega por cidade e tipo de pedido - TABELA
            st.markdown('#### O tempo médio e o desvio padrão de entrega por cidade e tipo de pedido')
            cols = [ 'Time_taken(min)', 'City', 'Type_of_order' ]
            df_aux = df1.loc[:,cols].groupby(['City','Type_of_order']).agg(['mean','std']).reset_index()
            df_aux.columns = ['City', 'Type_of_order', 'avg_time','std_time']
            st.dataframe( df_aux )
            
        
        with col2:
            #A distância média dos resturantes e dos locais de entrega - GRAFICO DE BARRA COM DESVIO PADRÃO
            st.markdown('#### A distância média dos resturantes e dos locais de entrega')
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig, use_container_width=True)
                    
        
        
    with st.container():
        st.markdown("""___""")
        st.title('Distribuição do Tempo')
        
        col1, col2 = st.columns([2,2])
        
        with col1:
            #A distância média dos restaurantes até e os clientes - grafico de setores
            st.markdown('#### A distância média dos restaurantes até e os clientes')
            fig = distace_restaurant_order(df1, fig=True)
            st.plotly_chart( fig, use_container_width=True )
            
            
        with col2:
            #O tempo médio e o desvio padrão de entrega por cidade - grafico de raio de sol
            st.markdown('#### O tempo médio e o desvio padrão de entrega por cidade')
            
            fig = avg_std_time_traffic(df1)

            st.plotly_chart(fig, use_container_width=True)



    
    