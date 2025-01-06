import streamlit as st
import pandas as pd
from datetime import date, datetime
from streamlit_extras.metric_cards import style_metric_cards
from pandas.tseries.offsets import MonthEnd
import plotly.graph_objects as go
import plotly.express as px
import time
import os
import joblib
#from AI_Interface.app import chat_with_Gemini
from AI_Interface.gemini_utils import getdfResponse  

@st.cache_data
def AccidentData():
    dataset = pd.read_csv('dataset/ACC_Cleaned.csv')
    dataset["INCIDENT_DATE"] = pd.to_datetime(dataset["INCIDENT_DATE"])
    def classify_time_period(incident_time):
        try:
            # Parse hour from INCIDENT_TIME
            hour = int(incident_time.split(":")[0])  # Extract the hour part
            if 0 <= hour < 6:
                return "Night (0:00 - 6:00)"
            elif 6 <= hour < 12:
                return "Morning (6:00 - 12:00)"
            elif 12 <= hour < 18:
                return "Afternoon (12:00 - 18:00)"
            elif 18 <= hour <= 24:
                return "Evening (18:00 - 24:00)"
        except (ValueError, AttributeError):  # Handle invalid or missing times
            return "Unknown"

    dataset["TIME_PERIOD"] = dataset["INCIDENT_TIME"].apply(classify_time_period)
    dataset = dataset[dataset["TIME_PERIOD"] != "Unknown"]
    return dataset

# Initialize default filter values
def reset_filters():
    st.session_state["suspected_cause"] = "All"
    st.session_state["weather_conditions"] = "All"
    st.session_state["province"] = "All"
    st.session_state["date_picker"] = (min_date, max_date)

st.title("Accident Tracking 🚨")

# Load and preprocess data
df = AccidentData()
df["INCIDENT_DATE"] = pd.to_datetime(df["INCIDENT_DATE"])

min_date = df["INCIDENT_DATE"].min().date()
max_date = df["INCIDENT_DATE"].max().date()

# Add Year-Month columns
df["YEAR_MONTH"] = df["INCIDENT_DATE"].dt.strftime("%Y-%b")
df["YEAR_MONTH_INT"] = df["INCIDENT_DATE"].dt.strftime("%Y-%m")
df["MONTH"] = df["INCIDENT_DATE"].dt.month_name()
# Define last 12 months
current_date = df["INCIDENT_DATE"].max() + MonthEnd(0)
start_date_12m = (current_date - pd.DateOffset(months=11)).replace(day=1)

# Create all months for 12 months
all_months = pd.date_range(start=start_date_12m, end=current_date, freq="MS").strftime("%Y-%m").tolist()
all_months_df = pd.DataFrame({"YEAR_MONTH_INT": all_months})

# Sidebar Filters
st.sidebar.title("Filters")
# Initialize session state for filters
if "selected_suspected_cause" not in st.session_state:
    st.session_state.selected_suspected_cause = "All"
if "selected_weather_conditions" not in st.session_state:
    st.session_state.selected_weather_conditions = "All"
if "selected_province" not in st.session_state:
    st.session_state.selected_province = "All"
if "selected_time_period" not in st.session_state:
    st.session_state.selected_time_period = "All"
if "selected_road" not in st.session_state:
    st.session_state.selected_road = "All"

# Check if reset button is pressed
if st.sidebar.button("Reset Filters"):
    st.session_state.selected_suspected_cause = "All"
    st.session_state.selected_weather_conditions = "All"
    st.session_state.selected_province = "All"
    st.session_state.selected_time_period = "All"
    st.session_state.selected_road = "All"
    st.session_state["date_picker"] = (min_date, max_date)

# Add "All" to the filter options
suspected_cause_options = ["All"] + df["SUSPECTED_CAUSE"].dropna().unique().tolist()
weather_conditions_options = ["All"] + df["WEATHER_CONDITIONS"].dropna().unique().tolist()
province_options = ["All"] + df["PROVINCE"].dropna().unique().tolist()
time_period_options = ["All"] + df["TIME_PERIOD"].dropna().unique().tolist()
road_options = ["All"] + df["AGENCY_DEPARTMENT"].dropna().unique().tolist()

