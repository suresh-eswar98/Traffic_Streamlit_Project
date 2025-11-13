import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import urllib.parse
import altair as alt


# -------------------------------
# STREAMLIT UI
# -------------------------------
st.set_page_config(page_title="👮 SecureCheck: Police Check", layout="wide")

st.title("👮 SecureCheck: Police Check")
st.write("Welcome! This is your Streamlit SecureCheck: Police Check.")

# -------------------------------
# DATABASE CONNECTION
# -------------------------------
try:
    # Encode password properly (important if it has special characters)
    password = urllib.parse.quote_plus("Sureshsk@12345")

    # Create engine for MySQL (root user, database = vehicle)
    engine = create_engine(f"mysql+pymysql://root:{password}@localhost/vehicle")

    # Test query
    query = "SELECT * FROM traffic_project LIMIT 10;"
    df = pd.read_sql(query, engine)

    st.write("Here is a preview of your data:")
    st.dataframe(df)

    # Example chart
    if "violation" in df.columns:
        st.subheader("📊 Violations Count")

        # Prepare data
        violation_counts = df["violation"].value_counts().reset_index()
        violation_counts.columns = ["violation", "count"]

        # Assign colors based on count
        def assign_color(count):
            if count == 3:
                return "skyblue"
            elif count == 2:
                return "lightgreen"
            elif count == 1:
                return "darkred"
            else:
                return "gray"  # default for other counts

        violation_counts["color"] = violation_counts["count"].apply(assign_color)

        # Bar chart with Altair
        bar = alt.Chart(violation_counts).mark_bar().encode(
            x='count',
            y=alt.Y('violation', sort='-x'),
            color=alt.Color('color', scale=None)
        )

        text = bar.mark_text(
            align='left',
            baseline='middle',
            dx=5
        ).encode(
            text='count'
        )

        chart = (bar + text).properties(width=600, height=400)
        st.altair_chart(chart)

    # -------------------------------
    # ADVANCED INSIGHTS SECTION
    # -------------------------------
    st.header("📈 Advanced Insights")

    query_option = st.selectbox(
        "Select a Query to Run",
        [
            "Top 10 vehicles involved in drug-related stops",
            "Vehicles most frequently searched",
            "Driver age group with highest arrest rate",
            "Gender distribution of drivers stopped in each country",
            "Race and gender combination with highest search rate",
            "Time of day with most traffic stops",
            "Average stop duration for different violations",
            "Are stops during night more likely to lead to arrests?",
            "Violations most associated with searches or arrests",
            "Violations most common among younger drivers (<25)",
            "Violation rarely results in search or arrest",
            "Countries with highest rate of drug-related stops",
            "Arrest rate by country and violation",
            "Country with most stops with search conducted",
            "Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions)",
            "Driver Violation Trends Based on Age and Race (Join with Subquery)",
            "Time Period Analysis of Stops (Year, Month, Hour)",
            "Violations with High Search and Arrest Rates (Window Function)",
            "Driver Demographics by Country (Age, Gender, Race)",
            "Top 5 Violations with Highest Arrest Rates"
      ]
    )

    # SQL QUERIES
    queries = {
        "Top 10 vehicles involved in drug-related stops": """
        SELECT vehicle_number, COUNT(*) AS stop_count
        FROM Traffic_project
        WHERE drugs_related_stop = 1
        GROUP BY vehicle_number
        ORDER BY stop_count DESC
        LIMIT 10;
    """,
    "Vehicles most frequently searched": """
        SELECT vehicle_number, COUNT(*) AS search_count
        FROM Traffic_project
        WHERE search_conducted = TRUE
        GROUP BY vehicle_number
        ORDER BY search_count DESC;
    """,
    "Driver age group with highest arrest rate": """
        SELECT 
            CASE 
                WHEN driver_age < 30 THEN '<30'
                WHEN driver_age BETWEEN 30 AND 50 THEN '30-50'
                WHEN driver_age BETWEEN 51 AND 70 THEN '51-70'
                ELSE '>70'
            END AS age_group,
            SUM(stop_outcome='Arrest') AS total_arrest
        FROM Traffic_project
        GROUP BY age_group;
    """,
    "Gender distribution of drivers stopped in each country": """
        SELECT 
            country_name,
            driver_gender,
            COUNT(*) AS total_stops
        FROM Traffic_project
        GROUP BY country_name, driver_gender
        ORDER BY country_name, driver_gender;
    """,
    "Race and gender combination with highest search rate": """
        SELECT 
    driver_gender, 
    driver_race, 
    COUNT(*) AS total_stops, 
    SUM(CASE WHEN search_conducted = 1 THEN 1 ELSE 0 END) AS total_searches,
    ROUND(SUM(CASE WHEN search_conducted = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS search_rate_percent
FROM 
    Traffic_project
GROUP BY 
    driver_gender, driver_race
ORDER BY 
    search_rate_percent DESC;

    """,
    "Time of day with most traffic stops": """
        SELECT 
            stop_time, COUNT(*) AS traffic_time
        FROM Traffic_project
        GROUP BY stop_time
        ORDER BY traffic_time DESC;
    """,
    "Average stop duration for different violations": """
        SELECT
            violation,
            AVG(
                CASE
                    WHEN stop_duration = '0-15 Min' THEN 7
                    WHEN stop_duration = '16-30 Min' THEN 23
                    WHEN stop_duration = '30+ Min' THEN 35
                END
            ) AS avg_stop_duration_minutes
        FROM Traffic_project
        GROUP BY violation
        ORDER BY avg_stop_duration_minutes DESC;
    """,
    "Are stops during night more likely to lead to arrests?": """
        SELECT 
            CASE 
                WHEN HOUR(stop_time) BETWEEN 0 AND 5 THEN 'Night'
                ELSE 'Other'
            END AS time_of_day,
            COUNT(*) AS total_stops,
            SUM(stop_outcome='Arrest') AS total_arrests
        FROM Traffic_project
        GROUP BY time_of_day;
    """,
    "Violations most associated with searches or arrests": """
        SELECT 
            violation,
            SUM(search_conducted=1) AS total_searches,
            SUM(stop_outcome='Arrest') AS total_arrest
        FROM Traffic_project
        GROUP BY violation
        ORDER BY total_searches DESC, total_arrest DESC;
    """,
    "Violations most common among younger drivers (<25)": """
        SELECT 
            violation,
            COUNT(*) AS total_stop
        FROM Traffic_project
        WHERE driver_age < 25
        GROUP BY violation
        ORDER BY total_stop DESC;
    """,
    "Violation rarely results in search or arrest": """
        SELECT 
            violation,
            SUM(search_conducted=1) AS total_searches,
            SUM(stop_outcome='Arrest') AS total_arrests,
            COUNT(*) AS total_stop
        FROM Traffic_project
        GROUP BY violation
        ORDER BY total_searches ASC, total_arrests ASC;
    """,
    "Countries with highest rate of drug-related stops": """
        SELECT 
    country_name, 
    COUNT(*) AS total_stop, 
    SUM(IF(drugs_related_stop = 1, 1, 0)) AS drug_stop,
    ROUND(SUM(IF(drugs_related_stop = 1, 1, 0)) * 100.0 / COUNT(*), 2) AS drug_stop_rate_percent
FROM 
    Traffic_project
GROUP BY 
    country_name
ORDER BY 
    drug_stop DESC;

    """,
    "Arrest rate by country and violation": """
        SELECT 
    country_name, 
    violation, 
    COUNT(*) AS total_stop, 
    SUM(IF(stop_outcome = 'Arrest', 1, 0)) AS Arrest_stop,
    ROUND(SUM(IF(stop_outcome = 'Arrest', 1, 0)) * 100.0 / COUNT(*), 2) AS Arrest_rate_percent
FROM 
    Traffic_project
GROUP BY 
    country_name, violation
ORDER BY 
    Arrest_rate_percent DESC;

    """,
    "Country with most stops with search conducted": """
        SELECT 
            country_name,
            COUNT(*) AS total_stop,
            SUM(search_conducted=1) AS search_stop
        FROM Traffic_project
        GROUP BY country_name
        ORDER BY search_stop DESC;
    """,
    "Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions)": """
        SELECT 
            country_name,
            year,
            total_stops,
            total_arrests,
            ROUND(total_arrests*100.0/total_stops,2) AS arrest_rate_percent,
            RANK() OVER (PARTITION BY year ORDER BY total_arrests DESC) AS rank_by_arrests
        FROM (
            SELECT 
                country_name,
                YEAR(stop_date) AS year,
                COUNT(*) AS total_stops,
                SUM(stop_outcome = 'Arrest') AS total_arrests
            FROM Traffic_project
            GROUP BY country_name, YEAR(stop_date)
        ) AS yearly_data
        ORDER BY year, country_name;
    """,
    "Driver Violation Trends Based on Age and Race (Join with Subquery)": """
        SELECT
            ab.age_group AS age_group,
            p.driver_race AS race,
            p.violation AS violation,
            COUNT(*) AS stops
        FROM (
            SELECT driver_age, driver_race, violation
            FROM traffic_project
        ) AS p
        JOIN (
            SELECT DISTINCT
                driver_age,
                CASE
                    WHEN driver_age < 20 THEN 'Under 20'
                    WHEN driver_age BETWEEN 20 AND 30 THEN '20-30'
                    WHEN driver_age BETWEEN 31 AND 50 THEN '31-50'
                    ELSE '50+'
                END AS age_group
            FROM traffic_project
            WHERE driver_age IS NOT NULL
        ) AS ab
        ON p.driver_age = ab.driver_age
        GROUP BY ab.age_group, p.driver_race, p.violation
        ORDER BY age_group, race, violation;
    """,
    "Time Period Analysis of Stops (Year, Month, Hour)": """
       SELECT
    t.country_name,
    YEAR(t.stop_date) AS year,
    MONTH(t.stop_date) AS month,
    HOUR(t.stop_time) AS hour,
    COUNT(*) AS total_stops
FROM Traffic_project t
WHERE t.stop_date IS NOT NULL
  AND t.stop_time IS NOT NULL
GROUP BY
    t.country_name,
    YEAR(t.stop_date),
    MONTH(t.stop_date),
    HOUR(t.stop_time)
ORDER BY
    YEAR(t.stop_date),
    MONTH(t.stop_date),
    HOUR(t.stop_time),
    t.country_name;

    """,
    "Violations with High Search and Arrest Rates (Window Function)": """
        SELECT 
            violation,
            total_stops,
            total_searches,
            total_arrests,
            ROUND(total_searches*100.0/total_stops,2) AS search_rate_percent,
            ROUND(total_arrests*100.0/total_stops,2) AS arrest_rate_percent,
            RANK() OVER (ORDER BY (total_arrests*1.0/total_stops) DESC) AS rank_by_arrest_rate
        FROM (
            SELECT 
                violation,
                COUNT(*) AS total_stops,
                SUM(search_conducted = 1) AS total_searches,
                SUM(stop_outcome = 'Arrest') AS total_arrests
            FROM Traffic_project
            GROUP BY violation
        ) v
        ORDER BY arrest_rate_percent DESC;
    """,
    "Driver Demographics by Country (Age, Gender, Race)": """
        SELECT 
            COUNT(*) AS drivers,
            driver_age,
            country_name,
            driver_gender,
            driver_race
        FROM traffic_project
        GROUP BY driver_age, country_name, driver_gender, driver_race
        ORDER BY driver_age;
    """,
    "Top 5 Violations with Highest Arrest Rates": """
        SELECT 
            violation,
            COUNT(*) AS total_stops,
            SUM(stop_outcome = 'Arrest') AS total_arrests,
            ROUND(SUM(stop_outcome = 'Arrest') * 100.0 / COUNT(*),2) AS arrest_rate_percent
        FROM Traffic_project
        GROUP BY violation
        ORDER BY arrest_rate_percent DESC
        LIMIT 5;
    """
    }

    if query_option in queries:
        result_df = pd.read_sql(queries[query_option], engine)
        result_df = result_df.astype(str)
        st.write(f"**Results for: {query_option}**")
        st.dataframe(result_df)

