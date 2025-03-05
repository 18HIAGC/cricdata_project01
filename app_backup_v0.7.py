# -*- coding: utf-8 -*-
# =============================================================================
# Created on Tue Oct 21, 2020
# Last Update: 04/03/2022
# Script Name: streamlit_cricdata_app_v0_7.py
# Description: ODI cricket data analysis using Python and Streamlit
#
# Current version: ver0.7 (Streamlit 1.7.0)
# Docs : https://www.streamlit.io/
#
# @author: 18HIAGC
# Acknowledgements: Stephen Rushe (CricSheet.org - cricket scorecard data)
# =============================================================================

# %% Part 1: Imports

import altair as alt
from datetime import datetime
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials as sac
import streamlit as st

FILE_DIR = './data/'
CSV_ST_CS = FILE_DIR+'cricsheet_stdata_ODI.csv'

TEAMS_TOP10 = ['Afghanistan', 'Australia', 'Bangladesh', 'England', 'India',
               'New Zealand', 'Pakistan', 'South Africa', 'Sri Lanka', 'West Indies']

gsheet_name = st.secrets.gsheet_name
WSHEET_NUM = 0

# %% Part 2.1 : Page Setup (set_page_config)

st.set_page_config(
    page_title="ODI Cricket Data Viewer",
	page_icon="🏏",
	layout="wide",
	initial_sidebar_state="expanded",
    menu_items={'About': "streamlit cricdata app (ver 0.7 - 2022-03-04) :panda_face:\
                \n added: Google Sheets integration \
                \n added: Infograhic Image (Avg. Halfway Del.)"
                }
    )


# %% Part 2.2 : Opening Paragraph & Instructions
"""
# ODI Cricket Data Viewer 🏏
### The common assumption when watching an ODI match is that the score at \
(or around) the 30 over mark can be doubled to predict the final score at the \
50 over mark.

But is this accurate and is it a stable trend?

The following analysis uses match data starting from the 2003-2004 season \
till the present to answer this question.
"""

# %% Part 3 : Functions

def cred_dict_constructor():
    """ Function to construct the cred_dict (credentials dictionary)
    """
    cred_dict1 = dict(
        type = st.secrets['gcp_service_account']['type'],
        project_id = st.secrets['gcp_service_account']['project_id'],
        private_key_id = st.secrets['gcp_service_account']['private_key_id'],
        private_key = st.secrets['gcp_service_account']['private_key'],
        client_email = st.secrets['gcp_service_account']['client_email'],
        client_id = st.secrets['gcp_service_account']['client_id'],
        auth_uri = st.secrets['gcp_service_account']['auth_uri'],
        token_uri = st.secrets['gcp_service_account']['token_uri'],
        auth_provider_x509_cert_url = st.secrets['gcp_service_account']['auth_provider_x509_cert_url'],
        client_x509_cert_url = st.secrets['gcp_service_account']['client_x509_cert_url']
        )

    return cred_dict1

def gsheet2df(cred_dict1, gsheet_name1, wsheet_num1):
    """ Function to fetch a google sheet and convert it into a df """
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    credentials = sac.from_json_keyfile_dict(cred_dict1, scope)
    client = gspread.authorize(credentials)

    gsheet1 = client.open(gsheet_name1)
    worksheet = gsheet1.get_worksheet(wsheet_num1).get_all_records()

    df_cs1 = pd.DataFrame(worksheet)
    df_cs1['Date'] = pd.to_datetime(df_cs1['Date'])

    return df_cs1

@st.cache
def read_cric_csv(df_cs1):
    """ Functon to read cricsheet_stdata_ODI
        Parameters: df_cs1 (df, cricsheet 50 over file)
        Returns: df_cs, df_full50 (2 DataFrames derived from csv file)
                 match_count1, season_count1, inn50_count1 (int. match stats)
    """
    # calc df for full 50 over matches
    df_full50 = df_cs1[df_cs1['Full_50'] == 'Y']
    df_full50 = df_full50.reset_index(drop=True)
    df_full50 = df_full50.drop(columns=['Final_Del', 'Full_50'])
    df_full50['Season'] = df_full50['Season'].astype(str)

    return df_full50

