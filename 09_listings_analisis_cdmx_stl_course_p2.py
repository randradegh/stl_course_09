##
# Análisis de accidentes de «listings» en la CDMX. Uso de streamlit, dataframes, pandas, mapas.
##
# Fecha inicio: 20220206
# Ref: Proyecto personal con datos de INEGI

##
# Utilerías del proyecto
##
#from os import ST_WRITE
from calendar import c
from utils import *
from pydeck.types import String
# Biblioteca local
import geopandas as gpd

header("9 casos de negocio con Streamlit")
st.subheader("9. Análisis de alojamientos temporales en la CDMX. Parte 2.")
st.subheader("Introducción")
st.markdown("""
    De manera similar a lo que hicimos en la Parte 1, se analizarán los alojamientos temporales tradicionales de la Ciudad de México y 
    los que ofrecen los particulares por medio de la plataforma AirBnB.

    ### Los alojamientos temporales de la Ciudad de México y los Geodatos
    El objetivo de esta segunda parte de nuestra app es realizar un análisis sobre los inmbuebles para alojamientos temporales, 
    ya sea del tipo de hoteles (DENUE) o de particulares (AirBnB) en las diversas alcaldías de la 
    Ciudad de México usando datos georeferenciados-
    
    Se construirá una app interactiva que permita que el usuario seleccione los 
    datos que desea analizar.

    Se mostrarán gráficos que permitan sacar algunas conclusiones acerca de las 
    diferencias en el comportamiento en cada alcaldía, además de...
""")

##
# Carga de datos Datos y conformación de los datos entre datasets
##

"""
    ### Temas a analizar
    - ¿Qué _features_ tiene nuestros _dataset_?
    - ¿En qué alcaldias hay más alojamientos temporales, por tipo?
    - Otras preguntas.

    Alguna de las preguntas se responderán para cada alcaldía de manera 
    interactiva.

    Se usarán tres datasets:
    - Polígonos que describen las fronteras de las alcaldías de la CDMX
    - Datos del DENUE para la CDMX para el tema de la sesión
    - Listings de AiBnB descargados en línea desde el sitio http://data.insideairbnb.com para la CDMX actualizados al 20211225.

    ___
    ### Descarga de datos

    Cargamos los datos usando el método read_csv() de Pandas.
    #### 1. Descarga de los datos del **Directorio Estadístico Nacional de Unidades Económicas (DENUE)**.
    Sitio oficial en INEGI: https://www.inegi.org.mx/app/mapa/denue/default.aspx

    La descarga se hace del sitio https://www.inegi.org.mx/app/descarga/?ti=6, en particular los dos 
    archivos nombrados «Servicios de alojamiento temporal y de preparación de alimentos y bebidas».

    De los registros de esos dos archivos se seleccionaron solamente los referentes a los rubros de 
    alojamientos temporales. Con ellos se construyó el _dataset_que usaremos en esta sesión.

    #### 2. Descarga de los datos de los _listings_ de AirBnB para la CDMX

    El _dataset_ se obtiene de http://data.insideairbnb.com/mexico/df/mexico-city/2021-12-25/visualisations/listings.csv,

    Contiene las diversos tipos de alojamientos temporales con varias _features_ acerca de ellos.

    ##### Carga de los datos a la app
    - DENUE
"""
with st.echo(code_location='above'):
    pd_hoteles = pd.read_csv('data/denue_hoteles_cdmx_2020.csv', sep='|')

"""
        - AirBNB
"""

with st.echo(code_location='above'):
    
    url = "http://data.insideairbnb.com/mexico/df/mexico-city/2021-12-25/visualisations/listings.csv"
    
    st.cache_data()
    def get_data():
        return pd.read_csv(url)

    df_abb = get_data()

"""
    ___
    ##### Conformación de los datos del DENUE.
    Para poder analizar conjuntamente los datos de los tres datasets que utilizaremos, debemos 
    hacer alguns operaciones para que algunas columnas tengan el mismo nombre, aunque su 
    significado sea ligeramente diferente.

    Por ejemplo, renombramos la columna _name_ para ser congruente con _nom_estab_ del DENUE.
"""