# Display filters with session state
selected_suspected_cause = st.sidebar.selectbox(
    "Suspected Cause",
    suspected_cause_options,
    index=suspected_cause_options.index(st.session_state.selected_suspected_cause)
)
selected_weather_conditions = st.sidebar.selectbox(
    "Weather Conditions",
    weather_conditions_options,
    index=weather_conditions_options.index(st.session_state.selected_weather_conditions)
)
selected_province = st.sidebar.selectbox(
    "Province",
    province_options,
    index=province_options.index(st.session_state.selected_province)
)
selected_time_period = st.sidebar.selectbox(
    "Time Period",
    time_period_options,
    index=time_period_options.index(st.session_state.selected_time_period)
)
selected_road = st.sidebar.selectbox(
    "Road",
    road_options,
    index=road_options.index(st.session_state.selected_road)
)
date_range_values = st.sidebar.date_input(
        "Select a date range",
        value=(min_date, max_date),
        help="Pick the start and end date for your analysis",
        key="date_picker",
)

# # Update session state based on user selection
# st.session_state.selected_suspected_cause = selected_suspected_cause
# st.session_state.selected_weather_conditions = selected_weather_conditions
# st.session_state.selected_province = selected_province
# st.session_state.selected_time_period = selected_time_period
# st.session_state.selected_road = selected_road

# Filter Data
filtered_df = df.copy()
if selected_suspected_cause != "All":
    filtered_df = filtered_df[filtered_df["SUSPECTED_CAUSE"] == selected_suspected_cause]
if selected_weather_conditions != "All":
    filtered_df = filtered_df[filtered_df["WEATHER_CONDITIONS"] == selected_weather_conditions]
if selected_province != "All":
    filtered_df = filtered_df[filtered_df["PROVINCE"] == selected_province]
if selected_time_period != "All":
    filtered_df = filtered_df[filtered_df["TIME_PERIOD"] == selected_time_period]
if selected_road != "All":
    filtered_df = filtered_df[filtered_df["AGENCY_DEPARTMENT"] == selected_road]
# Check date range selection
if isinstance(date_range_values, tuple) and len(date_range_values) == 2:
    start_date, end_date = date_range_values
else:
    st.warning("Please select both a start date and an end date to show data.")
    st.stop()

st.caption(f"This dashboard contains data between **{start_date.strftime('%d %b %Y')}** and **{end_date.strftime('%d %b %Y')}**.")

# # Sidebar Filters
# with st.sidebar.expander("Filters"):
#     # Add Reset Filters Button
#     if st.button("Reset Filters"):
#         reset_filters()

#     # Dropdowns for filters
#     selected_suspected_cause = st.selectbox(
#         "Select Suspected Cause:",
#         options=["All"] + df["SUSPECTED_CAUSE"].unique().tolist(),
#         index=0,
#         key="suspected_cause",
#     )

#     selected_weather_conditions = st.selectbox(
#         "Select Weather Conditions:",
#         options=["All"] + df["WEATHER_CONDITIONS"].unique().tolist(),
#         index=0,
#         key="weather_conditions",
#     )

#     selected_province = st.selectbox(
#         "Select Province:",
#         options=["All"] + df["PROVINCE"].unique().tolist(),
#         index=0,
#         key="province",
#     )

#     # Date range filter



# # Filter Data
# filtered_df = df.copy()
# if selected_suspected_cause != "All":
#     filtered_df = filtered_df[filtered_df["SUSPECTED_CAUSE"] == selected_suspected_cause]
# if selected_weather_conditions != "All":
#     filtered_df = filtered_df[filtered_df["WEATHER_CONDITIONS"] == selected_weather_conditions]
# if selected_province != "All":
#     filtered_df = filtered_df[filtered_df["PROVINCE"] == selected_province]
filtered_df_no_date = filtered_df.copy()
filtered_df = filtered_df[(filtered_df["INCIDENT_DATE"] >= pd.to_datetime(start_date)) & (filtered_df["INCIDENT_DATE"] <= pd.to_datetime(end_date))]