except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.info("But Streamlit is working fine. Check your MySQL setup or table.")

# ---------------------------
# 🚔 ADD NEW POLICE LOG & PREDICT
# ---------------------------
st.markdown("---")
st.title("🚔 Add New Police Log & Predict Outcome and Violation")

stop_date = st.date_input("stop_date")
stop_time = st.time_input("stop_time")
country_name = st.selectbox("country_name", ["Canada", "India", "USA"])
driver_gender = st.selectbox("Driver Gender", ["M", "F"])
driver_age = st.number_input("Driver Age", min_value=16, max_value=100, step=1)
driver_race = st.text_input("Driver Race")
search_conducted = st.selectbox("Was a Search Conducted?", ["Yes", "No"])
search_type = st.text_input("Search Type (if any)")
drug_related = st.selectbox("Was it Drug Related?", ["Yes", "No"])
stop_duration = st.selectbox("Stop Duration", ["0-15 Min", "16-30 Min", "30+ Min"])
vehicle_number = st.text_input("Vehicle Number")

if st.button("Predict Stop Outcome & Violation"):
    try:
        # sanitize vehicle_number to avoid SQL syntax error / injection
        vn = (vehicle_number or "").strip()
        if vn == "":
            st.warning("Please enter a vehicle number to do exact lookup.")
        else:
            vn_safe = vn.replace("'", "''")  # escape single quotes for SQL
            sql = f"SELECT violation, stop_outcome FROM traffic_project WHERE vehicle_number = '{vn_safe}' LIMIT 1;"
            row = pd.read_sql(sql, engine)

            if row.empty:
                st.warning("No exact record found for this vehicle number.")
            else:
                predicted_violation = row.iloc[0]["violation"]
                predicted_outcome = row.iloc[0]["stop_outcome"]

                st.subheader("📝 Exact-match Prediction (from dataset)")
                st.markdown(f"- **Predicted Violation:** {predicted_violation}")
                st.markdown(f"- **Predicted Stop Outcome:** {predicted_outcome}")

                if search_conducted == "No":
                    search_text = "No search was conducted"
                else:
                    search_text = f"A search was conducted ({search_type})"

                summary = (
                    f"🚗 A {driver_age}-year-old {driver_gender} driver was stopped for "
                    f"**{predicted_violation}** at {stop_time.strftime('%I:%M %p')}. "
                    f"{search_text}, and received a **{predicted_outcome}**. "
                    f"The stop lasted {stop_duration} and was "
                    f"{'drug-related' if drug_related == 'Yes' else 'not drug-related'}."
                )

                st.write(summary)

    except Exception as e:
        st.error(f"Lookup failed: {e}")