with st.echo(code_location='above'):
    # Renombramos dos columnas para ser congruentes con nom_estab del DENUE
    df_abb = df_abb.rename(columns={'name':'nom_estab','neighbourhood':'nomgeo'})
    st.write(df_abb.head(5))

"""
    Para AirBnB definimos el dataset para usar en los mapas y lo limpiamos
"""
    
with st.echo(code_location='above'):
    map_data = df_abb[["latitude", "longitude", "nom_estab", "nomgeo"]].dropna(how="any")
    st.write(map_data.head(5))

"""
    Generamos un nuevo _dataset_ de los hoteles que aparecen em el DENUE que contenga solo 
    los _features_ que nos interesan
"""

with st.echo(code_location='above'):
    hoteles = pd_hoteles[['latitud', 'longitud','nom_estab','municipio']]

"""
   ... y renombramos la columna municipio a nomgeo.
"""
with st.echo(code_location='above'):
    hoteles = hoteles.rename(columns={'municipio':'nomgeo'})
    st.write(hoteles.head(5))


##
# Límites de las alcaldías
##

'''
    ___
    #### Carga de los datos del los límites de las alcaldías.

    Este dataset incluye las coordenadas geográficas que forman un poligono para cada 
    una de las alcadías, además de algunos _features_ más: varios identificadores, nombre de la alcaldía, clave 
    del municipio, la clave geográfica de la alcaldía, las coordenadas geográficas del centro geométrico de 
    la alcaldía y los polígonos en dos formatos.

    Cargamos los datos del archivo correspondiente: *limites_alcaldias_cdmx.geojson*
'''

st.code("""
    shape = gpd.read_file('data/limites_alcaldias_cdmx.geojson')
""")

shape = gpd.read_file('data/limites_alcaldias_cdmx.geojson')

with st.expander("Visualizar/Ocultar límites de alcaldías", expanded=False):
    st.write(shape)

"""
    Más adelante aprederán la manera de visualizar estos polígonos o fronteras de las alcaldías.
"""


"""
    Uno de los _features_ de el _dataframe_ de límites es el centro geográfico de cada alcaldía. Se 
    encuenta en la columna g_pnt_2.

    Por ejemplo, vamos a desplegar las coordenadas del centro geográfico de la alcaldía Coyoacán:
"""

with st.echo(code_location='above)'):
    st.write(shape[shape['nomgeo'] == 'Coyoacán'].g_pnt_2)
    
"""
    Además podemos crear un par de dataframes adicionales que contengan dos conjuntos de 
    alcaldías. Uno de los _datasets_ contendrá las alcaldías con un identificador menor a 8 y otro las 
    alcaldías con un identificador mayor o igual a 8.
"""    

with st.echo(code_location='above)'):
    shape_a = shape[shape['cve_mun'] < 10]
    shape_b = shape[shape['cve_mun'] >= 10]

"""
    Podemos desplegar las alcadías que se encuentran en cada uno de ellos, por ejemplo el primero:
"""

with st.echo(code_location='above)'):
    st.write(shape_a[['cve_mun','nomgeo']].sort_values('cve_mun'))

"""
    ...y el segundo.
"""
with st.echo(code_location='above)'):
    st.write(shape_b[['cve_mun','nomgeo']].sort_values('cve_mun'))

###
## ¡Mapas!
###

