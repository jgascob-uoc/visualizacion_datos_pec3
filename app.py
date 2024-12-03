import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


#https://www.rtve.es/noticias/20211118/auge-establecimientos-solo-para-adultos-ninofobia/2221920.shtml
#https://www.xataka.com/magnet/hotelessinninos-el-polemico-debate-sobre-los-alojamientos-turisticos-solo-para-adultos
#https://familiasenruta.com/recursos-viajeros/hoteles-solo-adultos/
#https://estonoesloquepareze.com/no-alojar-ninos-ninofobia/

# Cargar el dataset
@st.cache_data
def load_data():
    file_path = "hotel_bookings.csv"  # Ajusta la ruta según corresponda
    df = pd.read_csv(file_path)
    df = df.dropna(subset=['adults', 'children', 'babies'])
    df['total_nights'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
    df['arrival_date'] = pd.to_datetime(df['arrival_date_year'].astype(str) + '-' + 
                                        df['arrival_date_month'] + '-01', errors='coerce')
    if 'group_type' not in df.columns:  # Solo calcular si no existe
        df['group_type'] = df.apply(
            lambda row: 'Family' if row['adults'] >= 1 and (row['children'] > 0 or row['babies'] > 0)
            else ('Couple' if row['adults'] == 2 and row['children'] == 0 and row['babies'] == 0
                  else ('Group' if row['adults'] > 2 else 'Single')), axis=1
        )
    return df

# Cargar datos
df = load_data()

# Filtros interactivos
st.title("Análisis de Reservas de Hoteles")
st.sidebar.header("Filtros")

# Filtro de rango de fechas
date_range = st.sidebar.date_input(
    "Rango de Fechas",
    [df['arrival_date'].min(), df['arrival_date'].max()],
    min_value=df['arrival_date'].min(),
    max_value=df['arrival_date'].max()
)

# Aplicar filtros
filtered_data = df[
    df['arrival_date'].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))
]

# Visualización 6: Distribución de reservas por tipo de grupo
st.subheader("Distribución de Reservas por Tipo de Grupo")
group_distribution = filtered_data['group_type'].value_counts(normalize=True).reset_index()
group_distribution.columns = ['group_type', 'percentage']
fig6 = px.pie(group_distribution, values='percentage', names='group_type', title="Distribución de Reservas")
st.plotly_chart(fig6)

# Visualización: Comparativa de Métricas Clave por Tipo de Grupo (Radar)
st.subheader("Comparativa de Métricas Clave por Tipo de Grupo (Radar)")


# Visualización 3: Distribución de turistas por país, ordenada de mayor a menor
st.subheader("Distribución de Turistas por País")

# Agrupar y ordenar los datos
country_group = filtered_data.groupby(['country', 'group_type']).size().reset_index(name='count')
country_group_sorted = country_group.groupby('country')['count'].sum().reset_index().sort_values(by='count', ascending=False)

# Filtrar los países principales si hay muchos
top_countries = st.sidebar.slider("Número de Países a Mostrar", min_value=5, max_value=20, value=10)
country_group_filtered = country_group[country_group['country'].isin(country_group_sorted.head(top_countries)['country'])]

# Crear gráfico interactivo
fig_country = px.bar(
    country_group_filtered,
    x='country',
    y='count',
    color='group_type',
    title="Distribución de Turistas por País (Ordenada de Mayor a Menor)",
    category_orders={"country": country_group_sorted['country'].head(top_countries).tolist()}
)

# Mostrar gráfico
st.plotly_chart(fig_country)

# Filtro de tipo de hotel
hotel_filter = st.sidebar.multiselect(
    "Selecciona Tipo de Hotel",
    options=df['hotel'].unique(),
    default=df['hotel'].unique()
)

# Filtrar datos por tipo de hotel
filtered_hotel_data = filtered_data[filtered_data['hotel'].isin(hotel_filter)]

# Visualización: Preferencia de Tipo de Hotel por Grupo
st.subheader("Preferencia de Tipo de Hotel por Grupo")

# Agrupar datos
hotel_preference = filtered_hotel_data.groupby(['group_type', 'hotel']).size().reset_index(name='count')

# Crear gráfico interactivo
fig_hotel_preference = px.bar(
    hotel_preference,
    x='group_type',
    y='count',
    color='hotel',
    title="Preferencia de Tipo de Hotel por Grupo",
    labels={'group_type': 'Tipo de Grupo', 'count': 'Cantidad de Reservas', 'hotel': 'Tipo de Hotel'},
    barmode='group'
)

# Mostrar gráfico
st.plotly_chart(fig_hotel_preference)


