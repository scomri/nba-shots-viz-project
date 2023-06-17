import numpy as np
import matplotlib
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
import altair as alt
import matplotlib.gridspec as gridspec
import plotly.express as px
import gzip


def show_viz1_shots_years(df_data_shots):
    # df_data_shots = pd.read_csv('Data/data_viz14.csv.gz', compression='gzip')

    # Filter data by years
    selected_years = st.slider("Select Period of Years", 2000, 2022, (2000, 2022), key='year')
    filtered_data_years = df_data_shots[(df_data_shots['year'] >= selected_years[0]) & (
            df_data_shots['year'] <= selected_years[1])]

    # Calculate shot count average and success rate per year and shot type
    df_avg_shot_count = filtered_data_years.groupby(['year', 'shot_type'])['made'].sum().reset_index()
    df_success_rate = round(
        filtered_data_years.groupby(['year', 'shot_type'])['made'].sum() / filtered_data_years.groupby(
            ['year', 'shot_type'])['team'].count() * 100,
        1)
    df_success_rate = df_success_rate.reset_index(name='success_rate')

    # Create the left plot for shot count average
    left_plot_chart_line = alt.Chart(df_avg_shot_count).mark_line().encode(
        x='year:O',
        y=alt.Y('made:Q', axis=alt.Axis(title='Shot Count Average')),
        color=alt.Color('shot_type:N', scale=alt.Scale(domain=[2, 3], range=['blue', 'orange']))
    ).properties(width=350, height=300, title='Shot Count Average')

    left_plot_points = alt.Chart(df_avg_shot_count).mark_circle(size=60).encode(
        x='year:O',
        y=alt.Y('made:Q'),
        color=alt.Color('shot_type:N', scale=alt.Scale(domain=[2, 3], range=['blue', 'orange']),
                        legend=alt.Legend(title='Shot Type', type='symbol',
                                          labelExpr="datum.value === 2 ? '2 points':'3 points'")),
        tooltip=[alt.Tooltip('year', title='Year'),
                 alt.Tooltip('made', title='Average Shot Count')]

    )

    # Create the right plot for success rate
    right_plot_chart_line = alt.Chart(df_success_rate).mark_line().encode(
        x='year:O',
        y=alt.Y('success_rate:Q', axis=alt.Axis(title='Shot Success Rate (%)')),
        color=alt.Color('shot_type:N', scale=alt.Scale(domain=[2, 3], range=['blue', 'orange']))
    ).properties(width=350, height=300, title='Success Rate')

    right_plot_points = alt.Chart(df_success_rate).mark_circle(size=60).encode(
        x='year:O',
        y=alt.Y('success_rate:Q'),
        color=alt.Color('shot_type:N', scale=alt.Scale(domain=[2, 3], range=['blue', 'orange']),
                        legend=alt.Legend(title='Shot Type', type='symbol',
                                          labelExpr="datum.value === 2 ? '2 points':'3 points'")),
        tooltip=[alt.Tooltip('year', title='Year'),
                 alt.Tooltip('success_rate', title='Shot Success Rate (%)')]
    )

    # Combine the plots side by side using Streamlit columns
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Average Shot Count Over the Years")
        st.altair_chart(left_plot_chart_line + left_plot_points)

    with col2:
        st.subheader("Shot Success Rate (%) Over the Years")
        st.altair_chart(right_plot_chart_line + right_plot_points)


