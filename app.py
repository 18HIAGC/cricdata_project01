# -*- coding: utf-8 -*-
# =============================================================================
# Created on Tue Oct 21, 2020
# Last Update: 2025/03/05
# Script Name: streamlit_cricdata_app_v1.0.py
# Description: ODI cricket data analytics using Python and Streamlit
#
# Current version: ver1.0 (Streamlit 1.43.2)
# Docs : https://www.streamlit.io/
#
# @author: 18HIAGC
# Acknowledgements: Stephen Rushe (CricSheet.org - cricket scorecard data)
# =============================================================================

# %% Part 1: Imports

import altair as alt
from datetime import datetime
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

APP_VERSION = '1.0'

DATA_DIR = './data/'
STREAMLIT_DATA_FILE = DATA_DIR + 'cricsheet_stdata_ODI.csv'

TEAMS_TOP9 = ['Australia', 'Bangladesh', 'England', 'India',
               'New Zealand', 'Pakistan', 'South Africa', 'Sri Lanka', 'West Indies']

exec_type = 'TESTING'   # 'TESTING' or 'PRODUCTION'


# %% Part 1.2 - Credentials

gsheet_name = 'cricsheet_stdata_ODI'

# %% Part 2.1 : Page Setup (set_page_config)

st.set_page_config(
    page_title="ODI Cricket Data Explorer",
	page_icon="🏏",
	layout="wide",
	initial_sidebar_state="expanded",
    menu_items={'About': "streamlit cricdata app (ver " + APP_VERSION + " - 2025-03-20) :panda_face:\
                \n added: Updated source data \
                \n added: Infograhic Image (Avg. Halfway Del.)"
                }
    )


# %% Part 2.2 : Opening Paragraph & Instructions
"""
# ODI Cricket : The 30 Over Prediction 🏏
### The common assumption when watching an ODI match is that the score at \
(or around) the 30 over mark can be doubled to predict the final score at the \
50 over mark. But is this accurate and is it a stable trend?

The following analysis uses match data starting from the 2003-2004 season \
till the present to answer this question.

N.B. Afghanistan matches are missing from the source data.
*[Explanation for withholding of Afghanistani matches](https://cricsheet.org/article/explanation-for-withholding-of-afghanistani-matches/)*
"""

# %% Part 3 : Functions

@st.cache_data
def csv2df(data_file):
    """ Function to fetch cricdata all summary data from a .csv file """
    df_cs2 = pd.read_csv(data_file)
    df_cs2['Date'] = pd.to_datetime(df_cs2['Date'])

    return df_cs2

@st.cache_data
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

