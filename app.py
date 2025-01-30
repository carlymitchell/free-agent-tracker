import streamlit as st
import pandas as pd
import altair as alt

####################################
# LOAD CSVS
@st.cache_data
def load_data():
    years = [22, 23, 24, 25]
    data = {"hitters": {}, "pitchers": {}}
    
    for year in years:
        # Load hitters' data
        data["hitters"][year] = {
            "performance": pd.read_csv(f"hitters_{year}.csv").drop(columns=["playerid"], errors="ignore"),
            "contract": pd.read_csv(f"hitters_{year}_contract.csv").drop(columns=["playerid"], errors="ignore"),
        }
        
        # Load pitchers' data
        data["pitchers"][year] = {
            "performance": pd.read_csv(f"pitchers_{year}.csv").drop(columns=["playerid"], errors="ignore"),
            "contract": pd.read_csv(f"pitchers_{year}_contract.csv").drop(columns=["playerid"], errors="ignore"),
            "pitches": pd.read_csv(f"pitchers_{year}_pitches.csv").drop(columns=["playerid"], errors="ignore"),
        }

    return data

data = load_data()

####################################
# FUNCTION: Convert Currency Columns
def convert_currency_columns(df):
    for col in df.columns:
        if df[col].dtype == "object":  # Only check string columns
            if df[col].str.startswith("$").any():  # Check if any value starts with "$"
                df[col] = df[col].replace('[\$,]', '', regex=True).astype(float)
    return df

####################################
# SIDEBAR
st.sidebar.title("MLB Free Agent Analysis")
st.sidebar.markdown("***Created and updated by Carly Mitchell. (carlymbaseball@gmail.com)***")
page = st.sidebar.radio(
    "Select a Page", 
    ["Home", "Search & Compare Free Agents", "2025 Free Agents", "Top Leaders"]
)

####################################
# HOME PAGE
if page == "Home":
    st.title("MLB Free Agent Analysis Tool")
    st.markdown("""
        Welcome to the MLB Free Agent Analysis Tool! Use this app to:
        - **Search & Compare free agents**: Filter by position, metrics, and performance stats, or compare specific players.
        - **Upcoming free agents**: View projections for the 2025 season.
        - **Top leaders**: Visualize the top players in various stats by free agency class.
        
        <br><br>  <!-- Adds extra spacing -->
        
        ***Data is pulled from [FanGraphs.com](https://www.fangraphs.com) and covers free agents from 2022 - 2025.***  
    """, unsafe_allow_html=True)

####################################
# SEARCH & COMPARE FREE AGENTS
elif page == "Search & Compare Free Agents":
    st.title("Search & Compare Free Agents")
    mode = st.radio("Mode", ["Performance Data", "Contract Data"], horizontal=True)
    selected_years = st.multiselect("Select Year(s)", [2022, 2023, 2024, 2025], default=[2025])
    player_type = st.radio("Select Player Type", ["Hitters", "Pitchers"], horizontal=True)
    
    data_type = "performance" if mode == "Performance Data" else "contract"
    dfs = []
    for year in selected_years:
        df = data[player_type.lower()][int(str(year)[-2:])][data_type]
        df = convert_currency_columns(df)  # Convert currency columns
        dfs.append(df)
    
    combined_df = pd.concat(dfs)

    # Display main data with sorting enabled
    st.markdown(f"### {player_type} {mode} for {', '.join(map(str, selected_years))}")
    st.data_editor(combined_df, use_container_width=True)

    # Player Comparison Feature
    selected_players = st.multiselect(
        "Select Players to Compare (Up to 5)", 
        combined_df["Name"].unique(), 
        default=combined_df["Name"].unique()[:2],
        max_selections=5
    )

    if len(selected_players) < 2:
        st.warning("Please select at least 2 players for comparison.")
    else:
        st.markdown(f"### {player_type} Comparison for {', '.join(map(str, selected_years))}")
        comparison_df = combined_df[combined_df["Name"].isin(selected_players)].set_index("Name").transpose()
        st.data_editor(comparison_df, use_container_width=True)

    # Display Pitch Type Data for Pitchers
    if player_type == "Pitchers":
        st.markdown("### Pitch Type Usage & Performance")
        pitch_dfs = []
        for year in selected_years:
            pitch_df = data["pitchers"][int(str(year)[-2:])]["pitches"]
            pitch_df = convert_currency_columns(pitch_df)  # Convert currency columns
            pitch_dfs.append(pitch_df)
        
        selected_pitch_data = pd.concat(pitch_dfs)
        selected_pitch_data = selected_pitch_data[selected_pitch_data["Name"].isin(selected_players)]

        if not selected_pitch_data.empty:
            st.data_editor(selected_pitch_data, use_container_width=True)
        else:
            st.warning("No pitch type data available for the selected players.")

####################################
# 2025 FREE AGENTS
elif page == "2025 Free Agents":
    st.title("2025 Free Agents - 2024 Data")
    
    mode = st.radio("View Data Type", ["Performance Data", "Contract Data"], horizontal=True)
    data_type = "performance" if mode == "Performance Data" else "contract"
    
    hitters_2025 = data["hitters"][25][data_type]
    pitchers_2025 = data["pitchers"][25][data_type]
    
    hitters_2025 = convert_currency_columns(hitters_2025)
    pitchers_2025 = convert_currency_columns(pitchers_2025)
    
    st.markdown("### Hitters")
    st.data_editor(hitters_2025, use_container_width=True)
    
    st.markdown("### Pitchers")
    st.data_editor(pitchers_2025, use_container_width=True)

####################################
# TOP LEADERS
elif page == "Top Leaders":
    st.title("Top Leaders by Free Agency Class")
    
    selected_year = st.selectbox("Select Year", [2022, 2023, 2024, 2025], index=3)
    player_type = st.radio("Select Player Type", ["Hitters", "Pitchers"], horizontal=True)
    
    data_type = st.radio("View Data Type", ["Performance Data", "Contract Data"], horizontal=True)
    df = data[player_type.lower()][int(str(selected_year)[-2:])][
        "performance" if data_type == "Performance Data" else "contract"
    ]
    
    df = convert_currency_columns(df)  # Convert currency columns

    selected_stat = st.selectbox(
        "Select a Stat",
        df.columns[1:],  
        index=df.columns[1:].tolist().index("WAR") if "WAR" in df.columns[1:] else 0
    )
    
    top_leaders = df.sort_values(by=selected_stat, ascending=False).head(10)
    st.data_editor(top_leaders, use_container_width=True)
    
    if data_type == "Performance Data" and player_type == "Pitchers":
        st.markdown("### Pitch Type Usage & Performance")
        pitch_df = data["pitchers"][int(str(selected_year)[-2:])]["pitches"]
        pitch_df = convert_currency_columns(pitch_df)
        st.data_editor(pitch_df, use_container_width=True)
