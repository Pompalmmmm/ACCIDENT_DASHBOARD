import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

@st.cache_data
def load_dataset(url):
    dataset = pd.read_csv(url)
    return dataset
# Load dataset
#df = load_dataset("https://raw.githubusercontent.com/Pompalmmmm/ACC_MAP/refs/heads/main/datamap_final.csv")
df_tambon = load_dataset('https://raw.githubusercontent.com/Pompalmmmm/ACC_MAP/refs/heads/main/tambon.csv')

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

df = AccidentData()
#--------------------------------------------PART OVERALL MAP-------------------------------------------------------------#

# Create a DataFrame for all provinces in Thailand with Thai and English names
data_province = {
    "Province (Thai)": [
        "กรุงเทพมหานคร", "กระบี่", "กาญจนบุรี", "กาฬสินธุ์", "กำแพงเพชร", "ขอนแก่น", "จันทบุรี",
        "ฉะเชิงเทรา", "ชลบุรี", "ชัยนาท", "ชัยภูมิ", "ชุมพร", "เชียงราย", "เชียงใหม่",
        "ตรัง", "ตราด", "ตาก", "นครนายก", "นครปฐม", "นครพนม", "นครราชสีมา", "นครศรีธรรมราช",
        "นครสวรรค์", "นนทบุรี", "นราธิวาส", "น่าน", "บึงกาฬ", "บุรีรัมย์", "ปทุมธานี",
        "ประจวบคีรีขันธ์", "ปราจีนบุรี", "ปัตตานี", "อยุธยา", "พะเยา", "พังงา",
        "พัทลุง", "พิจิตร", "พิษณุโลก", "เพชรบุรี", "เพชรบูรณ์", "แพร่", "ภูเก็ต",
        "มหาสารคาม", "มุกดาหาร", "แม่ฮ่องสอน", "ยโสธร", "ยะลา", "ร้อยเอ็ด", "ระนอง",
        "ระยอง", "ราชบุรี", "ลพบุรี", "ลำปาง", "ลำพูน", "ศรีสะเกษ", "สกลนคร", "สงขลา",
        "สตูล", "สมุทรปราการ", "สมุทรสงคราม", "สมุทรสาคร", "สระแก้ว", "สระบุรี", "สิงห์บุรี",
        "สุโขทัย", "สุพรรณบุรี", "สุราษฎร์ธานี", "สุรินทร์", "หนองคาย", "หนองบัวลำภู",
        "อ่างทอง", "อำนาจเจริญ", "อุดรธานี", "อุตรดิตถ์", "อุทัยธานี", "อุบลราชธานี",
        "บึงกาฬ"
    ],
    "Province (English)": [
        "Bangkok Metropolis", "Krabi", "Kanchanaburi", "Kalasin", "Kamphaeng Phet", "Khon Kaen", "Chanthaburi",
        "Chachoengsao", "Chonburi", "Chai Nat", "Chaiyaphum", "Chumphon", "Chiang Rai", "Chiang Mai",
        "Trang", "Trat", "Tak", "Nakhon Nayok", "Nakhon Pathom", "Nakhon Phanom", "Nakhon Ratchasima", "Nakhon Si Thammarat",
        "Nakhon Sawan", "Nonthaburi", "Narathiwat", "Nan", "Bueng Kan", "Buri Ram", "Pathum Thani",
        "Prachuap Khiri Khan", "Prachin Buri", "Pattani", "Phra Nakhon Si Ayutthaya", "Phayao", "Phang Nga",
        "Phatthalung", "Phichit", "Phitsanulok", "Phetchaburi", "Phetchabun", "Phrae", "Phuket",
        "Maha Sarakham", "Mukdahan", "Mae Hong Son", "Yasothon", "Yala", "Roi Et", "Ranong",
        "Rayong", "Ratchaburi", "Lop Buri", "Lampang", "Lamphun", "Si Sa Ket", "Sakon Nakhon", "Songkhla",
        "Satun", "Samut Prakan", "Samut Songkhram", "Samut Sakhon", "Sa Kaeo", "Saraburi", "Sing Buri",
        "Sukhothai", "Suphan Buri", "Surat Thani", "Surin", "Nong Khai", "Nong Bua Lamphu",
        "Ang Thong", "Amnat Charoen", "Udon Thani", "Uttaradit", "Uthai Thani", "Ubon Ratchathani",
        "Bueng Kan"
    ]
}

