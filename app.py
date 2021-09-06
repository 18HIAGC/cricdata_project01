# -*- coding: utf-8 -*-
# =============================================================================
# Created on Tue Oct 21, 2020
# Last Update: 06/09/2021
# Script Name: streamlit_cricdata_app_v0_4.py
# Description: ODI cricket data analysis using Python and Streamlit
# Current version: ver0.4 (Streamlit 0.86)
# Docs : https://www.streamlit.io/
#
# @author: 18HIAGC
# Acknowledgements: Stephen Rushe (CricSheet.org - cricket scorecard data)
# =============================================================================

# Changes in version 0.4:
#1. Updated df formatting: Date field
#2. Added form and submit button
#3. Updated plot1 - new colours and plot 2, switched to Altair module
#7. Created data download link

#%% Part 1: Imports

import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from datetime import datetime
import base64
# from base64 import b64encode

file_dir = "C:/Users//Nitesh/Documents/Dev/PythonEnvs/python_cricket/data/"
csv_st_cs = 'cricsheet_stdata_ODI.csv'
csv_st_ssn = 'cricsheet_stdata_ODI_season_grp.csv'


#%% Part 2 : Functions - Read CricSheet Data & Get Download Link

@st.cache
def read_cric_csv():
    # Dataframe for cricsheet 50 over innings file
    df_cs = pd.read_csv(file_dir+csv_st_cs, parse_dates=['Date'])
    # Dataframe for season delivery summary file
    df_ssn = pd.read_csv(file_dir+csv_st_ssn)
    # df_ssn = df_ssn.astype({'IHD': str})
    return df_cs, df_ssn

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = new_df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    # href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
    href = f'<a href="data:file/csv;base64,{b64}" download="data.csv" target="_blank">Download csv file</a>'
    return href

#%% Part 3 : Page Setup (set_page_config), Title and Opening paragraph

st.set_page_config(
    page_title="ODI Cricket Data Viewer",
	page_icon="🏏",
	layout="wide",
	initial_sidebar_state="expanded")

st.title('🏏 ODI Cricket : 30 Over Score Predictions')

"""
### The common assumption when watching an ODI match is that the score at \
(or around) the 30 over mark can be doubled to predict the final score at the \
50 over mark.

### But is this accurate and is it a stable trend?

### The following analysis uses match data starting from the 2003-2004 season \
till the present to answer this question.
"""

with st.container():

    # Display df_cs data
    with st.expander(label='Instructions', expanded=False):
        """### :book: Instructions:"""
        st.markdown('- Make selections for seasons and teams on the User Input sidebar to the left')
        st.markdown('- Your selections update the interactive graph and table')


#%% Part 3 : Loading data

# Call function: Read CricSheet Data
data_load_state = st.text('Loading data...')
df, df_ssn = read_cric_csv()
df_full50 = df[df['Full_50'] == 'Y']

# round to one decimal place(s) in python pandas
pd.options.display.float_format = '{:.1f}'.format
data_load_state.text('')

# fiter Data
# find max (latest available match) date/teams/venue/season
find_max_date = find_max_date = df_full50['Date'].iloc[-1]
max_date = datetime.strftime(find_max_date, '%b %d, %Y')

max_team1 = df_full50['Batting_Team'].iloc[-1]
max_team2 = df_full50['Opposition'].iloc[-1]
max_venue = df_full50['Venue'].iloc[-1]
min_season = df_full50['Season'].iloc[0]
max_season = df_full50['Season'].iloc[-1]

# Column Multi Select / SelectBox
df_teams = list(np.sort(df_full50['Batting_Team'].unique()))
df_season = list(np.sort(df_full50['Season'].unique()))


#%% Part 5 : Display filters in sidebar


with st.sidebar.form(key='sidebar_form'):
    st.subheader('Make selection & click Submit')

    # Sidebar - Start/End Slider: Seasons
    start_season, end_season = st.select_slider('Select start & end season:',
                                                help='drag the beginning and '\
                                                'end points of the slider to '\
                                                'select start and end season',
                                                options=df_season,
                                                value=(min_season, max_season))

    teams_top10 = ['Australia', 'Bangladesh', 'England', 'India',
                   'New Zealand', 'Pakistan', 'South Africa', 'West Indies']

    # Sidebar - Multiselect: Team
    team = st.multiselect(label='Add/Remove Batting Teams (default: top 8 teams):',
                          help='open the dropdown menu on the right to add items, '\
                          'click on the "x" to remove an item',
                          options=df_teams, default=teams_top10)

    # Filter dataframe
    new_df = df_full50[(df_full50['Batting_Team'].isin(team))
                  & (df_full50['Season'] >= start_season)
                  & (df_full50['Season'] <= end_season)]

    submit_button = st.form_submit_button(label=' Submit ',
                                          help='Submit selections made for season and team')


#%% Part 6.1 : Adding a visualisation - Plot 1

latest_match = ':information_source: Latest available match: **' + max_team1 + \
            '** vs **' + max_team2 + '** at **'+ max_venue + '** on '+ max_date

