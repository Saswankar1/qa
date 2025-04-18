import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Backend API endpoint
API_URL = "http://127.0.0.1:8000/query"

# Detect chart type from question
def detect_chart_type(question):
    q = question.lower()
    if "pie chart" in q:
        return "Pie"
    elif "bar chart" in q:
        return "Bar"
    elif "line chart" in q:
        return "Line"
    elif "area chart" in q:
        return "Area"
    return None  # No chart type mentioned

# Page config
st.set_page_config(page_title="Retail Q&A Tool", page_icon="📊", layout="centered")
st.title("🗄️ Retail Q&A Tool - Natural Language to SQL")

# User input
question = st.text_input("Ask a database question:", placeholder="e.g., Show all products with a bar chart")

if st.button("Generate SQL & Query Database"):
    if question.strip():
        st.info("🔍 Processing your query. Please wait...")

        try:
            response = requests.post(API_URL, json={"question": question})

            if response.status_code == 200:
                data = response.json()
                sql_query = data.get("sql_query", "No SQL generated")
                result = data.get("result", [])

                st.subheader("📝 Generated SQL Query:")
                st.code(sql_query, language="sql")

                st.subheader("📊 Query Results:")
                if isinstance(result, list) and result:
                    df = pd.DataFrame(result)

                    # Convert numeric types
                    df = df.convert_dtypes()
                    for col in df.columns:
                        try:
                            df[col] = pd.to_numeric(df[col])
                        except:
                            pass

                    st.dataframe(df, use_container_width=True)

                    # Detect if a chart was requested
                    chart_type = detect_chart_type(question)

                    if chart_type:
                        st.subheader(f"📈 {chart_type} Chart")

                        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
                        non_numeric_cols = df.select_dtypes(exclude=["number"]).columns.tolist()

                        if chart_type == "Pie":
                            if numeric_cols and non_numeric_cols:
                                label_col = st.selectbox("Label column (categories):", non_numeric_cols)
                                value_col = st.selectbox("Value column (numerical):", numeric_cols)
                                fig = px.pie(df, names=label_col, values=value_col, title=f"{label_col} vs {value_col}")
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("ℹ️ Pie chart requires both a categorical and numeric column.")

                        elif chart_type in ["Bar", "Line", "Area"]:
                            if numeric_cols:
                                x_axis = st.selectbox("X-axis:", df.columns)
                                y_axis = st.selectbox("Y-axis (numeric):", numeric_cols)

                                if chart_type == "Bar":
                                    fig = px.bar(df, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
                                elif chart_type == "Line":
                                    fig = px.line(df, x=x_axis, y=y_axis, title=f"{y_axis} over {x_axis}")
                                elif chart_type == "Area":
                                    fig = px.area(df, x=x_axis, y=y_axis, title=f"{y_axis} over {x_axis}")

                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("ℹ️ No numeric data available to generate the chart.")
                    else:
                        st.info("ℹ️ No chart type requested in the question. Showing only table.")
                elif isinstance(result, dict) and "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                else:
                    st.warning("⚠️ No data returned for this query.")
            else:
                st.error("❌ API request failed. Make sure your FastAPI server is running.")
        except Exception as e:
            st.error(f"🚨 Unexpected error: {e}")
    else:
        st.warning("⚠️ Please enter a valid question.")