df_provinces = pd.DataFrame(data_province)
df["INCIDENT_DATE"] = pd.to_datetime(df["INCIDENT_DATE"], dayfirst=True, errors="coerce")
min_date = df["INCIDENT_DATE"].min().date()
max_date = df["INCIDENT_DATE"].max().date()
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

# Update session state based on user selection
st.session_state.selected_suspected_cause = selected_suspected_cause
st.session_state.selected_weather_conditions = selected_weather_conditions
st.session_state.selected_province = selected_province
st.session_state.selected_time_period = selected_time_period
st.session_state.selected_road = selected_road

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

# Merge and Count
df_merged = pd.merge(filtered_df, df_provinces, left_on='PROVINCE', right_on='Province (Thai)', how='left')

# Group by province and count the number of rows
province_counts = df_merged.groupby('Province (English)')['PROVINCE'].count().reset_index(name='counts')

province_counts = pd.merge(
    province_counts,
    df_merged[['Province (English)', 'Province (Thai)']].drop_duplicates(),
    on='Province (English)',
    how='left'
)
# Center and Map
center_lat, center_lon = 13.736717, 100.523186
fig = px.choropleth(
    province_counts,
    geojson="https://raw.githubusercontent.com/apisit/thailand.json/master/thailand.json",
    locations='Province (English)',
    featureidkey='properties.name',
    color='counts',
    color_continuous_scale="OrRd", #"hot"
    hover_name='Province (Thai)',  # Show Province in Thai
    hover_data={'counts': True, 'Province (English)': False}  # Hide Province (English), Show counts
)

fig.update_geos(center={"lat": center_lat, "lon": center_lon}, fitbounds="locations", visible=False)
#fig.add_trace(go.Scattergeo(
    #lat=[center_lat], lon=[center_lon], #mode='markers+text',
    #marker=dict(size=12, color='red')
    #text="Center of Thailand",  # Display text "Center of Thailand"
    #textposition="top center"
#))
# เปลี่ยนชื่อ color bar
fig.update_coloraxes(colorbar_title="จำนวนอุบัติเหตุ")
# Layout
# fig.update_layout( title_text="Accident Density Map",
#                   title_font_size=24
#                   , margin={"r": 0, "t": 50, "l": 0, "b": 0}
#                   )

# Streamlit Layout
st.title(":red[Accident] Density Map 📍")
st.caption(f"This dashboard contains data between **{start_date.strftime('%d %b %Y')}** and **{end_date.strftime('%d %b %Y')}**.")
# st.markdown("👈Explore accidents data categorized with selectable options from the sidebar")

col = st.columns((1,0.5), gap='medium')
with col[0]:
    st.plotly_chart(fig, use_container_width=True)

#st.write("### ")
with col[1]:
    if filtered_df.empty:
        st.warning("ไม่มีข้อมูลที่ตรงกับตัวเลือกการกรอง")
    else:
        # สร้างตารางสรุปข้อมูล
        province_summary = filtered_df.groupby("PROVINCE").size().reset_index(name="จำนวนอุบัติเหตุ")
        province_summary.columns = ["จังหวัด", "จำนวนอุบัติเหตุ"]  # เปลี่ยนชื่อคอลัมน์เป็นภาษาไทย
        province_summary = province_summary.sort_values(by="จำนวนอุบัติเหตุ", ascending=False).reset_index(drop=True)  # เรียงลำดับจากมากไปน้อย
        st.dataframe(province_summary.set_index("จังหวัด"))