def show_viz2_shots_gametime():
    df_data_shots_gametime = pd.read_csv('Data/data_viz2_shots_gametime.csv')
    st.subheader("Shot Success Rate (%) for Time in Game (min)")
    df_data_shots_gametime['made'] = df_data_shots_gametime['made'].round(3)

    selected_period = st.slider("Select Time Period (in minutes)", 0, 48, (0, 48), key='time_period')

    filtered_data_2pt = df_data_shots_gametime[(df_data_shots_gametime['shot_type'] == 2) & (
            df_data_shots_gametime['minutes_from_the_start'] >= selected_period[0]) & (
                                                       df_data_shots_gametime['minutes_from_the_start'] <=
                                                       selected_period[1])]
    filtered_data_3pt = df_data_shots_gametime[(df_data_shots_gametime['shot_type'] == 3) & (
            df_data_shots_gametime['minutes_from_the_start'] >= selected_period[0]) & (
                                                       df_data_shots_gametime['minutes_from_the_start'] <=
                                                       selected_period[1])]

    combined_data = pd.concat([filtered_data_2pt, filtered_data_3pt])
    combined_data['made'] = combined_data['made'] * 100

    line_chart = alt.Chart(combined_data).mark_line(strokeWidth=2).encode(
        x=alt.X('minutes_from_the_start', axis=alt.Axis(title="Minutes from Start", values=[0, 12, 24, 36, 48])),
        y=alt.Y('made', axis=alt.Axis(title="Shot Success Rate (%)")),
        color=alt.Color('shot_type:N', scale=alt.Scale(domain=[2, 3], range=['blue', 'orange'])))

    point_chart = alt.Chart(combined_data).mark_circle(size=60).encode(
        x=alt.X('minutes_from_the_start'),
        y=alt.Y('made'),
        color=alt.Color('shot_type:N', scale=alt.Scale(domain=[2, 3],
                                                       range=['blue', 'orange']),
                        legend=alt.Legend(title='Shot Type', type='symbol',
                                          labelExpr="datum.value === 2 ? '2 points':'3 points'")),
        tooltip=[alt.Tooltip('minutes_from_the_start', title='Game Time (Min)'),
                 alt.Tooltip('made', title='Shot Success (%)')])

    chart = (line_chart + point_chart).properties(width=700, height=400,
                                                  )
    # chart = chart.transform_filter(
    #     alt.FieldRangePredicate(field='minutes_from_the_start', range=list(selected_period)))

    for i in range(0, 8):
        if i % 12 == 0:
            chart += alt.Chart(pd.DataFrame({'x': [12 * i]})).mark_rule(color="darkgray", strokeDash=[3, 3]).encode(
                x='x:Q')
        else:
            chart += alt.Chart(pd.DataFrame({'x': [6 * i]})).mark_rule(color="lightgray", strokeDash=[3, 3]).encode(
                x='x:Q')

    st.altair_chart(chart)


def draw_basketball_court(ax=None, color='black', lw=2, outer_lines=False):
    # If an axes object isn't provided to plot onto, just get current one
    if ax is None:
        ax = plt.gca()

    # Create the various parts of an NBA basketball court

    # Create the basketball hoop
    # Diameter of a hoop is 18" so it has a radius of 9", which is a value
    # 7.5 in our coordinate system
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)

    # The paint
    # Create the outer box 0f the paint, width=16ft, height=19ft
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color,
                          fill=False)
    # Create the inner box of the paint, width=12ft, height=19ft
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color,
                          fill=False)

    # Create free throw top arc
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    # Create free throw bottom arc
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,
                            linewidth=lw, color=color, linestyle='dashed')
    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw,
                     color=color)

    # Three point line
    # Create the side 3pt lines, they are 14ft long before they begin to arc
    corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw,
                               color=color)
    corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
    # I just played around with the theta values until they lined up with the
    # threes
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw,
                    color=color)

    # Center Court
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0,
                           linewidth=lw, color=color)
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0,
                           linewidth=lw, color=color)

    # List of the court elements to be plotted onto the axes
    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                      bottom_free_throw, restricted, corner_three_a,
                      corner_three_b, three_arc, center_outer_arc,
                      center_inner_arc]

    if outer_lines:
        # Draw the half court line, baseline and side out bound lines
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw,
                                color=color, fill=False)
        court_elements.append(outer_lines)

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax


def show_viz3_shots_bbcourt():
    df_shots = pd.read_csv('Data/data_viz3_shots_court.csv')
    st.subheader('Analysis of Shot Locations on Basketball Court')

    shot_type_filter = st.selectbox("Shot Type", ['All Shots', '2-points', '3-points'])
    shot_success_filter = st.selectbox("Shot Success", ['All Shots', 'Made', 'Missed'])

    # Apply filters to the data
    filtered_data = df_shots.copy()
    if shot_type_filter != 'All Shots':
        shot_type = 2 if shot_type_filter == '2-points' else 3
        filtered_data = filtered_data[filtered_data['shot_type'] == shot_type]
    if shot_success_filter != 'All Shots':
        made = True if shot_success_filter == 'Made' else False
        filtered_data = filtered_data[filtered_data['made'] == made]

    # Create the basketball court visualization
    fig, ax = plt.subplots(figsize=(5.85, 4.75))
    gs = gridspec.GridSpec(1, 2, width_ratios=[0.85, 0.05])
    ax = plt.subplot(gs[0])

    ax.set_xlim(-250, 250)
    ax.set_ylim(422.5, -47.5)
    hexbin = ax.hexbin(x=filtered_data['shotX_rim'], y=filtered_data['shotY_rim'], gridsize=40, cmap='YlOrRd')
    draw_basketball_court(outer_lines=True)
    ax.axes.get_xaxis().set_visible(False)
    ax.axes.get_yaxis().set_visible(False)

    cax = fig.add_axes([0.85, 0.15, 0.03, 0.7])
    cbar = fig.colorbar(hexbin, cax=cax)
    cax.yaxis.set_ticklabels([])
    cbar.set_label('Shot Count')

    st.pyplot(fig)