@st.cache
def season_grp_calc(df_in1):
    """ Function to calculate season average delivery number at which half of
        total runs is reached.
        Parameters: df_in1 (DataFrame, df returned by read_cric_csv())
        Returns: season_grp_AHB (DataFrame), all_AHD (string of delivery numbers)
    """

    # SELECT Season, mean(Half_Ball) FROM df_sahd GROUP BY Season
    df_sahd = df_in1.loc[:, ['Season', 'Half_Del', 'Half_Ball']]
    # df_sahd.reset_index(inplace=True, drop=True)

    # df_sahd (season avg half-del df) group by Season
    # .... df_sahd GROUP BY Season
    season_grp = df_sahd.groupby(df_sahd['Season'])

    # Season Group Avg Haf-Ball : SELECT Season, mean(Half_Ball) ....
    season_grp_AHB = season_grp['Half_Ball'].agg(['mean', 'count']).round(0)
    season_grp_AHB.columns = ['Half_Ball', 'Count']

    # calc inn. half del. no. from inn. half ball count
    season_grp_AHB['Half_Del'] = season_grp_AHB['Half_Ball'] \
                                 .apply(lambda x: int(x//6) + (int(x%6)/10))

    season_grp_AHB = season_grp_AHB.reset_index()
    season_grp_AHB = season_grp_AHB.astype({'Half_Ball' : int, 'Count':int})

    # calc all AHD (Avg. Haf Delivery for all 50 over innnngs)
    all_AHB = df_sahd['Half_Ball'].agg(['mean']).round(0)
    all_AHD = str(int(all_AHB // 6) + (int(all_AHB % 6) / 10))

    return season_grp_AHB, all_AHD

def display_plot1(df_in2):
    """ Function to display Altair scatterplot with ruled line.
        Parameters: df_in2 (DataFrame with ODI innings info)
        Returns: None.
    """
    base = alt.Chart(df_in2).properties(
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
            tooltip=['Batting_Team', 'Bowling_Team', 'Date', 'Half_Del',
                     'Venue', 'Winner']
    ).interactive()

    rule = base.mark_rule(color='red', opacity=0.8).encode(
        y='mean(Half_Del):Q',
        size=alt.value(5),
        tooltip=['mean(Half_Del)']
    )

    st.altair_chart(scatterplot + rule)


# %% Part 4 : Loading Data

# Call functions: Read csv file and calc season group data
data_load_state = st.text('Loading data...')

# construct cred_dict
cred_dict = cred_dict_constructor()

df_cs = gsheet2df(cred_dict, gsheet_name, WSHEET_NUM)

df_full50 = read_cric_csv(df_cs)
df_ssn, all_avg_ihd = season_grp_calc(df_full50)

# round to one decimal place(s) in python pandas
pd.options.display.float_format = '{:.1f}'.format
data_load_state.text('')

# filter Data
# find max (latest available match) date/teams/venue/season
find_max_date = df_cs['Date'].iloc[-1]
max_date = datetime.strftime(find_max_date, '%b %d, %Y')

max_team1 = df_cs['Batting_Team'].iloc[-1]
max_team2 = df_cs['Bowling_Team'].iloc[-1]
max_venue = df_cs['Venue'].iloc[-1]
min_season = df_full50['Season'].iloc[0]
max_season = df_full50['Season'].iloc[-1]

df_teams = list(df_full50['Batting_Team'].sort_values().unique())
df_season = list(df_full50['Season'].sort_values().unique())


# %% Part 5 : Stats Columns

# calc match stats
match_count = df_cs['Match_ID'].nunique()
season_count = df_cs['Season'].nunique()
inn50_count = df_cs['Match_ID'].count()

st.header('Stats')
col1, col2, col3 = st.columns([1,1,1])

col1.subheader('__*ODI Count*__')
col1.subheader('_{}_'.format(match_count) )

col2.subheader('_*Full Inn. Count*_')
col2.subheader('_**{}**_'.format(inn50_count) )

col3.subheader('_Avg Halfway Delivery_')
col3.subheader('_{}_'.format(float(all_avg_ihd)) )


# %% Part 6 : Sidebar : Display filters in sidebar

with st.sidebar.form(key='sidebar_form'):
    st.subheader(':star: Make selection & click Submit')

    # Sidebar - Start/End Slider: Seasons
    SLIDER_HELP = 'drag the beginning and end points of the slider to '\
                  'select first and last season'
    start_season, end_season = st.select_slider('Select start & end season:',
                                                help=SLIDER_HELP,
                                                options=df_season,
                                                value=(min_season, max_season))

    # Sidebar - Multiselect: Team
    team = st.multiselect(label='Add/Remove Batting Teams (default: top 10 teams):',
                          help='open the dropdown menu on the right to add items, '\
                          'click on the "x" to remove an item',
                          options=df_teams, default=TEAMS_TOP10)

    # Filter dataframe
    selection_df = df_full50[(df_full50['Batting_Team'].isin(team))
                  & (df_full50['Season'] >= start_season)
                  & (df_full50['Season'] <= end_season)]

    submit_button = st.form_submit_button(label=' Submit ',
                    help='Submit selections made for season and team')


# %% Part 7 : Display selection info & Instructons

# Display config info selected in sidebar form above
latest_match = ':information_source: Latest available match: **' + max_team1 +\
            '** vs **' + max_team2 + '** at **'+ max_venue + '** on '+ max_date

selected_seasons = ':calendar: You selected playing seasons between **' \
                    + start_season + '** and **'+ end_season + '**'

st.info(latest_match + '\n\n' + selected_seasons)

with st.container():

    # Display df_cs data
    with st.expander(label='Instructions  &  Definitions', expanded=False):
        """### :information_source: Instructions:"""
        st.markdown('- Make selections for seasons and teams on the User Input sidebar to the left')
        st.markdown('- Your selections update the interactive graph and table')

        """### :book: Definitions:"""
        st.markdown('+ Halfway Delivery:')
        st.markdown('Deiivery at which half of all runs for that 50 over innings \
            were scored. e.g. If the innings score after 50 overs was 200 runs \
            and 100 runs were scored after 30.1 overs then 30.1 overs is the \
            halfway delivery number.')
        st.markdown('+ Full Innings \ Completed Innings:')
        st.markdown('A completed 50 over ODI innings where all 300 legal \
            deliveries were bowled.')


# %% Part 8 : Display visualisations - Plot 1 & Infographic Image

st.header('Average Delivery Number')
st.write('Delivery Number at halfway point of a completed 50 over ODI innings'\
             ' (avg=' + all_avg_ihd + ' overs)')

display_plot1(selection_df)


st.header('New Balll and Powerplay Rule Changes')
st.subheader(all_avg_ihd + ' overs are bowled on average before the halfway '\
             'mark (in terms of final score) is reached in a completed 50 over '\
             'innings. But this mark has varied over time. The peak was '\
             'around the 2014-2015 season and continued to the 2015 World Cup. '\
             'After the dropping of the Batting Powerplay rule the averages declined again.')
"""> *[wikipedia: Powerplay(cricket)](https://en.wikipedia.org/wiki/Powerplay_(cricket))*"""

st.image(FILE_DIR + 'avg_halfway_del+PP+NB.png')


# %% Part 9 : Display df data

with st.container():

    # Display df_cs data
    with st.expander(label='Show/Hide raw data', expanded=True):

    # if st.checkbox('Show raw data'):
        st.subheader(':memo: ODI innings raw data')
        st.write('> Explore the data for every completed 50 over innings on ' \
                 'selected playing seasons between', start_season,'and', end_season)
        st.info(':information_source: This table is interactive.'\
                'Select options on the sidebar to customise')

        # Display data table
        # st.write(selection_df.style.format(Half_Del': '{:.1f}','Date': '{:%Y/%m/%d}'}))
        st.write(selection_df)


# %% Part 10 : Display Acknowledgements

# """### Mapping of halfway delivery number for ODI batting innings"""
# st.write('Mapping of halfway delivery number for innings between', start_season, 'and', end_season)

"""## **Acknowledgements**
#### Data downloaded from: *[Cricsheet.org](https://cricsheet.org/)*.
> Cricsheet is maintained by __*Stephen Rushe*__ and provides freely-available
> structured ball-by-ball data for international and T20 League cricket matches.
>
>Find Cricsheet on Twitter :bird: : *[@cricsheet](https://twitter.com/cricsheet)*
"""