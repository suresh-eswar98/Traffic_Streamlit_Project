import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime, date, time


# ----------------------------
# MySQL connection function
# ----------------------------
def get_connection():
    return mysql.connector.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='Sureshsk@12345',
        database='vehicle'
    )


# ----------------------------
# Traffic Query Form
# ----------------------------
st.title("🚓 Traffic Data Query")

with st.form("traffic_form"):
    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time")
    country_name = st.selectbox("Country Name", ["Canada", "India", "USA"])
    driver_gender = st.selectbox("Driver Gender", ["", "M", "F"])
    driver_age = st.number_input("Driver Age", min_value=0, max_value=120, step=1)
    driver_race = st.selectbox("Driver Race",["Asian", "Other", "Black","White","Hispanic"])
    search_conducted = st.selectbox("Search Conducted", ["", "Yes", "No"])
    search_type = st.text_input("Search Type")
    stop_duration = st.selectbox("Stop Duration", ["", "0-15 Min", "16-30 Min", "30+ Min"])
    drugs_related_stop = st.selectbox("Drugs Related Stop", ["", "Yes", "No"])
    vehicle_number = st.text_input("Vehicle Number(s) (comma separated)")

    submitted = st.form_submit_button("Stop Outcome & Violation Predict")

# ----------------------------
# Process form submission
# ----------------------------
if submitted:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # ----------------------------
        # Base query
        # ----------------------------
        query = """
            SELECT stop_date, stop_time, country_name, driver_gender, driver_age, driver_race,
                   violation, search_conducted, search_type,
                   stop_outcome, is_arrested, stop_duration, drugs_related_stop, vehicle_number
            FROM vehicle.traffic_project
        """

        and_conditions = []
        or_conditions = []
        values = []

        # Date OR Time inside parentheses
        date_time_conditions = []
        if stop_date:
            date_time_conditions.append("stop_date=%s")
            values.append(stop_date)
        if stop_time:
            date_time_conditions.append("stop_time=%s")
            values.append(stop_time)
        if date_time_conditions:
            and_conditions.append("(" + " OR ".join(date_time_conditions) + ")")

        # Other AND conditions
        if country_name:
            and_conditions.append("country_name=%s")
            values.append(country_name)
        if driver_gender:
            and_conditions.append("driver_gender=%s")
            values.append(driver_gender)
        if driver_age != 0:
            and_conditions.append("driver_age=%s")
            values.append(driver_age)
        if driver_race:
            and_conditions.append("driver_race=%s")
            values.append(driver_race)
        if search_conducted:
            and_conditions.append("search_conducted=%s")
            values.append(1 if search_conducted == "Yes" else 0)
        if search_type:
            and_conditions.append("search_type=%s")
            values.append(search_type)
        if stop_duration:
            and_conditions.append("stop_duration=%s")
            values.append(stop_duration)
        if drugs_related_stop:
            and_conditions.append("drugs_related_stop=%s")
            values.append(1 if drugs_related_stop == "Yes" else 0)

        # Vehicle_number as OR condition outside
        if vehicle_number:
            vehicle_list = [v.strip() for v in vehicle_number.split(",") if v.strip()]
            if vehicle_list:
                placeholders = ", ".join(["%s"] * len(vehicle_list))
                or_conditions.append(f"vehicle_number IN ({placeholders})")
                values.extend(vehicle_list)

        # Combine AND and OR conditions
        all_conditions = ""
        if and_conditions:
            all_conditions += " AND ".join(and_conditions)
        if or_conditions:
            if all_conditions:
                all_conditions = "(" + all_conditions + ") OR " + " OR ".join(or_conditions)
            else:
                all_conditions = " OR ".join(or_conditions)

        if all_conditions:
            query += " WHERE " + all_conditions

        query += " LIMIT 1"

        # Debug: Print formatted query
        formatted_query = query
        for v in values:
            if isinstance(v, str):
                v_formatted = f"'{v}'"
            elif isinstance(v, (date, time, datetime)):
                v_formatted = f"'{v}'"
            else:
                v_formatted = str(v)
            formatted_query = formatted_query.replace("%s", v_formatted, 1)

        print("Executing query:")
        print(formatted_query)

        # Execute query
        cursor.execute(query, values)
        record = cursor.fetchone()

        if record:
            (stop_date, stop_time, country_name, driver_gender, driver_age, driver_race,
             violation, search_conducted, search_type,
             stop_outcome, is_arrested, stop_duration, drugs_related_stop, vehicle_number) = record

            st.success("✅ Record found!")
            st.subheader("🚦 Query Result:")

            # Mask vehicle number if empty or NULL
            display_vehicle = vehicle_number if vehicle_number else "****"

            result_text = f"""
🚗 On *{stop_date}* at *{stop_time}, a *{driver_age}-year-old {driver_gender} driver** belonging to the *{driver_race}* race in *{country_name}* was stopped for *{violation}*.

Vehicle Number: *{display_vehicle}*
"""
            st.markdown(result_text)
        else:
            st.warning(" No record found matching your input.")

        cursor.close()
        conn.close()

    except Exception as e:
        st.error(f" Error: {e}")


# -----------------------
# Traffic Data Analysis
# -----------------------
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
            d.year,
            d.month,
            d.hour,
            COUNT(*) AS total_stops
        FROM Traffic_project t
        JOIN (
            SELECT 
                stop_date,
                YEAR(stop_date) AS year,
                MONTH(stop_date) AS month,
                HOUR(stop_time) AS hour
            FROM Traffic_project
        ) d
        ON t.stop_date = d.stop_date
        GROUP BY t.country_name, d.year, d.month, d.hour
        ORDER BY d.year, d.month, d.hour, t.country_name;
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

st.title("Traffic Data Analysis")
question = st.selectbox("Select a Question", list(queries.keys()))

if st.button("Run Query"):
    try:
        conn = get_connection()
        df = pd.read_sql(queries[question], conn)
        conn.close()
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error running query: {e}")