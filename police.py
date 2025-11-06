import streamlit as st
import pandas as pd
import psycopg2
import psycopg2.extras
import plotly.express as px
# Import necessary libraries
import plotly.graph_objects as go
from sqlalchemy import create_engine

# Ensure the required libraries are listed in

# Create a connection to the PostgreSQL database

def create_connection():
    try:
        conn = psycopg2.connect(
            dbname="securecheck",
            user="postgres",
            password="moon123",
            host="localhost",
            port= 5432,              
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None

# fetch data from the database for postgreSQL query
def fetch_data(query):
    conn = create_connection()
    if conn is None:
        return pd.DataFrame()  # Return an empty DataFrame if connection fails
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()
    finally:
        conn.close()
#streamlit ui
st.set_page_config(
    page_title="SecureCheck: Police Data Dashboard",
    page_icon=":police_car:",
    layout="wide"
)
st.title("🚨 SecureCheck:Police Data Dashboard")
st.markdown("👮Real time monitoring and insights for law enforcement.")

#load data
st.header("👮📅Police Data Overview")
query = "SELECT * FROM police_log"  # Adjust the limit as needed
data = fetch_data(query)
if not data.empty:
    st.write("Data loaded successfully!")
    st.dataframe(data.head(), use_container_width=True)
else:
    st.warning("No data found or failed to load data. Please check the database connection or query.")

#show data types
st.header("📟📄Data Types and Summary")
data_types = data.dtypes.reset_index()
data_types.columns = ['Column', 'Data Type']
st.dataframe(data_types, use_container_width=True)

#quick metrics
import streamlit as st
st.header("📊key Metrics")
# Create four columns for displaying metrics
col1, col2, col3 = st.columns(3)
# Calculate and display metrics in the columns
with col1:
    total_stops = data.shape[0]  # Total number of rows in the DataFrame
    st.metric("Total Stops", total_stops)
with col2:
    arrests = data[data['is_arrested'] == True].shape[0]  # Count of arrests
    st.metric("Total Arrests", arrests)
with col3:
    drug_related_stops = data[data['drugs_related_stop'] == True].shape[0]  # Count of drug-related stops
    st.metric("Drug-Related Stops", drug_related_stops)

#advanced query
st.header("🧩Advanced Query")
selected_query = st.selectbox("select a query to run",[
    "Top 10 vehicle_number involved in drug-related stops",
    "vehicles most frequently searched",
    "driver age group had the higgest arrest rate",
    "gender distribution of drivers stopped in each country",
    "race and gender combinations with the highest search rates",
    "time of day sees the most traffic stops",  
    "average stop duration of different violations",
    "are stops during the night more likely to result in arrests",
    "violations are most associated with searches or arrests",
    "violations are most common among young drivers (<25 years old)",
    "is there a violation that rarely results in search or arrest",
    "country with the highest rate of drug-related stops",
    "arrest rates by country and violation type",
    "country has the most stops with search conducted",]
)

query_map = {

    "Top 10 vehicle_number involved in drug-related stops": "select vehicle_number,count (*) AS stop_count from police_log where(drugs_related_stop)= True group by vehicle_number order by stop_count limit 10",
    "vehicles most frequently searched": "select vehicle_number, COUNT(*) AS search_count FROM police_log WHERE search_conducted = TRUE  GROUP BY vehicle_number ORDER BY search_count DESC LIMIT 10",
    "driver age group had the higgest arrest rate":"SELECT driver_age, COUNT(*) FILTER (WHERE is_arrested = TRUE) * 100.0 / COUNT(*) AS arrest_rate FROM police_log GROUP BY driver_age ORDER BY arrest_rate DESC LIMIT 1",
    "gender distribution of drivers stopped in each country": "sELECT country_name, driver_gender, COUNT(*) AS stop_count FROM police_log GROUP BY country_name, driver_gender ORDER BY country_name, stop_count DESC",
    "race and gender combinations with the highest search rates": "SELECT driver_race, driver_gender, COUNT(*) FILTER (WHERE search_conducted = TRUE) * 100.0 / COUNT(*) AS search_rate FROM police_log GROUP BY driver_race, driver_gender ORDER BY search_rate DESC LIMIT 5",
    "time of day sees the most traffic stops": "SELECT stop_time::time(0), COUNT(*) AS stop_count FROM police_log GROUP BY stop_time::time(0) ORDER BY stop_count DESC LIMIT 1",
    "average stop duration of different violations": "SELECT violation, AVG(CASE WHEN stop_duration = '0-15 Min' THEN 7.5 WHEN stop_duration = '16-30 Min' THEN 23 WHEN stop_duration = '30+ Min' THEN 45 ELSE NULL END) AS avg_duration_minutes FROM police_log GROUP BY violation ORDER BY avg_duration_minutes DESC",
    "are stops during the night more likely to result in arrests": "SELECT CASE WHEN stop_time::time BETWEEN '20:00:00' AND '23:59:59' OR stop_time::time BETWEEN '00:00:00' AND '06:00:00' THEN 'night' ELSE 'day' END AS time_period, COUNT(*) FILTER (WHERE is_arrested = TRUE) * 100.0 / COUNT(*) AS arrest_rate FROM police_log GROUP BY time_period",
    "violations are most associated with searches or arrests": "SELECT violation, COUNT(*) FILTER (WHERE search_conducted = TRUE OR is_arrested = TRUE) * 100.0 / COUNT(*) AS rate FROM police_log GROUP BY violation ORDER BY rate DESC LIMIT 5",
    "violations are most common among young drivers (<25 years old)": "SELECT violation, COUNT(*) AS count FROM police_log WHERE driver_age < 25 GROUP BY violation ORDER BY count DESC LIMIT 5",
    "is there a violation that rarely results in search or arrest": "SELECT violation, COUNT(*) FILTER (WHERE search_conducted = TRUE OR is_arrested = TRUE) * 100.0 / COUNT(*) AS search_or_arrest_rate FROM police_log GROUP BY violation ORDER BY search_or_arrest_rate ASC LIMIT 5",
    "country with the highest rate of drug-related stops": "SELECT country_name, COUNT(*) FILTER (WHERE drugs_related_stop = TRUE) * 100.0 / COUNT(*) AS drug_related_rate FROM police_log GROUP BY country_name ORDER BY drug_related_rate DESC LIMIT 1",
    "arrest rates by country and violation type": "SELECT country_name, violation, COUNT(*) FILTER (WHERE is_arrested = TRUE) * 100.0 / COUNT(*) AS arrest_rate FROM police_log GROUP BY country_name, violation ORDER BY arrest_rate DESC LIMIT 10",
    "country has the most stops with search conducted": "SELECT country_name, COUNT(*) AS search_count FROM police_log WHERE search_conducted = TRUE GROUP BY country_name ORDER BY search_count DESC LIMIT 1"

}
if st.button("Run Selected Query", key="simple_query"):
    st.info("Running the selected query... Please wait.")

    result = fetch_data(query_map[selected_query])
    if not result.empty:
        st.success("Query executed successfully!")
        st.dataframe(result, use_container_width=True)

    else:
        st.warning("No data found for the selected query. Please try another query or check the database connection.")

# Add a download button for the result DataFrame    
if 'result' in locals() and not result.empty:
    csv = result.to_csv(index=False)
    st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name='query_results.csv',
        mime='text/csv'
    )