# Visualización 1: Días de estancia promedio por tipo de grupo
st.subheader("Días de Estancia Promedio por Tipo de Grupo")
stay_avg = filtered_data.groupby('group_type')['total_nights'].mean().reset_index()
fig1 = px.bar(stay_avg, x='group_type', y='total_nights', title="Días de Estancia Promedio")
st.plotly_chart(fig1)

# Visualización: Días de Estancia Promedio por Mes y Tipo de Grupo
st.subheader("Días de Estancia Promedio por Mes y Tipo de Grupo")

# Calcular los días de estancia promedio por mes y grupo
monthly_stay_avg = (
    filtered_data.groupby([filtered_data['arrival_date'].dt.to_period('M'), 'group_type'])['total_nights']
    .mean()
    .reset_index()
)
monthly_stay_avg['arrival_date'] = monthly_stay_avg['arrival_date'].astype(str)

# Crear gráfico interactivo
fig_monthly_stay = px.line(
    monthly_stay_avg,
    x='arrival_date',
    y='total_nights',
    color='group_type',
    title="Días de Estancia Promedio por Mes y Tipo de Grupo",
    labels={
        'arrival_date': 'Mes',
        'total_nights': 'Estancia Promedio (Noches)',
        'group_type': 'Tipo de Grupo'
    }
)

# Mostrar gráfico en Streamlit
st.plotly_chart(fig_monthly_stay)


# Visualización 2: Peticiones especiales promedio por tipo de grupo
st.subheader("Peticiones Especiales Promedio por Tipo de Grupo")
special_requests_avg = filtered_data.groupby('group_type')['total_of_special_requests'].mean().reset_index()
fig2 = px.bar(special_requests_avg, x='group_type', y='total_of_special_requests', title="Peticiones Especiales Promedio")
st.plotly_chart(fig2)

# Visualización: Tasa de Reservas por Tipo de Grupo
st.subheader("Tasa de Reservas por Tipo de Grupo")

# Calcular la tasa de reservas
reservation_rate = filtered_data['group_type'].value_counts(normalize=True).reset_index()
reservation_rate.columns = ['group_type', 'reservation_rate']

# Crear gráfico interactivo
fig_reservation_rate = px.bar(
    reservation_rate,
    x='group_type',
    y='reservation_rate',
    title="Tasa de Reservas por Tipo de Grupo",
    labels={'group_type': 'Tipo de Grupo', 'reservation_rate': 'Tasa de Reservas'},
)

# Configurar diseño para que coincida con el formato de tasa de cancelación
fig_reservation_rate.update_layout(
    yaxis=dict(title="Tasa de Reservas (%)"),
    xaxis=dict(title="Tipo de Grupo"),
    title_x=0.5  # Centrar el título
)

# Mostrar gráfico
st.plotly_chart(fig_reservation_rate)

# Visualización 4: Reservas mensuales por tipo de grupo
st.subheader("Reservas Mensuales por Tipo de Grupo")
monthly_reservations = filtered_data.groupby([filtered_data['arrival_date'].dt.to_period('M'), 'group_type']).size().reset_index(name='count')
monthly_reservations['arrival_date'] = monthly_reservations['arrival_date'].astype(str)
fig4 = px.line(monthly_reservations, x='arrival_date', y='count', color='group_type', title="Reservas Mensuales por Tipo de Grupo")
st.plotly_chart(fig4)


# Visualización 5: Tasa de cancelación por tipo de grupo
st.subheader("Tasa de Cancelación por Tipo de Grupo")
cancel_rate = filtered_data.groupby('group_type')['is_canceled'].mean().reset_index()
fig5 = px.bar(cancel_rate, x='group_type', y='is_canceled', title="Tasa de Cancelación")
st.plotly_chart(fig5)

# Visualización: Cancelaciones por Mes y Tipo de Grupo
st.subheader("Cancelaciones por Mes y Tipo de Grupo")

# Filtrar y agrupar datos
monthly_cancellations = filtered_data[filtered_data['is_canceled'] == 1].groupby(
    [filtered_data['arrival_date'].dt.to_period('M'), 'group_type']
).size().reset_index(name='count')

# Formatear la fecha
monthly_cancellations['arrival_date'] = monthly_cancellations['arrival_date'].astype(str)

# Crear gráfico interactivo
fig_cancellations = px.line(
    monthly_cancellations,
    x='arrival_date',
    y='count',
    color='group_type',
    title="Cancelaciones por Mes y Tipo de Grupo",
    labels={'arrival_date': 'Mes', 'count': 'Cancelaciones', 'group_type': 'Tipo de Grupo'}
)

