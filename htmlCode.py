
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on Thu Aug  4 13:39:17 2022

@author: bjorn
'''
# Libraries
from plotly import graph_objects as go
import plotly.express as px
import pandas as pd
import dash
from dash.dependencies import Input, Output
from random import choice, random
from dash import Dash, html, dcc 
from plotly.subplots import make_subplots
from PIL import Image
import numpy as np

veganGreen = 'rgb(16,114,60)' # Light-green for the vegan color option !!! Change for real color
veggieGreen = 'rgb(140,190,84)' # Dark-green for the vegetarian color option !!! Change for real color


# Load Veggie Data

df = pd.read_csv("kv21_trimmet_98.csv",
                 dtype={"fips": str})

df_sim = pd.read_excel("data_sim.xlsx",
                 dtype={"fips": str})
df = df.fillna(0) # replace NA values with 0
#df_nameIndex = df.set_index("Navn")
df["Candidate"] = [df['Navn'][i]+f" ({df['Parti'][i][:2]})" for i, x in enumerate(df["Navn"])]
df_nameIndex = df.set_index("Candidate")
# Tilføjer en randomiseret kostkolonne
df_nameIndex["Kost"] = list(np.random.randint(low=1, high=6,size=len(df_nameIndex)))
kost_dict = {5: "Kødspiser", 4:"Fleksitar",3:"Pescetar", 2: "Vegetar",1:"Veganer", 6: "Ønsker ikke at svare"}
kost_color = {"Kødspiser":"red", "Fleksitar":"turquoise","Pescetar":"blue", "Vegetar":veggieGreen,"Veganer":veganGreen
              ,"Ønsker ikke at svare" : "grey"}
df_nameIndex["Kost"] = [kost_dict[x] for x in df_nameIndex["Kost"]]
df_nameIndex["Kost_color"] = [kost_color[x] for x in df_nameIndex["Kost"]]



#%% List of the five new columns
q1Answers = ['Daginstitutioner','Hospitaler, psykiatrien','Plejehjem, plejecentre og offentlig madudbringning til ældre', 'Offentlige arbejdspladser', 'ALLE offentlige institutioner']
#Adding the five columns, if not allready added
if q1Answers[0] not in df.columns:
    df = df.reindex(columns = df.columns[0:5].tolist() + q1Answers + df.columns[5:].tolist())
    
# First value adds random boolean(0,1) to "Alle offentlige institutioner" column.
# Second value adds random boolean (0,1) to the remaining four columns,
# depending on the boolean from the "Alle offentlige institutioner" column. 
q1Questions = df.columns[4:9]
for i in range(0,len(df)):
    value = 1 if random() > 0.7 else 0
    df.loc[i,q1Questions[4:5]] = value
    for col in q1Questions[0:4]:
        value2 = 1 if random() > 0.5 else 0
        if value == 0:
            df.loc[i,col] = value2
        else: 
            df.loc[i,col] = 0
#%% Definitions from the main-file

# This codeblock contains the variables for the dash-board
#Style
textBlack = 'rgb(0,0,0)' #Black for text

H2Style = {"fontSize": "25px", 
            "color": veganGreen,
            "text-align": "center",
            'background': 'white',
            'font-family': 'Calibri',
            "margin-top": "20px", 
            "margin-bottom":'10px',
            "padding":"1.5%"}

#Lists
parties = [] # !!! Add list according to values from survey
candidates = [] # !!! Add list according to values from survey
questions = df.columns[10:] # !!! Add questions to this list
kommuneList = df["Kommune"].unique()  # !!! change list according to values from survey
logo_img = Image.open("dvf_logo.png")

#%% function with html code


def CodeHTML(textBlack, veganGreen, labelsKommuneList):
    headline = 'Vegetarisk folketingsvalg 2022'
    subheadline = '''Det grønne valg 2022 er Dansk Vegetarisk Forenings 
    valgundersøgelse forud for folketingsvalget. 
    Her kan du finde ud af, hvad dine kandidater fra din storkreds vil gøre
    for at fremme grønne måltider i kommunens køkkener – 
    og på andre måder fremme en omstilling af mad og landbrug.'''
    component = html.Div([
        html.Div(
            children=[
                html.Img(
                    src = logo_img,
                    height = "90px"
                    ),
                html.H1(
                    children= headline, 
                    className='header-title',
                    style={'color': veganGreen,
                           'background': 'white',
                           'text-align': 'center',
                           'font-family': 'Calibri',
                           'font-weight': '6200',
                           'margin-top': '-10px',
                           'fontSize': '60px'}
                ),
                html.P(
                    children= subheadline,
                    className='header-description',
                    style={'fontSize': '18px',
                           'color': textBlack,
                           'text-align': 'center',
                           'background': 'white',
                           'font-family': 'Calibri',
                           'margin-top': '-40px',
                           'margin-bottom':'1px',
                           'padding':'1.5%'},
                ),
            ], className='header', style={'background': 'white'}
            ),
        html.H2(
            children= 'Vælg en storkreds',
            className="header-description",
            style=H2Style,
            ),
        html.Div(
            children= [
                dcc.Dropdown(id='kommuneValg',
                             options= labelsKommuneList,
                             value=kommuneList[0],
                             style={"margin-bottom": '50px'},
                             ),
                dcc.Graph(id="candidate_all"),
                ]),
        html.Div(
            children =[
                html.H2(
                    children= 'Vælg et spørgsmål',
                    className="header-description",
                    style=H2Style
                    ),
                html.Div([
                    dcc.RadioItems(questions,
                                  value = questions[0],
                                  labelStyle={'display': 'block'},
                                  id = 'questions')
                    ]),
                ]),
        html.Div([
            
            dcc.Graph(id="sunburst"),
            dcc.Graph(id="piecharts")
            ])
        
        ],style={'background-color':'white','margin':'2%','display':'inline-block'})
    return component

app = dash.Dash()
app.layout = CodeHTML(textBlack, veganGreen, kommuneList)

# dash code
# Start the dash-board
server = app.server

"""
lollipop-graph municipality
The following callback takes the choice of municipality as input an creates a subsection of 
the dataframe, this is then used to make a lollipop graph for the scores of the candidates
in that municipality
"""
@app.callback(
    Output("candidate_all", "figure"),
    Input("kommuneValg","value"))
def lollipop_all(value):
    fig = go.Figure()
    df_temp = df_nameIndex[df_nameIndex["Kommune"]==value]
    df_temp = df_temp.sort_values("Score", ascending = False)

    
    
    for i, mean in enumerate(df_temp["Score"]):

        candidate = df_temp.index[i]
        fig.add_trace(go.Scatter(x=[i,i],y=[0,mean],
                                 marker_size = [0,12],
                                 marker_color = df_temp["Kost_color"][i],
                                 line=go.scatter.Line(color=veggieGreen),
                                 hovertext=[df_temp.loc[candidate]["Parti"],df_temp.loc[candidate]["Parti"]],
                                 showlegend=False,
                                 hoverinfo=["none","x+y+text"],

                                 )
                      )
    for k, v in kost_color.items():
        fig.add_trace(go.Scatter(x=[0],y=[0],
                                 marker_size = [0],
                                 marker_color = v,
                                 name=k
                                ))
    fig.update_layout(legend= {'itemsizing': 'constant',
                               # "itemsymbol":"circle"
                               })
    
    fig.add_hline(y=df_temp["Score"].mean(), 
            line_width=0.5, 
            line_dash="dash", 
            line_color=veggieGreen,
            annotation_text="Kommune gennemsnit", 
            annotation_position="bottom right")
    
    
    
    tickvals_ = list(range(len(df_temp)))
    ticktext_ = list(df_temp.index)
    fig.update_layout(
        xaxis = dict(
            tickmode = "array",
            tickvals = tickvals_,
            ticktext = ticktext_),
        title = {"text":f"Kandidater for {value}"}
        )
    return fig 

"""
Candidates from the kommune/storkreds
The following callback takes a municipality as input from a dropdown, and from this it creates an output of the 
candidates for that municipality.
This output is sent as options for the Dropdown menu below(in the html code), where candidates for the lollipop-graph
are chosen.
"""
@app.callback(
    Output("Candidate_dropdown", 'options'),
    Input('kommuneValg', 'value'))
def save_data(value):
    return [{"label":x,"value":x} for x in df_nameIndex[df_nameIndex["Kommune"]==value].index]


# """
# Lollipop-graph candidates
# The following callback takes multiple dropdown inputs, where the user picks one or several candidates, that are then 
# visualized in a lollipop-graph, that is created in the callback and sent back as output. 
# """
# @app.callback(
#     Output("Lollipop_candidates", "figure"),
#     Input("Candidate_dropdown", "value")
#     )
# def update_lollipop(value):
#     valueList = list(value)
#     fig = go.Figure()
#     df_temp = df_nameIndex.loc[valueList]

#     df_temp = df_temp.sort_values("Score", ascending = False)

    
#     for i, mean in enumerate(df_temp["Score"]):
#         fig.add_trace(go.Scatter(x=[i,i],y=[0,mean], 
#                                  marker={"color":veggieGreen,"size":markerSize},
#                                 line=go.scatter.Line(color=veggieGreen),
#                                 showlegend=False))
    
#     tickvals_ = list(range(len(df_temp)))
#     ticktext_ = list(df_temp.index)
#     fig.update_layout(
#         xaxis = dict(
#             tickmode = "array",
#             tickvals = tickvals_,
#             ticktext = ticktext_),
#         xaxis_range=[-1,len(df_temp)])
#     return fig


"""
Piecharts for question, kommune and denmark
The following graph is a subplot of two subplots. Both shows the distribution of 
answers to the question, that is chosen earlier. One shows the distrubution for 
the chosen kommune and the other for all of the country.
IMPORTANT: Doesn't work correctly at the moment
"""
@app.callback(
    Output("piecharts","figure"),
    [Input("kommuneValg", "value"),Input("questions", "value")]
    )
def update_piechart(kommune, question):
    df_temp =  df_nameIndex[df_nameIndex["Kommune"]==kommune]
    df_temp = df_temp.sort_values(question, ascending = False)
    
    
    fig_pie = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
    
    # labels for piechart - kommune
    value_labels = {0:"Uenig", 1:"Delvist Enig", 2:"Enig"}
    answers_kommune = pd.Series([value_labels[x] for x in df_temp[question]], 
                                  index =df_temp.index)
    labels_kommune = list(answers_kommune.unique())
    
    # Value for kommune
    df_pie = df_temp.groupby(df_temp[question]).count()
    value_kommune = df_pie["Score"]
    
    # Colors kommune
    color_dict = { "Enig":'rgb(15,122,55)',"Delvist Enig": 'rgb(169,220,163)',"Uenig":'rgb(218,241,212)'}
    colors_pie = {}
    for answer in labels_kommune:
        colors_pie[answer] = color_dict[answer]
    
    
    fig_pie.add_trace(go.Pie(labels=labels_kommune, 
                                values=value_kommune, 
                                hole=0.6,
                                marker_colors = list(colors_pie.values()),
                                hoverinfo=["x+y+text"]
                                ),row = 1,col = 1)
    
    
    df_pie2 = df_nameIndex.groupby(df_nameIndex[question]).count()
    values = df_pie2["Score"]
    labels = ["Uenig", "Delvist Enig", "Enig"]
    colors = ['rgb(218,241,212)','rgb(169,220,163)','rgb(15,122,55)']
    
    
    fig_pie.add_trace(go.Pie(labels=labels, 
                                values=values, 
                                hole=0.6,
                                marker_colors = colors
                                ),row = 1,col = 2)
    
    
    fig_pie.add_trace(go.Sunburst(
        labels=[kommune],
        parents=[""],
        values=[1],
        ), row = 1, col=1)
    
    
    fig_pie.add_trace(go.Sunburst(
        labels=["Alle kandidater"],
        parents=[""],
        values=[1],
        ), row = 1, col=2)
    
    fig_pie.update_layout(
        autosize=False,
        width=1200,
        height=720)
    return fig_pie



"""
Sunburst, answers hierachial with candidates
The sunburst graph shows a sunburst graph with two layers, the inner layer is the
possible answers, and the outer is the candidates that has given the answer respectively
"""
@app.callback(
    Output("sunburst","figure"),
    [Input("kommuneValg", "value"),Input("questions", "value")]
    )
def update_sunburst(kommune,question):
    df_temp =  df_nameIndex[df_nameIndex["Kommune"]==kommune]
    df_temp = df_temp.sort_values(question, ascending = False)
    
    # Parents for sunburst
    value_labels = {0:"Uenig", 1:"Delvist Enig", 2:"Enig"}
    parents_candidates = pd.Series([value_labels[x] for x in df_temp[question]], 
                                  index =df_temp.index)
    
    sunburst_parents = []
    for answer in parents_candidates.unique():
        sunburst_parents.append("")
    sunburst_parents.extend(parents_candidates)
    
    # Names for sunburst
    sunburst_names = []
    
    inner_names = list(parents_candidates.value_counts(sort=False).index)
    sunburst_names.extend(inner_names)
    
    candidate_names = list(df_temp.index)
    sunburst_names.extend(candidate_names)
    
    # Values for sunburst
    sunburst_values = []
    
    inner_values = list(parents_candidates.value_counts(sort=False))
    sunburst_values.extend(inner_values)
    
    candidate_values = []
    for candidate in list(df_temp.index):
        candidate_values.append(1)
    
    sunburst_values.extend(candidate_values)
    
    fig = go.Figure()
    
    color_dict = { "Enig":'rgb(15,122,55)',"Delvist Enig": 'rgb(169,220,163)',"Uenig":'rgb(218,241,212)'}
    colors_sunburst = {}
    for answer in parents_candidates.unique():
        colors_sunburst[answer] = color_dict[answer]
    
    data = dict(
        names=sunburst_names,
        parent=sunburst_parents,
        value=sunburst_values)
    
    fig.add_trace(go.Sunburst(
        labels=data['names'],
        parents=data['parent'],
        values=data['value'],
        branchvalues="total",
        marker_colors = list(colors_sunburst.values()),
        insidetextorientation='radial',
        ))
    fig.update_layout(
        autosize=False,
        width=1200,
        height=720)
    return fig


if __name__ == '__main__':
    app.run_server()