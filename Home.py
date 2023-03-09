import streamlit as st
from PIL import Image

st.set_page_config(page_title='Home')

#image_path = "foguetinho.png"

image = Image.open('foguetinho.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.write('# Curry Company Growth Dashboard')

st.markdown(
    """
    
    Growth Dashboard foi contruído para acompanhar as métricas de crescimento do Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    -Visão Entregadores:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
        ### Ask for help
        - Time de Data Science no Discord
            - @Vivi
""")