import time
import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

@st.cache_data
def getdfResponse(df, description, date_range_values=None, selected_suspected_cause=None, selected_weather_conditions=None, 
                  selected_province=None, selected_time_period=None, selected_road=None):
    """
    Summarize key insights from a given DataFrame with narrative enhancement for better insights.
    Parameters:
        - df: Filtered DataFrame.
        - description: Description of the dataset.
        - date_range_values: Tuple containing start and end dates (date1, date2).
        - selected_suspected_cause: Selected suspected cause(s) (for context in the prompt).
        - selected_weather_conditions: Selected weather conditions (for context in the prompt).
        - selected_province: Selected province(s) (for context in the prompt).
        - selected_time_period: Selected time period(s) (for context in the prompt).
        - selected_road: Selected road(s) (for context in the prompt).
    """
    # Ensure data is not empty
    if df.empty:
        st.warning("The DataFrame is empty. Please provide a valid DataFrame.")
        return

    # Convert the DataFrame to a string for API input
    df_text = df.to_string(index=False)

    try:
        st.session_state.model = genai.GenerativeModel('gemini-pro')

        # Build a detailed narrative for the prompt
        filters = []
        if selected_suspected_cause:
            filters.append(f"The suspected cause(s) being filter to: {', '.join(selected_suspected_cause)}.")
        if selected_weather_conditions:
            filters.append(f"The weather conditions being considered are: {', '.join(selected_weather_conditions)}.")
        if selected_province:
            filters.append(f"This analysis focuses on the following province(s): {', '.join(selected_province)}.")
        if selected_time_period:
            filters.append(f"The time period of interest includes: {', '.join(selected_time_period)}.")
        if selected_road:
            filters.append(f"The specific road(s) under consideration are: {', '.join(selected_road)}.")

        # Add date range context
        if date_range_values:
            filters.append(f"The dataset covers the date range from {date_range_values[0]} to {date_range_values[1]}.")

        # Combine filters into a narrative description
        filter_description = " ".join(filters) if filters else "This analysis considers all available data without specific filters."

        # Create the prompt with enhanced narrative
        prompt = (
            f"This dataset provides information about {description}. "
            f"The analysis aims to uncover trends, patterns, and key insights related to road safety. {filter_description} "
            "Based on the filtered data provided below, please summarize key findings and conclusion."
            "all answer in English with no difficulty words and Don't answer anything that data does not tell you."
        )

        # Use Gemini to generate insights
        df_response = st.session_state.model.generate_content([prompt, df_text])

        # Display the response
        st.write("### Key Insights")
        # st.write(prompt)
        st.write(df_response.text)

    except Exception as e:
        if "ResourceExhausted" in str(e):
            st.error("Rate limit exceeded. Please try again later.")
            time.sleep(1)  # Introduce a 1-second delay
            getdfResponse(df, description, date_range_values, selected_suspected_cause, selected_weather_conditions,
                          selected_province, selected_time_period, selected_road)
        else:
            st.error(f"An error occurred: {e}")