"""
    ___
    ## Creación de mapas usando geodatos con *_pypeck_*

    #### ¿Qué es *_pydeck_*?
    *_pydeck_* está hecho para visualizar puntos de datos en mapas 2D o 3D. En concreto, se encarga de:
    - representar grandes conjuntos de datos (> 1 millón de puntos), como nubes de puntos LIDAR o pings de GPS
    - actualizaciones a gran escala de puntos de datos, como trazos de puntos con movimiento
    - hacer bellos mapas,

    Por debajo funciona con el _framework_ deck.gl de JavaScript.

    *_pydeck_* es más poderoso cuando se usa junto con Pandas.

    #### Configuración y visualización de un mapa
    Para generar con un mapa con *_pydeck_* debemos generar una capa (_layer_) y un punto de vista 
    (_viewport_).  

    ##### _Layer_
    
    Permite configurar una capa deck.gl para renderizar un mapa. Los parámetros pasados 
    aquí serán específicos para la capa particular deck.gl que de decida usar.

    Consulte el catálogo de capas deck.gl para determinar los parámetros particulares de su capa. 
    
     Parámetros:
    - type (str): tipo de capa para renderizar, por ejemplo, ScatterplotLayer
    - id (str, predeterminado Ninguno). Nombre único para la capa
    - data (str o lista de dict de {str: Any} o pandas.DataFrame, por defecto Ninguno): una URL de datos para cargar o una matriz de datos
    - use_binary_transport (booleano, predeterminado Ninguno): booleano que indica datos binarios
    - **kwargs: cualquiera de los parámetros pasables a una capa deck.gl.

    Los argumentos adicionales dependen de cada tipo de capa.

    Los tipos que usaremos son:

    - HexagonLayer
    - GeoJsonLayer y
    - ScatterplotLayer

    *Ejemplo:*
"""

code ="""
bordes = pdk.Layer(
    "GeoJsonLayer",
    data=shape,
    opacity=0.8,
    stroked=False,
    filled=True,
    extruded=True,
    wireframe=True,
    pickable=True,
    get_elevation=0,
    get_fill_color="[253, 254, 254, 40]",
    pointType= 'circle',
    lineWidthScale= 20,
    lineWidthMinPixels= 50,
    get_line_color=[164, 64, 0],
    getPointRadius= 100,
    getLineWidth= 20,    
)
"""

st.code(code, language='python')

"""
    ##### Configuración del _ViewState_

    También tenemos que especificar un objeto ViewState.

    Imagine el ViewState cómo la manera de enfocar el globo terráqueo con una cámara.

    Debe definir cosas como el centro geográfico de su vista, el acercamiento (_zoom_) que desea 
    usar, el ángulo de inclinación, etc.
        
    *_pydeck_* también proporciona algunos controles, la mayoría de los cuales deberían ser 
    familiares para las aplicaciones de mapas en toda la web. De forma predeterminada, 
    puede mantener presionado y arrastrar para rotar el mapa.

    *Ejemplo:*
"""

st.code("""
    # Set the viewport location
    view_state = pdk.ViewState(
        longitude=-1.415,
        latitude=52.2323,
        zoom=6, # 0 a 24: Globo a un edificio en particular
        min_zoom=5,
        max_zoom=15,
        pitch=40.5,
        bearing=-27.36) # Orientación con respecto al Norte
""", language='python'
)

"""
    ##### Tooltip
    Para generar el _tooltip_ se debe generar un diccionario:

    - HTML: establece el innerHTML del _tooltip_.
    - Texto: establezca el innerText del _tooltip_.
    - Estilo: un diccionario de estilos CSS que modificará el estilo predeterminado del _tooltip_.
    
    Tenga en cuenta que solo debe proporcionar html o texto, pero no ambos.

    **Sintaxis de plantillas**: 
    Se puede usar una sintaxis de plantilla utilizando convenciones similares a la sintaxis _.format_  
    de Python con nombres de variables.

    En el ejemplo, _elevationValue_ y _colorValue_ son _features_ de nuestro _dataset_.

    *Ejemplo:*
"""

code = """
    tooltip = {
   "html": "<b>Elevation Value:</b> {elevationValue} <br/> <b>Color Value:</b> {colorValue}",
   "style": {
        "backgroundColor": "steelblue",
        "color": "white"
   }
}
"""
st.code(code, language='python')