#Complex advanced query
st.header("🧩Complex Advanced Query")
complex_selected_query = st.selectbox("select a query to run",[
    "Yearly Breakdown of Stops and Arrests by Country",
    "Driver Violation Trends Based on Age and Race",
    "Time Period Analysis of Stops: Number of Stops by Year, Month, Hour of the Day",
    "Violations with High Search and Arrest Rates",
    "Driver Demographics by Country (Age, Gender, and Race)",
    "Top 5 Violations with Highest Arrest Rates",
], key="complex_query_selectbox")
query_map = {
    "Yearly Breakdown of Stops and Arrests by Country": """
SELECT 
    country_name,
    EXTRACT(YEAR FROM timestamp) AS year,
    COUNT(*) AS total_stops,
    SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests,
    ROUND(100.0 * SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS arrest_rate,
    RANK() OVER (PARTITION BY EXTRACT(YEAR FROM timestamp) ORDER BY COUNT(*) DESC) AS rank_by_stops
FROM 
    police_log
GROUP BY 
    country_name, EXTRACT(YEAR FROM timestamp)
ORDER BY 
    year, total_stops DESC;
    """,
    "Driver Violation Trends Based on Age and Race": """
SELECT
    driver_age,
    driver_race,
    violation,
    COUNT(*) AS violation_count
FROM 
    police_log
WHERE 
    violation IS NOT NULL
GROUP BY 
    driver_age, driver_race, violation
ORDER BY 
    violation_count DESC;
    """,
    
    "Time Period Analysis of Stops: Number of Stops by Year, Month, Hour of the Day": """
SELECT 
    EXTRACT(YEAR FROM timestamp) AS year,
    EXTRACT(MONTH FROM timestamp) AS month,
    EXTRACT(HOUR FROM timestamp) AS hour,
    COUNT(*) AS stop_count
FROM 
    police_log
GROUP BY 
    year, month, hour
ORDER BY 
    year, month, hour;
    """,
    "Violations with High Search and Arrest Rates": """
SELECT 
    violation,
    COUNT(*) AS total_stops,
    SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS search_count,
    SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrest_count,
    ROUND(100.0 * SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS search_rate,
    ROUND(100.0 * SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS arrest_rate,
    RANK() OVER (ORDER BY SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) DESC) AS arrest_rank
FROM 
    police_log
GROUP BY 
    violation
ORDER BY 
    arrest_rate DESC;
    """,
    "Driver Demographics by Country (Age, Gender, and Race)": """
    SELECT 
    country_name,
    driver_gender,
    driver_race,
    ROUND(AVG(driver_age), 1) AS avg_age,
    COUNT(*) AS total_drivers
FROM 
    police_log
GROUP BY 
    country_name, driver_gender, driver_race
ORDER BY 
    country_name, total_drivers DESC;
    """,
    "Top 5 Violations with Highest Arrest Rates": """
SELECT 
    violation,
    COUNT(*) AS total_cases,
    SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests,
    ROUND(100.0 * SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS arrest_rate
FROM 
    police_log
GROUP BY 
    violation
HAVING 
    COUNT(*) > 10  -- optional: exclude very rare violations
ORDER BY 
    arrest_rate DESC
LIMIT 5;
    """
}
if st.button("Run Selected Query", key="complex_query"):
    st.info("Running the selected query... Please wait.")
    result = fetch_data(query_map[complex_selected_query])
    if not result.empty:
        st.success("Query executed successfully!")
        st.dataframe(result, use_container_width=True)
    else:
        st.warning("No data found for the selected query. Please try another query or check the database connection.")