###Import AI###
from AI_Interface.gemini_utils import getdfResponse
if st.button("AI🤖", key='thailand_province'):
    st.markdown('### Data Summarization with :blue[Gemini] ✨')
    container = st.container(border=True,height=400)
    with container:
        getdfResponse(
                province_summary,
                description="Number of Road accident by Province Visualize in Thailand Map.",
                date_range_values=date_range_values,
                selected_suspected_cause=[selected_suspected_cause] if selected_suspected_cause != "All" else None,
                selected_weather_conditions=[selected_weather_conditions] if selected_weather_conditions != "All" else None,
                selected_province=[selected_province] if selected_province != "All" else None,
                selected_time_period=[selected_time_period] if selected_time_period != "All" else None,
                selected_road=[selected_road] if selected_road != "All" else None,
            )



#-----------------------------------------PART HEATMAP BY PROVINCE-----------------------------------------------------------#

#load dataset
df_centermap = load_dataset('https://raw.githubusercontent.com/Pompalmmmm/ACC_MAP/refs/heads/main/provinces.csv')

# Header for Province Filter and Reset Button
st.header("Accident Density by Province 🛣️")

# Initialize session state for filters
if "heatmap_province" not in st.session_state:
    st.session_state.heatmap_province = "All"

# Use PROVINCE from df for filtering options
province_options = ["All"] + df["PROVINCE"].dropna().unique().tolist()

# Display the province filter
col1, col2 = st.columns([4, 1])  # Create columns for filter and reset button
with col1:
    if st.session_state.heatmap_province in province_options:
        selected_province = st.selectbox(
            "Selected Province",
            province_options,
            index=province_options.index(st.session_state.heatmap_province)
        )
    else:
        selected_province = st.selectbox(
            "Selected Province",
            province_options,
            index=0  # Default to "All" if mismatch occurs
        )
with col2:
    st.write(" ")
    if st.button("Reset Filter"):
        st.session_state.heatmap_province = "All"
        selected_province = "All"

# Update session state based on user selection
st.session_state.heatmap_province = selected_province

df_centermap["province_name"] = df_centermap["province_name"].str.strip()

# Determine map center and zoom
if st.session_state.heatmap_province == "All":
    center_lat, center_lon, zoom_level = 13.736717, 100.523186, 6 # Default to Bangkok
else:
    # Match selected province
    province_center = df_centermap[df_centermap["province_name"] == st.session_state.heatmap_province]
    if not province_center.empty:
        center_lat = province_center["province_lat"].values[0]
        center_lon = province_center["province_lon"].values[0]
        zoom_level = province_center["province_zoom"].values[0]
    else:
        st.warning(f"No data available for the selected province: {st.session_state.heatmap_province}")
        center_lat, center_lon, zoom_level = 13.736717, 100.523186, 6

# Filter data for Heatmap
heatmap_df = df.copy()
if st.session_state.heatmap_province != "All":
    heatmap_df = heatmap_df[heatmap_df["PROVINCE"] == st.session_state.heatmap_province]