"""
    ##### Creación de la imagen del mapa (renderizado)

    Para crear la imagen se debe definir el estilo del mapa, las capas que los constituirán, 
    la vista inicial y, en su caso, el tooltip.

    Para crear el mapa usamos el método _pdk.Deck_ como parámetro del método _st.pydeck_chart_, 
    el cual requiere de algunos parámetros:
    - El estilo del mapa, es decir el mapa base,
    - Las capas a mostrar (puede ser solamente una).
    - La vista inicial,
    - Un _tooltip_ opcional.

    Cada uno de los parámetros de puede generar y configurar como una variable que se pasa al método 
    correspondiente.

    En nuestro ejemplos _capas_ es una lista, y _view_state_ y _my_tooltip_ son diccionarios.
"""
code= """
    m1 = st.pydeck_chart(pdk.Deck(map_style='mapbox://styles/mapbox/light-v10',
    layers=[capas], 
    initial_view_state=view_state, 
    tooltip=my_tooltip))
"""
st.code(code, language='python')

"""
    ##### Mapa base de *Mapbox*.
    Para este curso usaremos los mapas base de Mapbox.

    Mapbox es una plataforma de datos geográficos que empodera a los mapas y a los servicios de 
    ubicación utilizados en muchas aplicaciones populares. Sus servicios básicos son gratuitos, 
    pero tambien ofrece servicios con un cargo.

    Mapbox cuenta con varios estilos de mapas que pueden revisarse en 
    https://docs.mapbox.com/api/maps/styles/.

    La siguiente imagen se obtuvo del sitio de Mapbox.
"""

st.image('images/mapbox_styles.png')

"""
    Aquí se muestra el estilo «Mapbox Streets v8».
"""
st.image('images/mapbox_streets.png')



st.info("Mapa 1: Ejemplo con una capa del tipo de puntos o _ScatterplotLayer_.")

with st.echo(code_location='above'):
    st.write("""
        ##### Mapa 1: De puntos (_ScatterPlot_) de los _listings_ de AirBnB en la CDMX.
    """)
    # Capa, nombrara puntos_abb
    puntos_abb=pdk.Layer(
        'ScatterplotLayer',
        data=map_data, 
        get_position='[longitude, latitude]',
        get_radius=10,          # Radius is given in meters
        get_fill_color=[255, 0, 255, 140],
        elevation_scale=0,
        pickable=True
    )

    view_state = pdk.ViewState(
        latitude=19.4163,
        longitude=-99.1710,
        zoom=14,
        pitch=0
    )

    # El render se llama e1, se ejecuta al definirlo
    # Observe el estilo del mapa: dark-v10
    e1 = st.pydeck_chart(pdk.Deck(map_style='mapbox://styles/mapbox/dark-v10',
        layers=puntos_abb, 
        initial_view_state=view_state
        ))

st.info("Mapa 2: Capa del tipo _GeoJsonLayer_ de los límites de las alcaldías de la CDMX.")
#https://deck.gl/docs/api-reference/layers/geojson-layer
with st.echo(code_location='above'):
    
    bordes = pdk.Layer(
        "GeoJsonLayer",
        data=shape,
        opacity=0.8,
        stroked=True,
        filled=True,
        extruded=True,
        get_elevation=5,
        wireframe=True,
        pickable=True,
        get_fill_color="[253, 254, 254, 40]",
        lineWidthScale=20,
        lineGetWidth=1,
        lineWidthMinPixels=100,
        lineWidthMaxPixels=120,
        get_line_color=[176, 58, 46],
    )

    view_state = pdk.ViewState(
        latitude=19.3266,
        longitude=-99.1490,
        zoom=9,
        pitch=0
    )

    m2_tooltip={
        "html": 
        "<i>Mapa 2</i>"
        "<br><b>Alcaldía:</b> {nomgeo}",
        "style": {"color": "#FAFAFA", 
                "background-color":"#9a7d0a",
                "z-index":2,}
    }

    # El render se llama e2, se ejecuta al definirlo
    # Observe el estilo del mapa: light-v10
    e2 = st.pydeck_chart(pdk.Deck(map_style='mapbox://styles/mapbox/streets-v11',
        layers=bordes, 
        initial_view_state=view_state,
        tooltip = m2_tooltip
        ))

    
    
