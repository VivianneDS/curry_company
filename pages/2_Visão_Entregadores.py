#Libraries
import pandas as pd
import plotly.express as px
from haversine import haversine, Unit
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão_Entregadores',layout='wide')

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

def top_delivers(df1, top_asc):
    df_aux = df1.loc[:,['Delivery_person_ID','Time_taken(min)', 'City']].groupby(['City','Delivery_person_ID']).mean().sort_values('Time_taken(min)', ascending=top_asc).reset_index()

    df_aux01 = df_aux.loc[df_aux['City'] == 'Semi-Urban', :].head(10)
    df_aux02 = df_aux.loc[df_aux['City'] == 'Metropolitian', :].head(10)
    df_aux03 = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)

    df_aux04 = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index(drop = True)

    return df_aux04

def rating_std_mean (df1 , col):

    df_traffic = ( df1[["Delivery_person_Ratings", col]]
               .groupby([col])
               .agg(['mean', 'std']).reset_index() )

    #mudança de nome de coluna
    df_traffic.columns = ['Road_traffic_density' , 'Delivery_mean', 'Delivery_std' ]

    return df_traffic


# ---------------------------------------- Inicio da estrutura lógica do código ------------------------------------------
# ----------------------------------
#importando dataset
#----------------------------------

df = pd.read_csv('train.csv')

df1 = df.copy()

#Limpando dataset
df1 = clean_code(df1)

#=========================================================
#BARRA LATERAL
#========================================================
st.header('Marketplace - Visão Entregadores')


image = Image.open( 'foguetinho.png' )
st.sidebar.image( image , width=120 )

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('### Selecione uma data limite')
dataslider = st.sidebar.slider(
    'Data Limite',
    value=pd.datetime( 2022, 4, 23 ),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD/MM/YYYY')


st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
    'Condições do trânsito',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'])

weatherconditioons = st.sidebar.multiselect(
    'Condições climáticas',
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
        st.title('Métricas')
        col1,col2,col3,col4 = st.columns(4,gap='large')
        with col1:
            #A maior idade dos entregadores
            maior_idade = df1.loc[:,"Delivery_person_Age"].max()
            col1.metric('Maior de idade', maior_idade)
            
        with col2:
            #A menor idade dos entregadores
            menor_idade = df1.loc[:,"Delivery_person_Age"].min()
            col2.metric('Menor de idade', menor_idade)

        with col3:
            #A melgor condição de veículos
            melhor_condicao = df1.loc[:,"Vehicle_condition"].max()
            col3.metric('Melhor condição', melhor_condicao)
            
        with col4:
            #A pior condição de veiculos
            pior_condicao = df1.loc[:,"Vehicle_condition"].min()
            col4.metric('Pior condição', pior_condicao)
            
            
    with st.container():
        st.markdown("""___""")
        st.title('Avaliações')
        col1,col2 = st.columns([5,5])
        
        with col1:
            #Tabela de Avaliações medias por Entregador
            st.markdown("###### Avaliações médias por Entregador")

            df_avg_rating_per_deliver= df1[["Delivery_person_Ratings", "Delivery_person_ID"]].groupby(["Delivery_person_ID"]).mean().reset_index()
            st.dataframe(  df_avg_rating_per_deliver )
            
        with col2:
            # Tabela Avaliação média por Trânsito
            st.markdown('###### Avaliação média por Trânsito')
            df_traffic = rating_std_mean(df1, col = 'Road_traffic_density')
            st.dataframe(df_traffic)
    
            
            #--------------------------------------------------------------------------
            
            # Avaliação média por Clima
            st.markdown('###### Avaliação média por Clima')
            df_weatherconditions = rating_std_mean(df1, col = 'Weatherconditions')
            st.dataframe(df_weatherconditions)
     
            
    with st.container():
        st.markdown("""___""")
        st.title('Velocidade de entrega')
        col1,col2 = st.columns(2)
        
        with col1:
            st.markdown( '###### Top entregadores mais rápidos')
            df_aux04 = top_delivers(df1, top_asc=True)
            st.dataframe(df_aux04)
        
        with col2:
            st.markdown( '###### Top entregadores mais lentos')
            df_aux04 = top_delivers(df1, top_asc=False)
            st.dataframe(df_aux04)
           
            

            
        