# Metrics Calculation
total_days = (end_date - start_date).days + 1
total_accidents = filtered_df.shape[0]
accident_rate = total_accidents / total_days
total_injuries = filtered_df["TOTAL_INJURIES"].sum()
injuries_rate = total_injuries / total_accidents if total_accidents > 0 else 0

# Display Metrics
def metric_cards():
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Total Accidents", value=f"{total_accidents:,}")
    col2.metric(label="Accidents per Day", value=f"{accident_rate:,.2f}")
    col3.metric(label="Total Injuries", value=f"{total_injuries:,}")
    col4.metric(label="Injuries per Accident", value=f"{injuries_rate:,.2f}")
    style_metric_cards(box_shadow=False, border_left_color="#C7253E")

metric_cards()


#Prepare df for plot
accidents_by_month_12M = filtered_df_no_date.groupby("YEAR_MONTH_INT").size().reset_index(name="Accidents")
accidents_by_month_12M['YEAR'] = accidents_by_month_12M['YEAR_MONTH_INT'].str[:4]

accidents_by_month_12M['MONTH'] = pd.to_datetime(accidents_by_month_12M['YEAR_MONTH_INT'], format='%Y-%m')
month_order = [
    'January', 'February', 'March', 'April', 'May', 'June', 
    'July', 'August', 'September', 'October', 'November', 'December'
]
accidents_by_month_12M['MONTH'] = accidents_by_month_12M['MONTH'].dt.month_name()
accidents_by_month_12M['MONTH']= pd.Categorical(accidents_by_month_12M['MONTH'], categories=month_order, ordered=True)

st.subheader("Monthly Accident Trends Over Years")
st.caption("Date range will not apply to this chart.")
tab1, tab2, tab3 = st.tabs(["📈 Chart", "🗃 Data", " 🤖 AI"])
with tab1:
    fig_line = px.line(accidents_by_month_12M, x=accidents_by_month_12M['MONTH'], y='Accidents'
                    ,color=accidents_by_month_12M['YEAR_MONTH_INT'].str[:4], markers=True
                    ,category_orders={"MONTH": month_order})
    st.plotly_chart(fig_line)
    
with tab2:
    top_data = accidents_by_month_12M.iloc[:, :2].set_index('YEAR_MONTH_INT')
    st.dataframe(
    top_data,
    column_order=("YEAR_MONTH_INT", "Accidents"),
    column_config={
        "YEAR_MONTH_INT": st.column_config.TextColumn("YEAR-MONTH"),
        "Accidents": st.column_config.ProgressColumn(
            "Accidents",
            width = "large",
            format="%d", 
            min_value=0,
            max_value=int(top_data["Accidents"].max()),
        ),
    },
)
with tab3:
    st.markdown('### Data Summarization with :blue[Gemini] ✨')
    container = st.container(border=True,height=400)
    #user_message = st.chat_input('Your message here...')
    with container:
        #chat_with_Gemini(user_message,top_data)
        getdfResponse(
                top_data,
                description="Road Accidents Monthly Trends compare by each year in Thailand. The data have 2 columns YEAR_MONTH, Accidents: Number of Accident that filter from sidebar",
                date_range_values=date_range_values,
                selected_suspected_cause=[selected_suspected_cause] if selected_suspected_cause != "All" else None,
                selected_weather_conditions=[selected_weather_conditions] if selected_weather_conditions != "All" else None,
                selected_province=[selected_province] if selected_province != "All" else None,
                selected_time_period=[selected_time_period] if selected_time_period != "All" else None,
                selected_road=[selected_road] if selected_road != "All" else None,
            )


