# -*- coding: utf-8 -*-
# =============================================================================
# Created on Tue Oct 21, 2020
# Last Update: 11/04/2021
# Script Name: streamlit_cricdata_app.py
# Description: ODI cricket data analysis using Python and Streamlit
#
# Docs : https://www.streamlit.io/
#
# @author: 18HIAGC
# Acknowledgements: Stephen Rushe (CricSheet.org - cricket scorecard data)
# =============================================================================

#%% imports

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

file_dir = './data/'
# cricsheet file formattted for use in streamlit app (only full 50 over innings included)
csv_st_cs = 'cricsheet_stdata_ODI.csv'
csv_st_ssn = 'cricsheet_stdata_ODI_season_grp.csv'

#%% Part 1 : Page Setup (set_page_config)

st.set_page_config(
    page_title="ODI Cricket Data Viewer",
	page_icon="🏏",
	layout="wide",
	initial_sidebar_state="expanded")


#%% Part 2 : Read CricSheet data (read_cric_csv() function)

@st.cache
def read_cric_csv():
    # Dataframe for cricsheet 50 over innings file
    df_cs = pd.read_csv(file_dir+csv_st_cs, parse_dates=['Date'])
    # Dataframe for season delivery summary file
    df_ssn = pd.read_csv(file_dir+csv_st_ssn)
    return df_cs, df_ssn

df, df_ssn = read_cric_csv()

# df['Batting_Team'].value_counts()

# round to one decimal place(s) in python pandas
pd.options.display.float_format = '{:.1f}'.format

#%% Part 3 : Sidebar widgets for season, team selection (show_data() function)

# @st.cache
def show_data():
    """ define sidebar selection widets and the Plotly fig1 & 2 for display"""

    # find max (latest available match) date/teams/venue/season
    find_max_date = df.iloc[-1, 11]
    max_date = datetime.strftime(find_max_date, '%b %d, %Y')

    max_team1 = df.iloc[-1, 1]
    max_team2 = df.iloc[-1, 2]
    max_venue = df.iloc[-1, 12]
    min_season = df.iloc[1, 10]
    max_season = df.iloc[-1, 10]

    # Column Multi Select / SelectBox
    df_teams = list(np.sort(df['Batting_Team'].unique()))
    df_season = list(np.sort(df['Season'].unique()))

    # Sidebar Header
    st.sidebar.header('User Inputs')

    st.sidebar.write('Last match available: :us: :gb: :nl: :za:', max_team1, ' vs ', max_team2,\
                     ' at ', max_venue, ' on ', max_date)

    # Sidebar - Start/End Slider: Seasons
    start_season, end_season = st.sidebar.select_slider(
        'Select a range of seasons',
        options=df_season,
        value=(min_season, max_season))

    teams_top10 = ['Australia', 'Bangladesh', 'England', 'India', 'New Zealand',
                   'Pakistan', 'South Africa', 'Sri Lanka', 'West Indies', 'Zimbabwe']
    # Sidebar - Multiselect: Team
    team = st.sidebar.multiselect(label='Add/Remove Batting Teams (default: top 10 teams)',
                            options=df_teams, default=teams_top10)

    # Filter dataframe
    new_df = df[(df['Batting_Team'].isin(team))
                  & (df['Season'] >= start_season)
                  & (df['Season'] <= end_season)]

    # Plotly scatterplot
    fig1 = px.scatter(new_df, x ='Date',y='Half_Del', color='Batting_Team',
                      title='Delivery Number at halfway point of a full ODI innings (avg=29.2 overs)',
                      labels={
                      'Half_Del': 'delivery no.',
                      'Batting_Team': 'Batting Team'
                      })
    fig1.update_layout(shapes=[
                        dict( type= 'line',
                              xref= 'paper', x0= 0, x1= 1,
                              yref= 'y', y0= 29.2, y1= 29.2,
                            ),
                        ])

    fig2 =  px.bar(
            data_frame=df_ssn,
            x='Season',
            y='IHD',
            range_y=[27,32],
            labels={
                    'IHD': 'delivery no.'
                    })

    fig2.update_layout( title='Average halfway delivery number per season',
                        template='seaborn')

    return new_df, start_season, end_season, fig1, fig2

new_df, start_season, end_season, fig1, fig2 = show_data()


#%% Part 4 : Display Markdown text and df
"""
# 🏏 ODI Cricket : 30 Over Score Predictions
### The common assumption when watching an ODI match is that the score at \
(or around) the 30 over mark can be doubled to predict the final score at the \
50 over mark.

### But is this accurate and is it a stable trend?

### The following analysis uses match data starting from the 2003-2004 season \
till the present to answer this question.

### Instructions:
- Make selections for seasons and teams on the User Input sidebar to the left
- Your selections update the interactive graph and table
"""

# st.write('### Selected Season : ', selected_season)
st.write('You selected playing seasons between', start_season, 'and', end_season)

# """### Mapping of halfway delivery number for ODI batting innings"""
st.write('Mapping of halfway delivery number for innings between', start_season, 'and', end_season)

# Plot fig1
st.plotly_chart(fig1)
# Display data table
st.write(new_df.style.format({'Final_Del': '{:.1f}', 'Half_Del': '{:.1f}'}))

"""
### On average 29.2 overs have been bowled when the halfway mark (in terms of final \
score) is reached in an innings. But this mark has varied over the years. The peak \
was around the 2014-2015 season and continued to the 2015 World Cup.

"""
# Plot fig2
st.plotly_chart(fig2)
"""## **Acknowledgements**
Data downloaded from: *[Cricsheet.org](https://cricsheet.org/)*.
> Cricsheet is maintained by __*Stephen Rushe*__ and provides freely-available structured
> ball-by-ball data for international and T20 League cricket matches.
>
>Find Cricsheet on Twitter: *[@cricsheet](https://twitter.com/cricsheet)*
"""
