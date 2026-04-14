import streamlit as st
from core.pipeline import run_pipeline
from utils.plotting import plot_graph
from utils.evaluate import evaluate

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(page_title="SLA Dashboard", layout="wide")
st.title("🚨 SLA Anomaly Detection Dashboard")

# =========================================
# SIDEBAR
# =========================================
st.sidebar.header("Controls")

hours = st.sidebar.slider("Test Duration (hours)", 24, 168, 48)

# backend = st.sidebar.selectbox(
#     "Select Inference Backend",
#     ["FastAPI", "SageMaker"]
# )

run_button = st.sidebar.button("Run Pipeline")

# =========================================
# SESSION STATE
# =========================================
if "results" not in st.session_state:
    st.session_state.results = None

# =========================================
# RUN PIPELINE
# =========================================
if run_button:
    with st.spinner("Running pipeline..."):
        results = run_pipeline(hours)

    st.session_state.results = results
    st.success("Pipeline completed")

# =========================================
# DASHBOARD
# =========================================
if st.session_state.results is not None:

    results = st.session_state.results

    # =========================================
    # TABLES (TOP)
    # =========================================
    st.subheader("📊 Sample Data")
    st.dataframe(results.head())

    st.subheader("🚨 Detected Anomalies")
    anomalies = results[results["Status"] != "Normal ✅"]
    st.metric("Total Alerts", len(anomalies))
    st.dataframe(anomalies)

    # ----------------------------
    # METRICS
    # ----------------------------
    st.subheader("📈 Evaluation Metrics")

    metrics = evaluate(results)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Precision", f"{metrics['precision']:.3f}")
    col2.metric("Recall", f"{metrics['recall']:.3f}")
    col3.metric("F1 Score", f"{metrics['f1']:.3f}")
    col4.metric("Alert Rate", f"{metrics['alert_rate']:.3f}")

    # ----------------------------
    # ANOMALY TYPE BREAKDOWN
    # ----------------------------
    st.subheader("🔍 Anomaly Breakdown")

    if "anomaly_type" in results.columns:
        breakdown = results[results["is_anomaly"]]["anomaly_type"].value_counts()
        st.bar_chart(breakdown)

    # =========================================
    # FILTERS (MAIN PANEL)
    # =========================================
    st.subheader("🔍 Filters")

    col1, col2 = st.columns(2)

    with col1:
        operations = results["operation"].unique()
        selected_op = st.selectbox("Select Operation", operations)

    with col2:
        metrics = [
            "success_vol",
            "fail_vol",
            "success_rt_avg",
            "fail_rt_avg"
        ]
        selected_metric = st.selectbox("Select Metric", metrics)

    # =========================================
    # GRAPH (ONLY THIS UPDATES)
    # =========================================
    st.subheader("📈 Trend Analysis")
    plot_graph(results, selected_op, selected_metric)

else:
    st.info("Use the sidebar to run the pipeline")