# Combined Chart with Bar and Line
st.subheader("Accidents and %Month-over-Month (%MoM)")
st.caption("Date range will not apply to this chart.")
#Nut edit
#accidents_by_month_12M.merge(accidents_by_month_12M, on="YEAR_MONTH_INT", how="left").fillna(0)
#Selection
selected_Y = accidents_by_month_12M["YEAR"].unique()
selection = st.pills(" ",selected_Y,)
if selection == None :
    selection = "2024"
    st.caption(f"default: {selection}")

# Calculate Accidents and MoM -- may be do it before filter
accidents_by_month_12M = accidents_by_month_12M.loc[accidents_by_month_12M["YEAR"] == selection]

#accidents_by_month_12M = filtered_df_no_date[filtered_df_no_date["INCIDENT_DATE"] >= start_date_12m].groupby("YEAR_MONTH_INT").size().reset_index(name="Accidents")
#accidents_by_month_12M = all_months_df.merge(accidents_by_month_12M, on="YEAR_MONTH_INT", how="left").fillna(0)

accidents_by_month_12M = accidents_by_month_12M.set_index("YEAR_MONTH_INT")
accidents_by_month_12M["Accidents"] = accidents_by_month_12M["Accidents"].astype(int)
accidents_by_month_12M["MoM (%)"] = accidents_by_month_12M["Accidents"].pct_change().fillna(0) * 100

fig = go.Figure()

# Add bar chart for accidents
fig.add_trace(
    go.Bar(
        x=accidents_by_month_12M.index,
        y=accidents_by_month_12M["Accidents"],
        name="Accidents",
        marker_color="skyblue",
    )
)

# Add line chart for MoM
fig.add_trace(
    go.Scatter(
        x=accidents_by_month_12M.index,
        y=accidents_by_month_12M["MoM (%)"],
        name="MoM (%)",
        mode="lines+markers",
        line=dict(color="#C7253E", width=2),
        marker=dict(size=8),
        yaxis="y2",
    )
)