"""
    #### Manejo programático de las capas

    Para finalizar usaremos un _select_ de HTML para definir que capas deben visualizarse sobre 
    el mapa base.

    El código que usaremos se muestra a continuación.
"""
st.code(
"""
CAPAS = {
    "Fronteras de Alcaldías" : pdk.Layer(
        "GeoJsonLayer",
        data=shape,
        opacity=0.8,
        stroked=False,
        filled=True,
        extruded=True,
        wireframe=True,
        pickable=True,
        get_elevation=0,
        get_fill_color="[253, 254, 254, 40]",
        pointType= 'circle',
        lineWidthScale= 20,
        lineWidthMinPixels= 50,
        get_line_color=[164, 64, 0],
        getPointRadius= 100,
        getLineWidth= 100,    
        lineWidthUnits='meters'
    ),
    "Fronteras de Alcaldías Parciales" : pdk.Layer(
        "GeoJsonLayer",
        data=shape_a,
        opacity=0.8,
        stroked=False,
        filled=True,
        extruded=True,
        wireframe=True,
        pickable=True,
        get_elevation=10,
        pointType= 'circle',
        lineWidthScale= 20,
        lineWidthMinPixels= 50,
        get_line_color=[164, 64, 0],
        getPointRadius= 100,
        getLineWidth= 20,    
        get_fill_color=[229, 152, 102, 10],
    ),
    "AirBnB" : pdk.Layer(
        'ScatterplotLayer',
        data=map_data, 
        get_position='[longitude, latitude]',
        get_radius=30,          # Radius is given in meters
        get_fill_color=[230, 126, 34, 90],
        elevation_scale=0,
        #elevation_range=[0, 1000],
        pickable=True
    ), 

    "Hoteles" : pdk.Layer(
        'ScatterplotLayer',
        data=hoteles, 
        get_position='[longitud, latitud]',
        get_radius=30,          # Radius is given in meters
        get_fill_color='[5, 0, 160]',
        elevation_scale=0,
        #elevation_range=[0, 1000],
        pickable=True
    ),

    "AirBnB Hexágonos" : pdk.Layer(
        'HexagonLayer',
        data=map_data, 
        get_position='[longitude, latitude]',
        get_radius=30,          # Radius is given in meters
        get_fill_color=[230, 126, 34, 250],
        radius=40,
        elevation_scale=2,
        elevation_range=[0, 1000],
        extruded=True,
        pickable=True
    )
}
# text = pdk.Layer(
#     "TextLayer",
#     data=shape,
#     pickable=True,
#     get_position='geometry',
#     get_text="nomgeo",
#     get_size=60,
#     get_color=[160,64,0,20],
#     get_angle=0,
#     # Note that string constants in pydeck are explicitly passed as strings
#     # This distinguishes them from columns in a data set
#     get_text_anchor=String("middle"),
#     get_alignment_baseline=String("center"),
# )
view_state = pdk.ViewState(
    latitude=19.3266,
    longitude=-99.1490,
    zoom=9.5,
    pitch=0
)

my_tooltip={
    "html": 
    "Ejercicio con <i>Maxbox</i>"
    "<br><b>Nombre:</b> {nom_estab}"
    "<br><b>Alcaldía:</b> {nomgeo}",
    "style": {"color": "#FAFAFA", 
            "background-color":"#9a7d0a",
            "z-index":2,}
}

"""
    ### Capas
    #### Seleccione las capas a visualizar
"""
st.sidebar.markdown("""
## Capas del Mapa
#### Seleccione las capas a visualizar
""")
selected_layers = [
    layer for layer_name, layer in CAPAS.items()
    if st.sidebar.checkbox(layer_name, True)]
if selected_layers:
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v10",
        initial_view_state=view_state,
        layers=selected_layers,
        tooltip=my_tooltip

    ))
else:
    st.error("Please choose at least one layer above.")
"""
)

"""
Como puede observarse...

Cuando se elige _«Frontera de Alcaldías Parciales»_ se indica a _py_deck_ que use el _dataset_ 
recortado para solamente algunas de las 16 alcaldías de la CDMX:
   
        shape_a = shape[shape['cve_mun'] < 10]

Observe que se están seleccionando las alcaldías con un clave de municipio menor a 10, es decir de 2 a 9.
"""