# Mostrar gráfico
st.plotly_chart(fig_cancellations)




# Calcular métricas clave por grupo
group_metrics = filtered_data.groupby('group_type').agg({
    'total_nights': 'mean',  # Duración promedio de estadía
    'adr': 'mean',           # Tarifa diaria promedio
    'is_canceled': 'mean',   # Tasa de cancelación
    'total_of_special_requests': 'mean'  # Promedio de peticiones especiales
}).reset_index()

# Escalar métricas para normalizar valores (0-1)
metrics_scaled = group_metrics.iloc[:, 1:].div(group_metrics.iloc[:, 1:].max(), axis=1)
metrics_scaled = pd.concat([group_metrics[['group_type']], metrics_scaled], axis=1)

# Categorías para el radar
categories = ['Duración Promedio (Noches)', 'Tarifa Diaria Promedio (ADR)', 'Tasa de Cancelación', 'Peticiones Especiales']

# Crear gráfico de radar
fig_radar = go.Figure()

for i, row in metrics_scaled.iterrows():
    values = row[1:].tolist()
    fig_radar.add_trace(go.Scatterpolar(
        r=values + [values[0]],  # Cerrar el gráfico
        theta=categories + [categories[0]],
        fill='toself',
        name=row['group_type']
    ))

# Configuración del diseño
fig_radar.update_layout(
    polar=dict(radialaxis=dict(visible=True)),
    title="Comparativa de Métricas Clave por Tipo de Grupo",
    showlegend=True
)

# Mostrar gráfico en Streamlit
st.plotly_chart(fig_radar)


# Comparativa de costos operativos y rentabilidad teórica por tipo de grupo
st.subheader("Comparativa de Costos Operativos")

# Calcular métricas clave
group_analysis = filtered_data.groupby('group_type').agg({
    'total_nights': 'mean',  # Duración promedio de estadía
    'total_of_special_requests': 'mean',  # Promedio de peticiones especiales
    'is_canceled': 'mean',  # Tasa de cancelación
    'adr': 'mean'  # Tarifa diaria promedio
}).reset_index()

# Calcular rentabilidad teórica
group_analysis['theoretical_rentability'] = group_analysis['adr'] * group_analysis['total_nights'] * (1 - group_analysis['is_canceled'])

# Crear gráfico interactivo
fig_cost_rentability = go.Figure()

# Agregar barras para costos operativos
fig_cost_rentability.add_trace(go.Bar(
    x=group_analysis['group_type'],
    y=group_analysis['total_nights'],
    name='Duración de Estadía',
    marker_color='green'
))
fig_cost_rentability.add_trace(go.Bar(
    x=group_analysis['group_type'],
    y=group_analysis['total_of_special_requests'],
    name='Peticiones Especiales',
    marker_color='purple'
))
fig_cost_rentability.add_trace(go.Bar(
    x=group_analysis['group_type'],
    y=group_analysis['is_canceled'] * 10,  # Escalar cancelaciones para visualización
    name='Tasa de Cancelación (*10)',
    marker_color='red'
))


# Configurar diseño del gráfico
fig_cost_rentability.update_layout(
    title="Comparativa de Costos Operativos y Rentabilidad Teórica",
    barmode='stack',
    xaxis=dict(title="Tipo de Grupo"),
    yaxis=dict(title="Costos Operativos"),
    legend=dict(title="Métricas"),
    height=600
)

# Mostrar gráfico
st.plotly_chart(fig_cost_rentability)


# Visualización: Rentabilidad Teórica por Tipo de Grupo
st.subheader("Rentabilidad Teórica por Tipo de Grupo")

# Calcular métricas clave
group_rentability = filtered_data.groupby('group_type').agg({
    'adr': 'mean',  # Tarifa diaria promedio
    'total_nights': 'mean',  # Duración promedio de estadía
    'is_canceled': 'mean'  # Tasa de cancelación
}).reset_index()

# Calcular rentabilidad teórica
group_rentability['theoretical_rentability'] = (
    group_rentability['adr'] * group_rentability['total_nights'] * (1 - group_rentability['is_canceled'])
)

# Crear gráfico interactivo
fig_rentability = px.bar(
    group_rentability,
    x='group_type',
    y='theoretical_rentability',
    title="Rentabilidad Teórica por Tipo de Grupo",
    labels={'group_type': 'Tipo de Grupo', 'theoretical_rentability': 'Rentabilidad Teórica'},
    color='group_type'
)

# Configurar diseño
fig_rentability.update_layout(showlegend=False)

# Mostrar gráfico
st.plotly_chart(fig_rentability)


