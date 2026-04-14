import streamlit as st
import plotly.graph_objects as go


def plot_graph(results, selected_op, selected_metric):

    df_filtered = results[results["operation"] == selected_op]

    df_plot = df_filtered.groupby("timestamp").agg({
        selected_metric: "max",
        f"pred_{selected_metric}": "max"
    }).reset_index()

    # Smooth curves
    df_plot["actual_smooth"] = df_plot[selected_metric].rolling(3, center=True).mean()
    df_plot["pred_smooth"] = df_plot[f"pred_{selected_metric}"].rolling(3, center=True).mean()

    # Anomaly points
    df_anomaly = df_filtered[
        (df_filtered["Status"] != "Normal ✅") &
        (df_filtered["Root_Cause"].fillna("") == selected_metric)
    ]

    df_anomaly = df_anomaly.groupby("timestamp").agg({
        "Severity": "max"
    }).reset_index()

    df_anomaly = df_plot.merge(df_anomaly, on="timestamp", how="inner")

    fig = go.Figure()

    # Actual
    fig.add_trace(go.Scatter(
        x=df_plot["timestamp"],
        y=df_plot["actual_smooth"],
        mode="lines",
        name="Actual"
    ))

    # Predicted
    fig.add_trace(go.Scatter(
        x=df_plot["timestamp"],
        y=df_plot["pred_smooth"],
        mode="lines",
        name="Predicted",
        line=dict(dash="dash")
    ))

    # Anomaly markers
    sev = df_anomaly["Severity"].clip(0, 5)

    fig.add_trace(go.Scatter(
        x=df_anomaly["timestamp"],
        y=df_anomaly["actual_smooth"],
        mode="markers",
        name="Anomaly",
        marker=dict(
            size=10,
            color=sev,
            colorscale="Reds",
            cmin=0,
            cmax=5,
            showscale=True,
            colorbar=dict(title="Severity", thickness=20, len=0.5)
        )
    ))

    fig.update_layout(
        xaxis_title="Time",
        yaxis_title=selected_metric,
        height=450
    )

    st.plotly_chart(fig, use_container_width=True)