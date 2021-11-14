from re import T
import streamlit as st
    # importing numpy and pandas for to work with sample data.
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import plotly_express as px
import plotly.io as pio
import datetime as dt
from streamlit.elements.color_picker import ColorPickerMixin
import plotly_express as px
import plotly.graph_objects as go
import seaborn as sns
import time
import os
import json 
from math import *

st.title('Projet Data Visualization - Hatim Chahdi')
st.text('Mankour Inès')
st.markdown('Transactions immo 2016 à 2020')


pio.renderers.default='firefox'


#df.info(verbose=False, memory_usage="deep") #grace a ca j'ai pu voir que je passais de 3Go a 1Go en passant en argument 
#les colonnes que je voulais et les dtypes de chaque colonne dans read_csv()
#df.isnull().sum(axis = 0) # pour compter le nombre de NaN par colonne pour voir quelle colonne on garde 
#df.dropna(axis=1,thresh=,inplace=True) #on drop les colonnes dont on a au minimum thresh valeurs 
#df.dropna(axis=0, inplace=True) #on drop les lignes ou il y a au moins 1 NaN
#pd.options.display.max_columns = None


departementsjson=json.load(open("departements.geojson",'r'))

def log_time(func):
    """
    Mesure le temps d'exécution d'une fonction.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        print("Durée d'exécution : {:1.3}s".format(end_time - start_time), file=open("output.txt","w"))

    return wrapper




def get_month(df):
    return df.month

@st.cache(allow_output_mutation=True)
def loaddata(csv):
    req_col=['date_mutation','nature_mutation','valeur_fonciere','code_departement','nom_commune','type_local','surface_reelle_bati','nombre_pieces_principales','nature_culture','surface_terrain','longitude','latitude','adresse_nom_voie']
    df=pd.read_csv(csv,usecols=req_col,parse_dates=['date_mutation'],dtype={("nature_mutation ","nom_commune","nature_culture",'adresse_nom_voie'):"category",("valeur_fonciere","surface_relle_bati","nombre_pieces_principales","surface_terrain","longitude","latitude") : "float32",'code_departement': "string"} )
    df['date_mutation']=pd.to_datetime(df["date_mutation"])
    df.dropna(axis=0, inplace=True)
    df['month']=df['date_mutation'].map(get_month)
    return(df)

df2020=loaddata('full_2020.csv')
df2019=loaddata('full_2019.csv')
df2018=loaddata('full_2018.csv')
df2017=loaddata('full_2017.csv')
df2016=loaddata('full_2016.csv')

def renaming(df,column1,column2):
        df.rename(columns={column1:column2},inplace=True)

renaming(df2020,'valeur_fonciere','valeur_fonciere2020')
renaming(df2019,'valeur_fonciere','valeur_fonciere2019')
renaming(df2018,'valeur_fonciere','valeur_fonciere2018')
renaming(df2017,'valeur_fonciere','valeur_fonciere2017')
renaming(df2016,'valeur_fonciere','valeur_fonciere2016')


#--------------------------------- Fonctions des graphiques --------------------------------
def mapslider(df):
        month_to_filter=st.slider('Select the month',min_value=min(df['month']),max_value=max(df['month']))
        st.write("Slider:",month_to_filter)
        filtered_data = df[df["date_mutation"].dt.month == month_to_filter]
        st.subheader(f'Map of all sales during month {month_to_filter}')
        filtered_data['lon'] = df['longitude']
        filtered_data['lat'] = df['latitude']
        st.map(filtered_data)

def linechart(df,dropdown):
    if len(dropdown)>0:
        if '2020' in dropdown:
            mean_vf_2020=df2020.groupby('month').valeur_fonciere2020.mean()
            df=pd.concat([df,mean_vf_2020],axis=1)
        if '2019' in dropdown:
            mean_vf_2019=df2019.groupby('month').valeur_fonciere2019.mean()
            df=pd.concat([df,mean_vf_2019],axis=1)
        if '2018'in dropdown:
            mean_vf_2018=df2018.groupby('month').valeur_fonciere2018.mean()
            df=pd.concat([df,mean_vf_2018],axis=1)
        if '2017' in dropdown:
            mean_vf_2017=df2017.groupby('month').valeur_fonciere2017.mean()
            df=pd.concat([df,mean_vf_2017],axis=1)
        if '2016' in dropdown:
            mean_vf_2016=df2016.groupby('month').valeur_fonciere2016.mean()
            df=pd.concat([df,mean_vf_2016],axis=1)
    st.line_chart(df)


def plotlyscatter(df,title1,title2):
    fig = px.scatter(
            x=df.index,
            y=df[1],
        )
    fig.update_layout(
        xaxis_title=title1,
        yaxis_title=title2,
    )
    st.write(fig)


def choropleth(df,column):
    for i in [20,57,67,68]:
        df.loc[i] = df[column].mean()
    
    df['logcol']=np.log(df[column])
    fig=px.choropleth(df,geojson=departementsjson, locations=df.index,color=df.logcol,scope="europe",featureidkey='properties.code')
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.write(fig)

def yearlygobar(group,count,name1,name2,name3):
    by_type2020=df2020.groupby(group).count()[count]
    by_type2019=df2019.groupby(group).count()[count]
    by_type2018=df2018.groupby(group).count()[count]
    by_type2017=df2017.groupby(group).count()[count]
    by_type2016=df2016.groupby(group).count()[count]
    
    year_range = pd.Series(pd.date_range("2016-01-01", periods=5, freq="Y")).dt.year
    ventes_appt=[]
    ventes_appt.extend([by_type2016[0],by_type2017[0],by_type2018[0],by_type2019[0],by_type2020[0]])
    ventes_local=[]
    ventes_local.extend([by_type2016[1],by_type2017[1],by_type2018[1],by_type2019[1],by_type2020[1]])
    ventes_maison=[]
    ventes_maison.extend([by_type2016[2],by_type2017[2],by_type2018[2],by_type2019[2],by_type2020[2]])
    fig = go.Figure(data=[
        go.Bar(name=name1, x=year_range, y=ventes_appt),
        go.Bar(name=name2, x=year_range, y=ventes_local),
        go.Bar(name=name3, x=year_range, y=ventes_maison),
    ])
    
    fig.update_layout(barmode='group',title="Nombre de ventes de chaque type de local par année",yaxis_title="Nombre de ventes")
    st.plotly_chart(fig)


def pieselect(group,count,annee):
    if annee==2016:
        by_nature2016=df2016.groupby(group).count()[count]
        fig = px.pie(by_nature2016,values=count,names=by_nature2016.index)
    if annee==2017:
        by_nature2017=df2017.groupby(group).count()[count]
        fig = px.pie(by_nature2017,values=count,names=by_nature2017.index)
    if annee==2018:
        by_nature2018=df2018.groupby(group).count()[count]
        fig = px.pie(by_nature2018,values=count,names=by_nature2018.index)
    if annee==2019:
        by_nature2019=df2019.groupby(group).count()[count]
        fig = px.pie(by_nature2019,values=count,names=by_nature2019.index)
    if annee==2020: 
        by_nature2020=df2020.groupby(group).count()[count]
        fig = px.pie(by_nature2020,values=count,names=by_nature2020.index)
    st.write(fig)



# def run_the_app():
#     @st.cache
#     def load_metadata(url):
#         return pd.read_csv(url)


st.sidebar.title("Où voulez-vous aller ? ")
app_mode = st.sidebar.selectbox("",
        ["Accueil", "Recherche/ Vente Appart"])


def main(app_mode):


    if app_mode== "Accueil":
        st.sidebar.success('')


        mapslider(df2020)


        st.title(" Voici une carte legendée en couleur par la valeur foncière moyenne de chaque département")
        dfdep2020=df2020.groupby('code_departement').mean('valeur_fonciere2020')
        dfdep2020.drop(dfdep2020.tail(4).index,inplace=True)
        choropleth(dfdep2020,'valeur_fonciere2020')

    

        st.title("Valeur foncière en fonction des mois de l'année")
        tickers=('2019','2018','2017','2016')
        dropdown=st.multiselect('Comparer avec',tickers)
        mean_vf_2020=df2020.groupby('month').valeur_fonciere2020.mean()
        linechart(mean_vf_2020,dropdown)


        #by_surface_terrain= df2020.groupby('surface_terrain').mean()
        #st.title("moyenne des valeurs foncieres en fonction de la surface du terrain")
        #graph=px.bar(by_surface_terrain,y=by_surface_terrain["valeur_fonciere"])
        #st.plotly_chart(graph)


        #ici je fais un px.bar du nombre de ventes par type de local pour chaque année donc x=typelocal y=nombreventes 
        #et pour chaque type de local on a la vente de chaque année OU ALORS 
        #x=[2016,2017,2018,2019,2020] et on a nos barres par type de local 



        
        yearlygobar('type_local','date_mutation','Appartement','Local','Maison')
        
        
        

        annee=st.selectbox("",[2016,2017,2018,2019])
        pieselect('nature_mutation','date_mutation',annee)



        #scatter avec y=valeur fonciere et x = m2 
        dfscatter2020=df2020.groupby('surface_terrain').valeur_fonciere2020.mean()
        print(dfscatter2020)
        fig1=px.scatter(dfscatter2020,x=dfscatter2020.index,y=dfscatter2020)
        st.plotly_chart(fig1)

    if app_mode== "Recherche/ Vente Appart":
        st.sidebar.success('')
        st.title("Recherche/vente Appart")

        st.write("Voici les ventes faites en 2020 dans votre secteur pour vous donner un ordre d'idée des prix si vous voulez vendre ou acheter :)")

        departements=df2020['code_departement'].unique() 
        
        choixdep = st.selectbox("",departements)
        df2=df2020[df2020["code_departement"] == choixdep]
        communes=df2['nom_commune'].unique()
        communes.sort()
        choixcom=st.selectbox("",communes)
        df3=df2[df2["nom_commune"] == choixcom]
        rues=df3['adresse_nom_voie'].unique()
        rues.sort()
        choixrue=st.selectbox("",rues)
        filtered_data = df3[df3["adresse_nom_voie"] == choixrue]
        filtered_data['lon'] = df2020['longitude']
        filtered_data['lat'] = df2020['latitude']
        st.map(filtered_data)
        st.write("voici les ventes situées dans" + choixrue)
        st.write(filtered_data)







        



main(app_mode)


