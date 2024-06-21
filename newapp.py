import streamlit as st
import pandas as pd
import preprocessor
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import plotly.graph_objs as go
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import numpy as np

st.title('Global Terrorism Analysis')
df = pd.read_csv('globalterrorismdb_0718dist.csv', encoding='ISO-8859-1', sep=',', on_bad_lines='skip',  engine='python')
st.sidebar.title('Global Terrorism Analysis')

df.rename(columns={'iyear':'Year','imonth':'Month','iday':'Day','country_txt':'Country','provstate':'state','region_txt':'Region','attacktype1_txt':'AttackType','target1':'Target','nkill':'Killed','nwound':'Wounded','summary':'Summary','gname':'Group','targtype1_txt':'Target_type','weaptype1_txt':'Weapon_type','motive':'Motive'},inplace=True)
df=df[['Year','Month','Day','Country','state','Region','city','latitude','longitude','AttackType','Killed','Wounded','Target','Summary','Group','Target_type','Weapon_type','Motive']]

user_menu=st.sidebar.radio(
    'Select an Option',
    ('Overall Analysis','Year wise Analysis' ,'Country wise Analysis')
)

if user_menu=='Overall Analysis':
    st.title('Most Terrorist Attacks')
    Country=df['Country'].value_counts().idxmax()
    Region=df['Region'].value_counts().idxmax()
    Year=df['Year'].value_counts().idxmax()
    Month=df['Month'].value_counts().idxmax()
    AttackType=df['AttackType'].value_counts().idxmax()

    col1,col2,col3 =st.columns(3)

    with col1:
        st.subheader('Country')
        st.write(Country)
    with col2:
        st.subheader('Region')
        st.write(Region)
    with col3:
        st.subheader('Year')
        st.write(Year)
    col4,col5 =st.columns(2)
    with col4:
        st.subheader('Month')
        st.text(Month)
    with col5:
        st.header('AttackType')
        st.text(AttackType)


    st.header('Region-Wise Trends For Global Terrorism')
    crosstab=pd.crosstab(df.Year,df.Region)
    fig,ax=plt.subplots()
    crosstab.plot(kind='area',stacked=False,ax=ax)
    plt.title('Terrorist Activities in Each Year',fontsize=25)
    plt.ylabel('Number of Attacks',fontsize=20)
    plt.xlabel('Year',fontsize=20)
    st.pyplot(fig)
    st.write('The Terrorist Activities has been immensely risen in past few years in regions like SOUTH ASIA and MIDDLE EAST & NORT AFRICA')



    df['Wounded'] = df['Wounded'].fillna(0).astype(int)
    df['Killed'] = df['Killed'].fillna(0).astype(int)
    df['Casualities'] = df['Killed'] + df['Wounded']

    # Sort by Casualities and select the top 40
    df1 = df.sort_values(by='Casualities', ascending=False)[:40]

    # Create a pivot table
    table1 = df1.pivot_table(index='Country', columns='Year', values='Casualities')
    table1.fillna(0, inplace=True)

    # Create the heatmap
    heatmap = go.Heatmap(z=table1.values, x=table1.columns, y=table1.index, colorscale='Viridis')
    data = [heatmap]
    layout = go.Layout(title='Top 40 Worst Terror Attacks Casuality')
    fig1 = go.Figure(data=data, layout=layout)

    # Display the heatmap in Streamlit
    st.header('Total Killings Analysis')
    st.subheader("Top 40 Worst Terror Attacks Casuality Heatmap")
    st.plotly_chart(fig1)
    st.write('In between 1982-2017 the worst ever Terror attack was marked in United States in 2001 casuing 9574 Casualities(killed and wounded people combined)')

    st.header('Percentage of Killings by Each Attack Type')
    killData=df.loc[:,'Killed']
    
    attackData=df.loc[:,'AttackType']
    typeKillData=pd.concat([attackData,killData],axis=1)
    table2=typeKillData.pivot_table(columns='AttackType',values='Killed',aggfunc='sum')
    labels=table2.columns.tolist()#convert table columns to list
    T_values = table2.sum(axis=0).tolist()
    fig2,ax2=plt.subplots(figsize=(18,8),subplot_kw=dict(aspect='equal'))
    ax2.pie(T_values, startangle=90, autopct='%.2f%%')
    ax2.set_title('Percentage of Kill by Each Attack Type')
    ax2.legend(labels, loc='upper right', bbox_to_anchor=(1.3, 0.9), fontsize=10)
    st.write("Total number of people killed by terror attacks all-time:",int(sum(killData.dropna())))
    # Display the pie chart in Streamlit
    st.pyplot(fig2)
    st.write('Armed Assault and bombing/explosions are the major causes of death as they seemed to have taken more than 77% of lives')