# Add a download button for the result DataFrame    
if 'result' in locals() and not result.empty:
    csv = result.to_csv(index=False)
    st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name='complex_query_results.csv',
        mime='text/csv'
    )

#visual insights

st.header("📊Visual Insights")
tab1, tab2 = st.tabs (["stops by violation", "Driver gender distribution"])

with tab1:
    st.subheader("🚦Stops by Violation")
    # Compute violation_counts before plotting
    if 'violation' in data.columns:
        # Debug: Show unique violations and their counts
        st.write("Unique violations:", data['violation'].unique())
        st.write("Value counts for violation:", data['violation'].value_counts())

        data['violation'] = data['violation'].astype(str)
        data['violation'] = data['violation'].fillna('Unknown')  # Handle missing values
        violation_counts = data['violation'].value_counts().reset_index()
        violation_counts.columns = ['violation', 'count']
        violation_counts = violation_counts.sort_values(by='count', ascending=False)
        # Optionally, filter out violations with count <= 1 for clarity
        violation_counts = violation_counts[violation_counts['count'] > 1]
        violation_counts = violation_counts.head(10)  # Limit to top 10 violations

        # Debug: Show violation_counts in Streamlit
        st.write("Violation counts preview:", violation_counts)

        import plotly.express as px
        fig = px.bar(
            violation_counts,
            x='violation',
            y='count',
            text='count',
            title='Stops by Violation',
            color='violation',
            color_discrete_sequence=px.colors.qualitative.Safe
        )

        fig.update_traces(
            textposition='outside',
            marker=dict(line=dict(width=1, color='DarkSlateGrey'))
        )
        fig.update_layout(
            bargap=0.3,
            yaxis_type='log',  # Use logarithmic scale for better height difference
            width=1000,
            height=800,        # Increase chart height
            xaxis=dict(categoryorder='total descending')
        )

        st.subheader("Top 10 Violations")
        st.write("This chart shows the top 10 violations based on the number of stops.")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for violations.")
  
with tab2:
    st.subheader("🚗Driver Gender Distribution")
    # Create a pie chart for driver gender distribution
    if 'driver_gender' in data.columns:
        gender_counts = data['driver_gender'].value_counts().reset_index()
        gender_counts.columns = ['driver_gender', 'count']
        fig = px.pie(gender_counts, names='driver_gender', values='count', title='Driver gender Distribution')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("no data available for driver gender distribution.")


