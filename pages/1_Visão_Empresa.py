#Libraries
import pandas as pd
import plotly.express as px
from haversine import haversine, Unit
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa',layout='wide')
#importação do útils - clean_code
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


def order_metric(df1):
    #Order Metric
    #grafico de pedidos por dia
    df_aux = df1[['ID','Order_Date']].groupby(['Order_Date']).count().reset_index()
    df_aux.columns = ['Day', 'Orders']
    #Criando gráfico de barras
    fig = px.bar(df_aux,x='Day',y='Orders').update_layout(xaxis_showgrid=False, yaxis_showgrid=False)
            
    return fig


def traffic_order_share(df1):
    df_aux = df1[['ID','Road_traffic_density']].groupby(['Road_traffic_density']).count().reset_index() 
    df_aux['Porcentagem_entrega(%)'] = round((df_aux['ID']/df_aux['ID'].sum())*100,2)

    #Grafico de pizza

    fig = px.pie( df_aux, values='Porcentagem_entrega(%)', names='Road_traffic_density')
                
    return fig

def traffic_order_city(df1):
    df_aux = df1[['ID','City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
    df_aux.columns = ['City', 'Traffic Density', 'ID']

    fig =  px.scatter( df_aux, x='City', y='Traffic Density', size='ID', color='City').update_layout(xaxis_showgrid=False, yaxis_showgrid=False)
            
    return fig

def order_by_week(df1):
    #criar a coluna semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1[['ID','week_of_year']].groupby(['week_of_year']).count().reset_index()
    df_aux.columns = ['Week of Year', 'Orders']
    fig = px.line( df_aux, x='Week of Year', y='Orders').update_layout(xaxis_showgrid=False, yaxis_showgrid=False)
    fig.update_xaxes(range=[6, 15])
    return fig

def order_share_by_week(df1):
    #Quantidade de pedidos por semana / numero de entregadores unicos por semana
    df_aux01 = df1[['ID','week_of_year']].groupby(['week_of_year']).count().reset_index()
    df_aux02 = df1[['Delivery_person_ID','week_of_year']].groupby(['week_of_year']).nunique().reset_index()

    #juntar dois dataframes

    df_aux = pd.merge( df_aux01, df_aux02, how='inner')
    df_aux['order_by_delivery'] = round(df_aux['ID']/df_aux['Delivery_person_ID'],3)
    df_aux.columns = ['Week of Year','ID','Delivery_person_ID','Order by Delivery']


    fig = px.line( df_aux, x='Week of Year', y='Order by Delivery').update_layout(xaxis_showgrid=False, yaxis_showgrid=False)
    fig.update_layout(yaxis_range=[2,10])
    fig.update_xaxes(range=[6, 15])

    return fig

def country_maps(df1):
    cols = ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
    df_aux = df1.loc[:,cols].groupby(['City','Road_traffic_density']).median().reset_index()
    map1 = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']],
                       popup=location_info[['City','Road_traffic_density']]).add_to( map1 )
    folium_static( map1, width = 1024, height = 600)

    return None


# ---------------------------------------- Inicio da estrutura lógica do código ------------------------------------------
# ----------------------------------
#importando dataset
#----------------------------------

df = pd.read_csv('train.csv')

#Limpando dados
df1 = df.copy()
df1 = clean_code(df1)



#=========================================================
#BARRA LATERAL
#=========================================================

st.header('Marketplace - Visão Cliente')
#figura da empresa
image = Image.open('foguetinho.png')
st.sidebar.image( image , width=120 )

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

#filtro de data
st.sidebar.markdown('### Selecione uma data limite')
dataslider = st.sidebar.slider(
    'Data Limite',
    value=pd.datetime( 2022, 4, 23 ),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD/MM/YYYY')


st.sidebar.markdown("""___""")


#seleção de transito
traffic_options = st.sidebar.multiselect(
    'Condições do trânsito',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'])

st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered by Comunidade DS')

#filtro de data
linhas_selecionadas = df1['Order_Date'] < dataslider
df1 = df1.loc[linhas_selecionadas,:]

#seleção de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)#está em
df1 = df1.loc[linhas_selecionadas,:]


#=========================================================
#LAYOUT SREAMLIT
#========================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

#clausula - palavra reservada do python

with tab1:
    with st.container():
        st.markdown('# Orders by Day')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True) #para caber no espaço

    with st.container():
        #col1, col2 = st.columns( 2 )
        #col1, col2 = st.columns(2, gap ="large")
        col1,col2 = st.columns([1.5,2.5], gap='large')  
        
        with col1:
            #grafico de pizza
            st.header('Traffic Order Share')
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            #Grafico de bolha
            st.header('Traffic Order City')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True)           
             
with tab2:
    with st.container():
        #Grafíco de linhas - Pedidos por semana
        st.markdown('# Order by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
        #Grafico de qt de pedidos por entregador por semana
        st.markdown('# Order Share by Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
              
        
with tab3:
    st.markdown('# Country Maps')
    country_maps(df1)

    