def show_viz4_teams_years(data_all_shots):
    # data_all_shots = pd.read_csv('Data/data_viz14.csv.gz', compression='gzip')
    st.subheader("NBA Teams Shot Taking Analysis Over the Years")

    # Set the years range and the default selected year
    years_range = list(range(2000, 2023))
    default_year = 2018

    # Create a Streamlit slider for selecting the specific year
    selected_year = st.slider("Select Year", min_value=years_range[0], max_value=years_range[-1], value=default_year)
    # Filter the data based on the selected year
    data_all_shots_year = data_all_shots[data_all_shots["year"] == selected_year]

    # Create a Streamlit checkbox selector for choosing teams
    selected_teams = st.multiselect("Select Teams", options=list(data_all_shots["team"].unique()), default=["GSW"])
    # Filter the data based on the selected teams
    data_all_shots_teams = data_all_shots_year[data_all_shots_year["team"].isin(selected_teams)]

    # Calculate the shot counts for each team and shot type
    shot_counts = data_all_shots_teams.groupby(["team", "shot_type"]).size().unstack(fill_value=0)

    # Extract the team names and shot types
    teams = shot_counts.index.tolist()
    shot_types = shot_counts.columns.tolist()

    # Prepare the data for plotting
    x = np.arange(len(teams))
    width = 0.4

    # Plot the grouped bar chart
    fig, ax = plt.subplots()
    bars = []
    for i, shot_type in enumerate(shot_types):
        bars.append(ax.bar(x + i * width, shot_counts[shot_type], width))

    # Add labels for the bars
    for bar_group in bars:
        ax.bar_label(bar_group, padding=3)

    # Customize the plot
    ax.set_title(f'Shot Taking of {", ".join(selected_teams)} in Year {selected_year}')
    ax.set_ylabel('Shot Count')
    ax.set_xticks(x)
    ax.set_xticklabels(teams)
    ax.legend(shot_types)
    plt.tight_layout()
    st.pyplot(fig)