@st.cache_data
def season_grp_calc(df_in1):
    """ Function to calculate season average delivery number at which half of
        total runs is reached.
        Parameters: df_in1 (DataFrame, df returned by read_cric_csv())
        Returns: season_grp_AHB (DataFrame), all_AHD (string of delivery numbers)
    """

    # SELECT Season, mean(Half_Ball) FROM df_sahd GROUP BY Season
    df_sahd = df_in1.loc[:, ['Season', 'Half_Del', 'Half_Ball']]
    # df_sahd.reset_index(inplace=True, drop=True)

    # df_sahd (season avg half-del df) GROUP BY Season
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
    # all_AHD = str(int(all_AHB // 6) + (int(all_AHB % 6) / 10))
    all_AHD = str(int(all_AHB.iloc[0] // 6) + (int(all_AHB.iloc[0] % 6) / 10))

    return season_grp_AHB, all_AHD

@st.cache_data
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
        domain=['Africa XI', 'Asia XI', 'Australia', 'Bangladesh', 'Bermuda',
        'Canada', 'Denmark', 'England','Hong Kong', 'India', 'Ireland', 'Italy', 'Kenya',
        'Malaysia', 'Namibia', 'Nepal', 'Netherlands', 'New Zealand', 'Oman', 'P.N.G.', 'Pakistan',
        'Scotland', 'South Africa','Sri Lanka', 'U.A.E.', 'U.S.A.', 'Uganda', 'West Indies',
        'Zimbabwe'],

        range=['DarkGreen', ' LightBlue', 'Gold', '#006747', 'Blue',
        'Red', 'Red', 'Navy', 'Green', 'SkyBlue', '#169b62', 'Blue', 'DarkGreen',
        'Yellow', 'Blue', 'Blue', 'OrangeRed', 'Black', 'Red', 'Black', 'Lime',
        'Blue', '#007a4d', 'DarkBlue', 'Grey', 'Blue', 'Yellow', '#7b0041',
        'Red'],
    )

    scatterplot = base.mark_point(filled=True, size=100, opacity=0.7
                                  ).encode(
            x=alt.X('Date:T',
                    title = 'Match Date'),
                    # axis=alt.Axis(values=)),
            y=alt.Y('Half_Del:Q',
                    title = 'Halfway Delivery Over',
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

@st.cache_data
def display_plot2(df_in3):
    """ Function to display Altair line and bar graph plots.
        Parameters: df_in3 (DataFrame with ODI innings info grouped by season)
        Returns: None.
    """
    base2 = alt.Chart(df_in3).properties(
                width=800,
                height=450)

    plot1 = base2.mark_bar(size=15, opacity=0.6).encode(
                x = alt.X('Season:O'),
                y = alt.Y('Half_Del:Q',
                          title = 'Avg. Halfway Delivery',
                          # axis=alt.Axis(values=['168', '174', '185', '190']),
                          axis=alt.Axis(values=[26,27,28,29,30,31,32]),
                          scale=alt.Scale(domain=[26, 32]),
                          ),
                color=alt.condition(
                            alt.datum.Season == '2014-2015',
                            alt.value('orange'),
                            alt.value('steelblue')
                ),
                tooltip=['Season:O', 'Half_Del:Q'],
                ).interactive()

    plot2 = base2.mark_line(interpolate='monotone', size=5,
                              opacity=0.5, color='yellow').encode(
                x = alt.X('Season:O'),
                y = alt.Y('Half_Del:Q',
                          title = 'Avg. Halfway Delivery',
                          )
                )

    st.altair_chart(plot1 + plot2)

@st.cache_data
def html_counter(starter, target):

    my_html2 = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <style>
                div.a {{
                  /*white-space: nowrap; */
                  width: 250px;
                  overflow: hidden;
                  text-overflow: clip;
                  border: 1px solid #000000;
                  font-family:Verdana;
                  font-size: 30px
                }}

                div.b {{
                  /*white-space: nowrap; */
                  width: 250px;
                  overflow: hidden;
                  text-overflow: clip;
                  border: 1px solid #000000;
                  font-family:Verdana;
                  font-size: 50px
                }}
            </style>
        </head>

        <body style="text-align:left; margin: auto; border: 1px solid #000000;">
            <div class="a">ODI COUNT</div>
            <div class="b"; id="counter">
        		<!-- counts -->
        	</div>

            <script>
                let counts = setInterval(updated, 50);
                let starter = {0};
                const target = {1};
                let count = document.getElementById("counter");

                function updated() {{
                    starter += 1;
                    count.innerHTML = starter;

                    if (starter === target) {{
                        clearInterval(counts);
                    }}
                }}
            </script>
        </body>
        </html>
        """.format(starter, target)

    return my_html2


# %% Part 4 : Loading Data

# Call functions: Read csv file and calc season group data
data_load_state = st.text('Loading data...')

df_cs = csv2df(STREAMLIT_DATA_FILE)

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

# df_full50['Season'] = df_full50['Season'].astype(str)
# df_full50['Season'] = pd.to_datetime(df_full50['Date'])

df_season = list(df_full50['Season'].sort_values().unique())
# df_season = [x.replace('-20', '-') for x in df_season]

# %% Part 5 : Stats Columns

# calc match stats
match_count = df_cs['Match_ID'].nunique()
season_count = df_cs['Season'].nunique()
inn50_count = df_cs['Match_ID'].count()

st.subheader('Stats')
components.html(html_counter(match_count - 50, match_count), width=250, height=120,)

st.header('_Avg Halfway Delivery_')
st.header('_{}_'.format(float(all_avg_ihd)) )


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
    team = st.multiselect(label='Add/Remove Batting Teams (default: top 9 teams):',
                          help='open the dropdown menu on the right to add items, '\
                          'click on the "x" to remove an item',
                          options=df_teams, default=TEAMS_TOP9)

    # Filter dataframe
    selection_df = df_full50[(df_full50['Batting_Team'].isin(team))
                  & (df_full50['Season'] >= start_season)
                  & (df_full50['Season'] <= end_season)]

    submit_button = st.form_submit_button(label=' Submit ',
                    help='Submit selections made for season and team',
                    type= 'primary')


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
        st.markdown('Delivery at which half of all runs for that 50 over innings \
            were scored. e.g. If the innings score after 50 overs was 200 runs \
            and 100 runs were scored after 30.1 overs then 30.1 overs is the \
            halfway delivery number.')
        st.markdown('+ Full Innings \ Completed Innings:')
        st.markdown('A completed 50 over ODI innings where all 300 legal \
            deliveries were bowled.')


# %% Part 8 : Display visualisations - Plot 1 & Infographic Image

st.header('Average Delivery Number')
st.write('Delivery Number at halfway point of a completed 50 over ODI innings')

display_plot1(selection_df)


st.header('New Balll and Powerplay Rule Changes')
st.subheader(all_avg_ihd + ' overs are bowled on average before the halfway '\
             'mark (in terms of final score) is reached in a completed 50 over '\
             'innings. But this mark has varied over time. The peak was '\
             'around the 2014-2015 season and continued to the 2015 World Cup. '\
             'After the dropping of the Batting Powerplay rule the averages declined again.')
"""> *[wikipedia: Powerplay(cricket)](https://en.wikipedia.org/wiki/Powerplay_(cricket))*"""

st.image(DATA_DIR + 'avg_halfway_del+PP+NB.png')


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
        st.write(selection_df.style.format(
                                {'Half_Del': '{:.1f}','Date': '{:%Y-%m-%d}'}))
        # st.write(selection_df)


# %% Part 10 : Display Acknowledgements

# """### Mapping of halfway delivery number for ODI batting innings"""
# st.write('Mapping of halfway delivery number for innings between', start_season, 'and', end_season)

"""## **Acknowledgements**
##### Data downloaded from: *[Cricsheet.org](https://cricsheet.org/)*.
> Cricsheet is maintained by __*Stephen Rushe*__ and provides freely-available
> structured ball-by-ball data for international and T20 League cricket matches.
>
> Find Cricsheet on Mastadon :mammoth: : *[@cricsheet@deeden.co.uk](https://social.deeden.co.uk/@cricsheet)*
>
> *[Explanation for withholding of Afghanistani matches](https://cricsheet.org/article/explanation-for-withholding-of-afghanistani-matches/)*
>
##### Questions or Comments? Contact the author via email: 18hiagc@gmail.com
"""