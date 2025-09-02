🔎 Project Overview

SecureCheck is a real-time monitoring system designed for police check posts. It uses Python + SQL + Streamlit to log, analyze, and display vehicle stop records in an efficient and centralized way.

Instead of traditional manual logging, SecureCheck enables:

Centralized SQL database for storing stop records.

Python data processing for cleaning and analytics.

Streamlit dashboard for real-time monitoring, filtering, and reporting.

🛠 Skills You’ll Gain

Python → Data cleaning, preprocessing, analytics.

SQL (PostgreSQL/MySQL/SQLite) → Schema design, queries, joins, and window functions.

Streamlit → Building dashboards and real-time reporting apps.

🌍 Domain & Business Use Cases

Domain: Law Enforcement & Public Safety

Use Cases:

Real-time logging of vehicles and officers’ activities.

Automatic detection of suspect/flagged vehicles using SQL filters.

Monitoring check post efficiency (stop duration, number of arrests).

Crime pattern analysis by demographics, location, or time.

Centralized multi-location database for connected check posts.

📌 Approach

Data Processing (Python)

Handle missing values & clean age/violation columns.

Convert categorical values for analysis.

Database Design (SQL)

Create a traffic_stops table with fields like stop_date, stop_time, country_name, driver_gender, violation, stop_outcome.

Insert cleaned records into SQL.

Streamlit Dashboard

Display logs (vehicle info, violation, stop outcome).

Search & filter with SQL queries.

Show analytics & trends:

Arrest rates by age/gender/country.

High-risk violations.

Time-of-day stop distribution.

🗂 Dataset (traffic_stops)

Key features:

Date & Time: stop_date, stop_time

Driver Info: driver_gender, driver_age, driver_race

Violation Info: violation, violation_raw, stop_outcome, is_arrested

Search Info: search_conducted, search_type, drugs_related_stop

Duration & Location: stop_duration, country_name

🔑 Example Use Case

🚗 A 27-year-old male driver was stopped for Speeding at 2:30 PM.
No search conducted → Received Citation.
Stop lasted 6–15 minutes, not drug-related.

This example maps directly to the dataset fields.

📊 SQL Queries (Analysis Scope)

Vehicle-Based: Top 10 vehicles in drug-related stops, most searched vehicles.

Demographic-Based: Arrest rates by age, gender distribution by country, race-gender search rates.

Time & Duration: Peak stop times, average stop duration by violation, arrest likelihood at night.

Violation-Based: Common violations among <25, high-risk violations, rare violations for arrests.

Location-Based: Countries with highest drug-related stops, arrest rates by country, search-conducted analysis.

Complex Queries: Window functions, yearly breakdowns, violation trends, demographic breakdowns.

✅ Results

Faster check post operations (optimized SQL lookups).

Automated alerts for flagged vehicles.

Real-time monitoring of violations & arrests.

Data-driven decision-making for law enforcement agencies.

📈 Project Evaluation Metrics

Query Execution Time → Are queries optimized?

Data Accuracy → No missing/misclassified entries.

System Uptime → Real-time dashboard updates.

User Engagement → Ease of use for officers.

Violation Detection Rate → % of flagged vehicles caught.