def show_viz5_shots_states():
    # df_shots_2 = pd.read_csv('Data/data_viz5_states_2points.csv.gz', compression='gzip')
    # df_shots_3 = pd.read_csv('Data/data_viz5_states_3points.csv.gz', compression='gzip')
    data_shot_counts = pd.read_csv('Data/data_viz5_states.csv.gz', compression='gzip')
    st.subheader("NBA Teams Shot Count Analysis by States in the USA")

    # Create a Streamlit radio button for selecting shot type
    selected_shot_type = st.radio("Shot Types:", ('2 Points', '3 Points'), index=1)

    # Filter the data based on the selected shot type
    if selected_shot_type == '2 Points':
        data_filtered_shot_type = data_shot_counts[data_shot_counts['shot_type'] == 2]
    else:
        data_filtered_shot_type = data_shot_counts[data_shot_counts['shot_type'] == 3]

    # Calculate shot count average per state
    df_state_shot_counts = data_filtered_shot_type.groupby('state').agg(
        {'made': 'sum', 'team': 'nunique'}).reset_index()
    df_state_shot_counts['shot_count_avg'] = df_state_shot_counts['made'] / df_state_shot_counts['team']

    # Create a dictionary mapping state abbreviations to their full names
    states_fullname_dict = {
        'GA': 'Georgia',
        'MA': 'Massachusetts',
        'NC': 'North Carolina',
        'IL': 'Illinois',
        'OH': 'Ohio',
        'TX': 'Texas',
        'CO': 'Colorado',
        'MI': 'Michigan',
        'CA': 'California',
        'IN': 'Indiana',
        'FL': 'Florida',
        'WI': 'Wisconsin',
        'MN': 'Minnesota',
        'NJ': 'New Jersey',
        'NY': 'New York',
        'PA': 'Pennsylvania',
        'AZ': 'Arizona',
        'OR': 'Oregon',
        'WA': 'Washington',
        'ON': 'Ontario',
        'UT': 'Utah',
        'BC': 'British Columbia',
        'DC': 'District of Columbia',
        'TN': 'Tennessee',
        'LA': 'Louisiana',
        'OK': 'Oklahoma'
    }
    # Add a new column "state_fullname" to the dataframe
    df_state_shot_counts['state_fullname'] = df_state_shot_counts['state'].map(states_fullname_dict)

    # # Add list of teams to the dataframe
    # df_state_shot_counts['teams_full_names'] = df_state_shot_counts['state'].map(
    #     data_filtered_shot_type.groupby('state')['team_fullname'].unique().apply(list))

    # Create the team_fullname_dictx
    teams_fullname_dict = {
        'ATL': 'Atlanta Hawks',
        'BOS': 'Boston Celtics',
        'CHH': 'Charlotte Hornets',
        'CHI': 'Chicago Bulls',
        'CLE': 'Cleveland Cavaliers',
        'DAL': 'Dallas Mavericks',
        'DEN': 'Denver Nuggets',
        'DET': 'Detroit Pistons',
        'GSW': 'Golden State Warriors',
        'HOU': 'Houston Rockets',
        'IND': 'Indiana Pacers',
        'LAC': 'LA Clippers',
        'LAL': 'Los Angeles Lakers',
        'MIA': 'Miami Heat',
        'MIL': 'Milwaukee Bucks',
        'MIN': 'Minnesota Timberwolves',
        'NJN': 'New Jersey Nets',
        'NYK': 'New York Knicks',
        'ORL': 'Orlando Magic',
        'PHI': 'Philadelphia 76ers',
        'PHO': 'Phoenix Suns',
        'POR': 'Portland Trail Blazers',
        'SAC': 'Sacramento Kings',
        'SAS': 'San Antonio Spurs',
        'SEA': 'Seattle SuperSonics',
        'TOR': 'Toronto Raptors',
        'UTA': 'Utah Jazz',
        'VAN': 'Vancouver Grizzlies',
        'WAS': 'Washington Wizards',
        'MEM': 'Memphis Grizzlies',
        'NOH': 'New Orleans Hornets',
        'CHA': 'Charlotte Bobcats',
        'NOK': 'New Orleans/Oklahoma City Hornets',
        'OKC': 'Oklahoma City Thunder',
        'BRK': 'Brooklyn Nets',
        'NOP': 'New Orleans Pelicans',
        'CHO': 'Charlotte Hornets'
    }
    # list of teams to the dataframe
    df_state_shot_counts['teams'] = df_state_shot_counts['state'].map(data_filtered_shot_type.groupby(
                                                                                'state')['team'].unique().apply(list))
    # Add team full names to the dataframe using teams_fullname_dict
    df_state_shot_counts['teams_fullname'] = df_state_shot_counts['teams'].apply(
                                                    lambda team_cod: [teams_fullname_dict[code] for code in team_cod])
    # df_state_shot_counts['team_fullname'] = df_state_shot_counts['team'].map(teams_fullname_dict)

    # Create the interactive USA choropleth map plot
    fig = px.choropleth(df_state_shot_counts, locations='state', locationmode='USA-states', scope="usa",
                        color='shot_count_avg', color_continuous_scale='Viridis',
                        hover_data=['state_fullname', 'teams_fullname', 'shot_count_avg'])
    fig.update_layout(coloraxis_colorbar=dict(title="Shot Count"),
                      title="Shot count is calculated as an average based on the number of teams in each state",
                      hoverlabel=dict(
                          bgcolor="white",
                          font_color="black",
                          font_size=12,
                          font_family="Arial")
                      )
    fig.update_traces(
        hovertemplate="<b>State: %{customdata[0]}</b>"
                      "<br>Teams: %{customdata[1]}"
                      "<br>Shot Count Average: %{customdata[2]}<br>"
    )

    st.plotly_chart(fig)


######################################################################################################################


st.set_page_config(page_title='NBA Shots Viz Project - Streamlit App')
st.title("NBA Basketball Shots Data Visualizations")

# Load dataset for Viz #1 & #4 only once:
df_data_viz14 = pd.read_csv('Data/data_viz14.csv.gz', compression='gzip')

show_viz1_shots_years(df_data_viz14)
show_viz2_shots_gametime()
show_viz3_shots_bbcourt()
show_viz4_teams_years(df_data_viz14)
show_viz5_shots_states()