#st.write('Usted seleccionó:', sel_capa)

st.write(shape_a[['nomgeo']].sort_values('nomgeo'))


st.error("Revisar el efecto del orden de las capas")
# Configuración para diseñar el mapa de Mapbox
##

## Capas 
CAPAS = {
    "Fronteras de Alcaldías" : pdk.Layer(
        "GeoJsonLayer",
        data=shape,
        opacity=0.8,
        stroked=False,
        filled=True,
        extruded=True,
        wireframe=True,
        pickable=True,
        get_elevation=0,
        get_fill_color="[253, 254, 254, 40]",
        pointType= 'circle',
        lineWidthScale= 20,
        lineWidthMinPixels= 50,
        get_line_color=[164, 64, 0],
        getPointRadius= 100,
        getLineWidth= 100,    
        lineWidthUnits='meters'
    ),
    "Fronteras de Alcaldías Parciales" : pdk.Layer(
        "GeoJsonLayer",
        data=shape_a,
        opacity=0.8,
        stroked=False,
        filled=True,
        extruded=True,
        wireframe=True,
        pickable=True,
        get_elevation=10,
        pointType= 'circle',
        lineWidthScale= 20,
        lineWidthMinPixels= 50,
        get_line_color=[164, 64, 0],
        getPointRadius= 100,
        getLineWidth= 20,    
        get_fill_color=[229, 152, 102, 10],
    ),
    "AirBnB" : pdk.Layer(
        'ScatterplotLayer',
        data=map_data, 
        get_position='[longitude, latitude]',
        get_radius=30,          # Radius is given in meters
        get_fill_color=[230, 126, 34, 90],
        elevation_scale=0,
        #elevation_range=[0, 1000],
        pickable=True
    ), 

    "Hoteles" : pdk.Layer(
        'ScatterplotLayer',
        data=hoteles, 
        get_position='[longitud, latitud]',
        get_radius=30,          # Radius is given in meters
        get_fill_color='[5, 0, 160]',
        elevation_scale=0,
        #elevation_range=[0, 1000],
        pickable=True
    ),

    "AirBnB Hexágonos" : pdk.Layer(
        'HexagonLayer',
        data=map_data, 
        get_position='[longitude, latitude]',
        get_radius=30,          # Radius is given in meters
        get_fill_color=[230, 126, 34, 250],
        radius=40,
        elevation_scale=2,
        elevation_range=[0, 1000],
        extruded=True,
        pickable=True
    )
}
# text = pdk.Layer(
#     "TextLayer",
#     data=shape,
#     pickable=True,
#     get_position='geometry',
#     get_text="nomgeo",
#     get_size=60,
#     get_color=[160,64,0,20],
#     get_angle=0,
#     # Note that string constants in pydeck are explicitly passed as strings
#     # This distinguishes them from columns in a data set
#     get_text_anchor=String("middle"),
#     get_alignment_baseline=String("center"),
# )
view_state = pdk.ViewState(
    latitude=19.3266,
    longitude=-99.1490,
    zoom=9.5,
    pitch=0
)

my_tooltip={
    "html": 
    "Ejercicio con <i>Maxbox</i>"
    "<br><b>Nombre:</b> {nom_estab}"
    "<br><b>Alcaldía:</b> {nomgeo}",
    "style": {"color": "#FAFAFA", 
            "background-color":"#9a7d0a",
            "z-index":2,}
}

"""
    ### Capas
    #### Seleccione las capas a visualizar
"""
st.sidebar.markdown("""
## Capas del Mapa
#### Seleccione las capas a visualizar
""")
selected_layers = [
    layer for layer_name, layer in CAPAS.items()
    if st.sidebar.checkbox(layer_name, True)]
if selected_layers:
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v10",
        initial_view_state=view_state,
        layers=selected_layers,
        tooltip=my_tooltip

    ))
else:
    st.error("Please choose at least one layer above.")