if user_menu=='Year wise Analysis':
    st.sidebar.title('Year wise Analysis')
    
    Year_list=df['Year'].dropna().unique().tolist()
    Year_list.sort()
    selected_year=st.sidebar.selectbox('Select an year',Year_list)

    filterYear = df['Year'] == selected_year
    filterData = df[filterYear]
    reqfilterData = filterData.loc[:, ['city', 'latitude', 'longitude']]
    reqfilterData = reqfilterData.dropna()
    dataList = reqfilterData.values.tolist()

    st.header(f'Total Terrorist Attacks Planned and Executed in {selected_year}')

    map = folium.Map(location=[0, 30], tiles='CartoDB positron', zoom_start=2)
    markerCluster = folium.plugins.MarkerCluster().add_to(map)

    for i in range(len(dataList)):
        folium.Marker(location=[dataList[i][1], dataList[i][2]], popup=dataList[i][0]).add_to(markerCluster)


    
    folium_static(map)

    st.header('Yearwise terriorist activities')
    x_year=df['Year'].unique()
    y_count_years=df['Year'].value_counts(dropna=False).sort_index()
    plt.figure(figsize=(20,10))
    sns.barplot(x=x_year,y=y_count_years,palette='rocket')
    plt.xticks(rotation=90)
    plt.xlabel('Attack Year')
    plt.ylabel('Number of Attacks Each Year')
    plt.title('Attack of Year')
    st.pyplot(plt)
    st.write('We can witness in Exponential rise in terrorist activities after 1973')

if user_menu=='Country wise Analysis':
    st.sidebar.title('Country wise Analysis')
    st.header('Top Countries Affected by Terrorism')
    plt.subplots(figsize=(15,6))
    sns.barplot(x=df.Country.value_counts()[:15].index,y=df.Country.value_counts()[:15].values,palette='PiYG')
    plt.title('Top Countries Affected')
    plt.xlabel('Countries')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    st.pyplot(plt)
    st.write('Surprisingly, Our Country India lies at fourth in this list')

    st.title('Total Number of Killings Countrywise')
    countrydata=df.loc[:,'Country']
    killData=df.loc[:,'Killed']
    countrykillData=pd.concat([countrydata,killData],axis=1)
    table3=countrykillData.pivot_table(columns='Country',values='Killed',aggfunc='sum')

    fig_size=plt.rcParams["figure.figsize"]
    fig_size[0]=25
    fig_size[1]=25
    plt.rcParams["figure.figsize"]=fig_size


    label=table3.columns.tolist()
    label=label[:50]
    index=np.arange(len(label))
    transpose=table3.T
    T_values=transpose.values.tolist()
    T_values=T_values[:50]
    T_values=[int(k[0]) for k in T_values]#converting float to int
    colors = ['red', 'blue', 'green', 'purple']
    fig,ax=plt.subplots(1,1)
    ax.yaxis.grid(True)
    fig_size=plt.rcParams["figure.figsize"]
    fig_size[0]=25
    fig_size[1]=25
    plt.bar(index,T_values,width=1.1,color=colors)
    plt.xticks(index,label,fontsize=20,rotation=90)
    plt.xlabel('Countries',fontsize=20)
    plt.ylabel('Number of people killed',fontsize=20)
    plt.title('Number of people killed Countriwise',fontsize=20)
    st.pyplot(fig)
    

    label=table3.columns.tolist()
    label=label[50:101]
    index=np.arange(len(label))
    transpose=table3.T
    T_values=transpose.values.tolist()
    T_values=T_values[50:101]
    T_values=[int(k[0]) for k in T_values]#converting float to int
    colors = ['red', 'blue', 'green', 'purple']
    fig,ax=plt.subplots(1,1)
    ax.yaxis.grid(True)
    fig_size=plt.rcParams["figure.figsize"]
    fig_size[0]=25
    fig_size[1]=25
    plt.bar(index,T_values,width=1.1,color=colors)
    plt.xticks(index,label,fontsize=20,rotation=90)
    plt.xlabel('Countries',fontsize=20)
    plt.ylabel('Number of people killed',fontsize=20)
    plt.title('Number of people killed Countriwise',fontsize=20)
    st.pyplot(fig)

    label=table3.columns.tolist()
    label=label[151:206]
    index=np.arange(len(label))
    transpose=table3.T
    T_values=transpose.values.tolist()
    T_values=T_values[151:206]
    T_values=[int(k[0]) for k in T_values]#converting float to int
    colors = ['red', 'blue', 'green', 'purple']
    fig,ax=plt.subplots(1,1)
    ax.yaxis.grid(True)
    fig_size=plt.rcParams["figure.figsize"]
    fig_size[0]=25
    fig_size[1]=25
    plt.bar(index,T_values,width=1.1,color=colors)
    plt.xticks(index,label,fontsize=20,rotation=90)
    plt.xlabel('Countries',fontsize=20)
    plt.ylabel('Number of people killed',fontsize=20)
    plt.title('Number of people killed Countriwise',fontsize=20)
    st.pyplot(fig)
    