# Add a footer with the app version and author information
st.markdown("---")
st.markdown('Built with ❤️ for law enforcement agencies to enhance public safety and transparency.')
st.header("Custom natural language queries 📟")
st.markdown('📃Fill in the form below to get insights from the police data using natural language queries.')
st.header("📝 Natural Language Query Form")
# Create a form for natural language queries
with st.form("nl_query_form"):
    stop_date = st.date_input("Select Stop Date")
    stop_time = st.time_input("Select Stop Time")
    country_name = st.selectbox("Select Country", data['country_name'].unique().tolist())
    driver_age = st.number_input("Enter Driver Age", min_value=0, max_value=120, value=30)
    driver_gender = st.selectbox("Select Driver Gender", ["male", "female", "other"])
    driver_race = st.selectbox("Select Driver Race", data['driver_race'].unique().tolist())
    search_conducted = st.checkbox("Search Conducted")
    search_type = st.selectbox("Select Search Type", ["Consent", "Probable Cause", "Inventory", "Other"])
    drug_related_stops = st.checkbox("Drug Related Stops")
    stop_duration = st.selectbox("Select Stop Duration", data['stop_duration'].unique().tolist())
    vehicle_number = st.selectbox("Select Vehicle Number", data['vehicle_number'].unique().tolist())
    time_stamp = st.text_input("Enter Timestamp (YYYY-MM-DD HH:MM:SS)", value=stop_date.strftime('%Y-%m-%d') + ' ' + stop_time.strftime('%H:%M:%S'))
    
    submit_button = st.form_submit_button("predict stop outcome")
    # Ensure the timestamp is in the correct format
    try:
        time_stamp = pd.to_datetime(time_stamp, format='%Y-%m-%d %H:%M:%S')
    except ValueError:
        st.error("Invalid timestamp format. Please use 'YYYY-MM-DD HH:MM:SS'.")
        time_stamp = pd.to_datetime(stop_date.strftime('%Y-%m-%d') + ' ' + stop_time.strftime('%H:%M:%S'))

    # Process the form submission   
    if submit_button:
        st.success("Query submitted successfully!")
        # Convert columns to correct types for comparison
        data['stop_time'] = pd.to_datetime(data['stop_time'], format='%H:%M:%S', errors='coerce').dt.time
        data['stop_date'] = pd.to_datetime(data['stop_date'], format='%Y-%m-%d', errors='coerce').dt.date
        # Ensure boolean columns are boolean
        if data['search_conducted'].dtype != bool:
            data['search_conducted'] = data['search_conducted'].astype(bool)
        if data['drugs_related_stop'].dtype != bool:
            data['drugs_related_stop'] = data['drugs_related_stop'].astype(bool)
        # Ensure timestamp column is datetime
        if 'timestamp' in data.columns:
            data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')
        # Filter the data based on the form inputs       
        filtered_data = data[
            (data['driver_gender'] == driver_gender) &
            (data['driver_age'] == driver_age) &
            (data['search_conducted'] == search_conducted) &
            (data['stop_duration'] == stop_duration) &
            (data['drugs_related_stop'] == drug_related_stops) &
            (data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S') == time_stamp.strftime('%Y-%m-%d %H:%M:%S'))
        ]
        # Debug: Show filtered data if needed
        # st.write(filtered_data)
        #predict stop_outcome
        if filtered_data.empty:
            predicted_outcome = "warning"
            predicted_violation = "speeding"
        else:
        # Predict the stop outcome based on the filtered data
            predicted_outcome = filtered_data['stop_outcome'].mode()[0]  # Get the most common outcome
            predicted_violation = filtered_data['violation'].mode()[0]  # Get the most common violation
        # If no matching records are found, set default values
        # If the filtered data is empty, set default values for prediction
        # If the filtered data is not empty, predict the stop outcome
        #natural language query results
        st.header("🔍 Natural Language Query Results")
        st.markdown("### 📋 Query Summary"
                    " | Results based on your inputs")
        # Display the results in a markdown format
        search_text = "A search was conducted " if search_conducted else "no search was conducted"
        drug_text = "was a drug-related stop" if drug_related_stops else "was not a drug-related stop"

        st.markdown(f"""

        **🚘Prediction summary🚘**
                            
        **❌Prediction Violation:** {predicted_violation}  
        **❌Prediction Stop Outcome:** {predicted_outcome}    

        A {driver_age}-year-old {driver_gender} driver in {country_name} was stopped 
        on **{stop_date}** at **{stop_time}**. 
        The stop was for a violation of **{predicted_violation}**.
        The stop duration was **{stop_duration}**.
        Vehicle number involved in the stop was **{vehicle_number}**.
        {search_text} and it {drug_text}.
        """)
    # project footer
    st.markdown("---")
    st.markdown("👮‍♂️ **SecureCheck** is a project developed by Selva Saranya")
    st.markdown("🔗 [GitHub Repository]( polgit@github.com:Selvasaranya2025/Police_log.git)")