selected_seasons = ':calendar: You selected playing seasons between **' + start_season + \
            '** and **'+ end_season + '**'

st.info(latest_match + '\n\n' + selected_seasons)

st.subheader('Delivery Number at halfway point of a completed 50 over ODI innings (avg=29.2 overs)')

base = alt.Chart(new_df).properties(
        width=900,
        height=650,
        # title='Delivery Number at halfway point',
        # background='#aab7b8',
        ) #.add_selection(selector)


color_scale = alt.Scale(
    domain=['Afghanistan', 'Africa XI', 'Asia XI', 'Australia', 'Bangladesh', 'Bermuda',
    'Canada', 'Denmark', 'England','Hong Kong', 'India', 'Ireland', 'Italy', 'Kenya',
    'Malaysia', 'Namibia', 'Nepal', 'Netherlands', 'New Zealand', 'Oman', 'P.N.G.', 'Pakistan',
    'Scotland', 'South Africa','Sri Lanka', 'U.A.E.', 'U.S.A.', 'Uganda', 'West Indies', 'Zimbabwe'],

    range=['Blue', 'DarkGreen', ' LightBlue', 'Gold', '#006747', 'Blue',
    'Red', 'Red', 'Navy', 'Green', 'SkyBlue', '#169b62', 'Blue', 'DarkGreen',
    'Yellow', 'Blue', 'Blue', 'OrangeRed', 'Black', 'Red', 'Black', 'Lime',
    'Blue', '#007a4d', 'DarkBlue', 'Grey', 'Blue', 'Yellow', '#7b0041', 'Red'],
)

scatterplot = base.mark_point(filled=True, size=100, opacity=0.7
                              ).encode(
        x=alt.X('Date:T',
                title = 'Match Date'),
                # axis=alt.Axis(values=)),
        y=alt.Y('Half_Del:Q',
                title = 'Halfway Delivery',
                scale=alt.Scale(zero=False)),
                # scale=alt.Scale(domain=[18,42])),
                # axis=alt.Axis(values=ticks)),

        color=alt.Color('Batting_Team:N', scale=color_scale),
        tooltip=['Batting_Team', 'Opposition', 'Date', 'Half_Del', 'Venue', 'Winner?']
).interactive()

rule = base.mark_rule(color='red', opacity=0.8).encode(
    y='mean(Half_Del):Q',
    size=alt.value(5),
    tooltip=['mean(Half_Del)']
)

st.altair_chart(scatterplot + rule)


#%% Part 6.2 : Adding a visualisation - Plot 2

"""
### On average 29.2 overs are been bowled when the halfway mark (in terms of final \
score) is reached in a completed 50 over innings. But this mark has varied over the years. \
The peak was around the 2014-2015 season and continued to the 2015 World Cup.
"""

# print(df_ssn.info(),df_ssn)

base2 = alt.Chart(df_ssn).properties(
            width=800,
            height=450)

plot2_1 = base2.mark_line(interpolate='monotone', size=8,
                          opacity=1, color='red').encode(
            x = alt.X('Season:N'),
            y = alt.Y('IHD:Q',
                      title = 'Avg. Halfway Delivery',
                      # axis=alt.Axis(values=['168', '174', '185', '190']),
                      axis=alt.Axis(values=[21,22,23,24,25,26,27]),
                      scale=alt.Scale(domain=[21, 27]),
                      )
            ).properties(width=800,
                         height=450)

plot2_2 = base2.mark_bar(size=15, opacity=0.5).encode(
            # .transform_filter('datum.Season == ['2005', '2018']')
            x = alt.X('Season:N'),
            y = alt.Y('IHD:Q'),
            tooltip=['Season', 'IHD'],
            ).interactive()

st.altair_chart(plot2_1 + plot2_2)


#%% Part 7 : Display df data

with st.container():

    # Display df_cs data
    with st.expander(label='Show/Hide raw data', expanded=True):

    # if st.checkbox('Show raw data'):
        st.subheader(':memo: ODI innings raw data')
        st.write('> Explore the data for every completed 50 over innings on ' \
                 'selected playing seasons between **', start_season, \
                 '**and**', end_season ,'**')
        st.info(':information_source: This table is interactive. Select options on the sidebar to customise')

        # Display data table
        st.write(new_df.style.format({'Final_Del': '{:.1f}', 'Half_Del': '{:.1f}','Date': '{:%Y/%m/%d}'}))

        # download_link
        st.markdown(get_table_download_link(df), unsafe_allow_html=True)


#%% Part 8 : Display Acknowledgements


# """### Mapping of halfway delivery number for ODI batting innings"""
# st.write('Mapping of halfway delivery number for innings between', start_season, 'and', end_season)


"""## **Acknowledgements**
Data downloaded from: *[Cricsheet.org](https://cricsheet.org/)*.
> Cricsheet is maintained by __*Stephen Rushe*__ and provides freely-available structured
> ball-by-ball data for international and T20 League cricket matches.
>
>Find Cricsheet on Twitter: *[@cricsheet](https://twitter.com/cricsheet)*
"""