# Customize layout for dual axes
fig.update_layout(
    # title="Accidents and %Month-over-Month (%MoM)",
    xaxis=dict(title="Year Month", showgrid=False),
    yaxis=dict(title="Number of Accidents", side="left", showgrid=False),
    yaxis2=dict(title="MoM (%)", overlaying="y", side="right", showgrid=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    width=800,
    height=500,
)

st.plotly_chart(fig, use_container_width=True)

col = st.columns((1,1), gap='small')
with col[0]:
    table = st.checkbox("see table")
    if table:
    # Detailed Data
        st.subheader("Detailed Data with MoM (%)")
        st.dataframe(
            accidents_by_month_12M[['Accidents', 'MoM (%)']]
            .style.format({
                "Accidents": "{:,}",  # Add thousands separator for Accidents
                "MoM (%)": "{:.2f}%"  # Format MoM (%) with two decimal places and a % sign
            })
        )
with col[1]:
    if st.button("🤖 AI"):
        st.markdown('### Data Summarization with :blue[Gemini] ✨')
        container = st.container(border=True,height=400)
        with container:
            # getdfResponse(accidents_by_month_12M)
            getdfResponse(
                accidents_by_month_12M,
                description="Accidents and Month-over-Month (MoM) Road Accident in Thailand",
                date_range_values=date_range_values,
                selected_suspected_cause=[selected_suspected_cause] if selected_suspected_cause != "All" else None,
                selected_weather_conditions=[selected_weather_conditions] if selected_weather_conditions != "All" else None,
                selected_province=[selected_province] if selected_province != "All" else None,
                selected_time_period=[selected_time_period] if selected_time_period != "All" else None,
                selected_road=[selected_road] if selected_road != "All" else None,
            )

st.divider()

st.markdown("### Accidents by :blue[Vehicles] ")

vehicle_map = {
"motor_bike": "L","Motor_tricycle": "L","tricycle": "L",
"Private_Public_passenger_car": "M","van": "M","passenger_pickup": "M","Bus": "M",
"4wheel_pickup": "N","trailer_Truck_10wheels": "N","truck_6wheel ": "N","truck_6to10wheel ": "N",
"Others": "Others", "bicycle": "Others","pedestrian": "Others","e_tan_Agricultural_veh": "Others"
}
filtered_df['VEHICLE_CATEGORY'] = filtered_df['VEHICLE'].map(vehicle_map)

vehicle_rename = {
"motor_bike": "Motor bike","Motor_tricycle": "Motor tricycle","tricycle": "Tricycle",
"Private_Public_passenger_car": "Passenger car","van": "Van","passenger_pickup": "Passenger pickup","Bus": "Bus",
"4wheel_pickup": "Pickup(4W)","trailer_Truck_10wheels": "Trailer truck(10W)","truck_6wheel ": "Truck(6W)","truck_6to10wheel ": "Truck(6-10W)",
"Others": "Others", "bicycle": "Bicycle","pedestrian": "Pedestrian","e_tan_Agricultural_veh": "E-tan"
}

data = filtered_df.value_counts('VEHICLE_CATEGORY').sort_values(ascending=False)
data = filtered_df[['VEHICLE','VEHICLE_CATEGORY']]
data = data.groupby('VEHICLE_CATEGORY').value_counts().reset_index(name="Accidents")
data['VEHICLE'] = data['VEHICLE'].replace(vehicle_rename)

# st.caption(f"This dashboard contains data between **{start_date.strftime('%d %b %Y')}** and **{end_date.strftime('%d %b %Y')}**.")
col = st.columns((1,0.75), gap='medium')
with col[0]:
    
    fig_pie = px.sunburst(data, path=['VEHICLE_CATEGORY','VEHICLE','Accidents'], values='Accidents'
                        ,color='VEHICLE_CATEGORY' 
                        ,maxdepth = 2
                        )
    st.plotly_chart(fig_pie)
with col[1]:
    #data = data.set_index('VEHICLE_CATEGORY')
    st.dataframe(data.set_index('VEHICLE_CATEGORY')
                 ,column_config={ 
                     "VEHICLE_CATEGORY": st.column_config.TextColumn("Category"
                                                                     ,width = "small"
                                                                     ,help="Categories by **UNECE**")                                      
                     #,"VEHICLE": st.column_config.Column(width = "medium")
                     }
                 )
    #st.caption("W is amount of Wheels")
#st.caption("The UNECE categorizes vehicles into broad groups under the World Forum for Harmonization of Vehicle Regulations")
st.markdown(
    """
    The UNECE categorizes vehicles into broad groups under the World Forum for Harmonization of Vehicle Regulations
    - **Category L**: Motorized two- and three-wheel vehicles  
        - Motor Bike, Motor Tricycle, Tricycles  
    - **Category M**: Passenger vehicles with four or more wheels  
        - Private or Public Passenger Car, Passenger Pickup, Van, Bus  
    - **Category N**: Goods Transport Vehicles  
        - 4 wheels Pickup, 6 wheels Truck, 6 to 10 wheels Truck, 10 wheels Trailer Truck  
    - **Others**: Category Not Specified by UNECE  
        - **Non-Motorized**: Bicycle, Pedestrian  
        - **Agricultural Vehicles**: E_tan_Agricultural_veh  
        - **Could not specify**: Reporter did not record vehicle type  
    """
)


if st.button("AI🤖"):
    st.markdown('### Data Summarization with :blue[Gemini] ✨')
    container = st.container(border=True,height=400)
    with container:
        getdfResponse(
        data,
        description="Accidents Caused by Vehicles in Thailand",
        date_range_values=date_range_values,
        selected_suspected_cause=[selected_suspected_cause] if selected_suspected_cause != "All" else None,
        selected_weather_conditions=[selected_weather_conditions] if selected_weather_conditions != "All" else None,
        selected_province=[selected_province] if selected_province != "All" else None,
        selected_time_period=[selected_time_period] if selected_time_period != "All" else None,
        selected_road=[selected_road] if selected_road != "All" else None,
    )