# Check if province has data
if not heatmap_df.empty:
    # Group data by LATITUDE, LONGITUDE and collect ROUTE_CODE
    heatmap_grouped = heatmap_df.groupby(["LATITUDE", "LONGITUDE"]).agg(
        distinct_acc_code_count=("ACC_CODE", "nunique"),  # Use original name
        route_code_list=("ROUTE_CODE", lambda x: ', '.join(x.dropna().unique()))  # Collect ROUTE_CODE as a string
    ).reset_index()

    # ตรวจสอบข้อมูลที่ Grouped
    #st.write("ข้อมูลสำหรับ Heatmap:", heatmap_grouped)

    # ตรวจสอบค่าสูงสุดและต่ำสุด
    max_count = heatmap_grouped["distinct_acc_code_count"].max()
    min_count = heatmap_grouped["distinct_acc_code_count"].min()

    # กำหนด tickvals (ตำแหน่งตัวเลขใน Color Bar)
    tick_vals = list(range(min_count, max_count + 1, max(1, (max_count - min_count) // 5)))  # เพิ่มช่วงห่างให้เหมาะสม

    # Create Heatmap
    fig_heatmap = px.density_mapbox(
        heatmap_grouped,
        lat="LATITUDE",
        lon="LONGITUDE",
        z="distinct_acc_code_count",  # Use original column name
        radius=10,  # Adjust the radius for density
        hover_data={
            "distinct_acc_code_count": True,  # Show renamed column
            "route_code_list": True  # Show ROUTE_CODE in hover
        },
        mapbox_style="carto-positron",
        center={"lat": center_lat, "lon": center_lon},  # Set map center
        zoom=zoom_level,  # Adjust zoom level
        #title=f"Heatmap of {st.session_state.heatmap_province}" if st.session_state.heatmap_province != "All" else "Heatmap of All Provinces",
        color_continuous_scale="YlOrRd",  # Set heatmap color scale to Reds
        labels={
            "distinct_acc_code_count": "จำนวนอุบัติเหตุ",  # Change accident count label
            "route_code_list": "Location"  # Change route_code_list label
        }
    )

    # Update layout for better visuals
    fig_heatmap.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        #title={"y": 0.95, "x": 0.5, "xanchor": "center", "yanchor": "top"},
        coloraxis_colorbar=dict(
            title="จำนวนอุบัติเหตุ",  # Set label for color bar
            titleside="top",
            tickvals=tick_vals,  # กำหนดตำแหน่งตัวเลขใน Color Bar
            ticktext=[str(val) for val in tick_vals],  # แปลง tickvals เป็นข้อความ
            tickformat="d"  # แสดงเฉพาะเลขจำนวนเต็ม
        ),
        coloraxis_cmin=0,  # กำหนดค่าเริ่มต้นขั้นต่ำ
        coloraxis_cmax=max_count  # กำหนดค่าสูงสุดจากข้อมูล
    )

    # Display Heatmap
    if not heatmap_df.empty:
    # แสดง Title
        if st.session_state.heatmap_province != "All":
            st.subheader(f"ความหนาแน่นของอุบัติเหตุจังหวัด{st.session_state.heatmap_province}")
        else:
            st.subheader("ความหนาแน่นของอุบัติเหตุทุกจังหวัด")

    # แสดง Heatmap

    st.plotly_chart(fig_heatmap, use_container_width=True)
else:
    # กรณีไม่มีข้อมูล
    st.warning("ไม่มีข้อมูลที่ตรงกับตัวเลือกการกรอง")

heatmap_df_selected = heatmap_df[["ROUTE_CODE", "SUSPECTED_CAUSE"]]
heatmap_df_selected_group = heatmap_df_selected.groupby(["ROUTE_CODE", "SUSPECTED_CAUSE"]).value_counts().reset_index(name="Accidents")
# st.dataframe(heatmap_df_selected_group)
#_____AI______
# select: route_code, suspected_cause, lat, lon, nums accidents
if st.button("AI🤖", key='only_province'):
    st.markdown('### Data Summarization with :blue[Gemini] ✨')
    container = st.container(border=True,height=400)
    with container:
        getdfResponse(
        heatmap_df_selected_group,
        description="number of accident group by route, suspected causem province, latitude and longitude.",
        date_range_values=date_range_values,
        selected_suspected_cause=[selected_suspected_cause] if selected_suspected_cause != "All" else None,
        selected_weather_conditions=[selected_weather_conditions] if selected_weather_conditions != "All" else None,
        selected_province=[selected_province] if selected_province != "All" else None,
        selected_time_period=[selected_time_period] if selected_time_period != "All" else None,
        selected_road=[selected_road] if selected_road != "All" else None,
    )

