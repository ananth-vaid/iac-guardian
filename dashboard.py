#!/usr/bin/env python3
"""
IaC Guardian - Management Dashboard
Datadog-style executive dashboard for FinOps and engineering managers
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="IaC Guardian - Management Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .risk-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .risk-critical { background: #f44336; color: white; }
    .risk-high { background: #ff9800; color: white; }
    .risk-medium { background: #ffc107; color: black; }
    .risk-low { background: #4caf50; color: white; }
</style>
""", unsafe_allow_html=True)


def get_mock_data():
    """Generate mock analytics data"""

    # This week's activity
    dates = pd.date_range(end=datetime.now(), periods=7, freq='D')

    return {
        'summary': {
            'prs_analyzed': 47,
            'risks_blocked': 8,
            'cost_saved': 428000,
            'outages_prevented': 3,
            'auto_fixes': 12,
            'avg_detection_time': 8.5
        },
        'daily_activity': pd.DataFrame({
            'date': dates,
            'prs_analyzed': [5, 8, 6, 9, 7, 8, 4],
            'risks_found': [1, 2, 1, 2, 1, 1, 0],
            'costs_saved': [12000, 35000, 8000, 156000, 42000, 150000, 25000]
        }),
        'risk_feed': [
            {
                'pr': '#342', 'repo': 'payments-infra', 'title': 'Reduce payment-api replicas',
                'risk': 'CRITICAL', 'impact': '$2M outage prevented',
                'status': 'Blocked', 'time': '2 hours ago'
            },
            {
                'pr': '#289', 'repo': 'data-platform', 'title': 'Scale up processing cluster',
                'risk': 'HIGH', 'impact': '$282k annual savings',
                'status': 'Auto-fix created', 'time': '5 hours ago'
            },
            {
                'pr': '#256', 'repo': 'api-gateway', 'title': 'Update cert manager version',
                'risk': 'MEDIUM', 'impact': 'Security compliance',
                'status': 'Approved', 'time': '1 day ago'
            },
            {
                'pr': '#234', 'repo': 'auth-service', 'title': 'Add rate limiting',
                'risk': 'LOW', 'impact': 'Best practice',
                'status': 'Approved', 'time': '1 day ago'
            },
            {
                'pr': '#198', 'repo': 'database-infra', 'title': 'Upgrade RDS instances',
                'risk': 'HIGH', 'impact': '$45k over-provisioning',
                'status': 'Auto-fix created', 'time': '2 days ago'
            },
        ],
        'top_repos': [
            {'repo': 'payments-infra', 'risks': 12, 'cost_impact': 245000},
            {'repo': 'data-platform', 'risks': 8, 'cost_impact': 156000},
            {'repo': 'api-gateway', 'risks': 5, 'cost_impact': 18000},
            {'repo': 'auth-service', 'risks': 3, 'cost_impact': 9000},
        ],
        'cost_timeline': pd.DataFrame({
            'week': ['Week 1', 'Week 2', 'Week 3', 'Week 4 (current)'],
            'detected': [125000, 98000, 156000, 428000],
            'saved': [85000, 72000, 124000, 285000]
        })
    }


def main():
    # Header
    st.title("🛡️ IaC Guardian - Management Dashboard")
    st.markdown("*Real-time infrastructure change analytics powered by AI*")

    # Time range selector
    col1, col2, col3 = st.columns([3, 1, 1])
    with col2:
        time_range = st.selectbox("Time Range", ["Last 7 days", "Last 30 days", "Last 90 days"])
    with col3:
        auto_refresh = st.checkbox("Auto-refresh", value=True)

    st.divider()

    # Get data
    data = get_mock_data()

    # Summary metrics
    st.markdown("## 📊 Key Metrics")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric(
            "PRs Analyzed",
            data['summary']['prs_analyzed'],
            delta="+12 vs last week",
            help="Total infrastructure PRs analyzed"
        )

    with col2:
        st.metric(
            "Risks Blocked",
            data['summary']['risks_blocked'],
            delta="-2 vs last week",
            delta_color="inverse",
            help="High/Critical risks that were blocked"
        )

    with col3:
        st.metric(
            "Cost Impact",
            f"${data['summary']['cost_saved']:,}",
            delta="+$156k vs last week",
            help="Total potential cost waste detected"
        )

    with col4:
        st.metric(
            "Outages Prevented",
            data['summary']['outages_prevented'],
            delta="+1 vs last week",
            help="Estimated production incidents avoided"
        )

    with col5:
        st.metric(
            "Auto-Fixes",
            data['summary']['auto_fixes'],
            delta="+4 vs last week",
            help="Automatic remediation PRs created"
        )

    with col6:
        st.metric(
            "Detection Time",
            f"{data['summary']['avg_detection_time']}s",
            delta="-1.2s vs last week",
            delta_color="inverse",
            help="Average time to analyze PR"
        )

    st.divider()

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 Daily Activity")

        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='PRs Analyzed',
            x=data['daily_activity']['date'],
            y=data['daily_activity']['prs_analyzed'],
            marker_color='lightblue'
        ))

        fig.add_trace(go.Bar(
            name='Risks Found',
            x=data['daily_activity']['date'],
            y=data['daily_activity']['risks_found'],
            marker_color='coral'
        ))

        fig.update_layout(
            barmode='group',
            height=300,
            showlegend=True,
            xaxis_title='',
            yaxis_title='Count'
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 💰 Cost Impact Timeline")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=data['cost_timeline']['week'],
            y=data['cost_timeline']['detected'],
            name='Issues Detected',
            mode='lines+markers',
            line=dict(color='red', width=3),
            marker=dict(size=10)
        ))

        fig.add_trace(go.Scatter(
            x=data['cost_timeline']['week'],
            y=data['cost_timeline']['saved'],
            name='Costs Saved',
            mode='lines+markers',
            line=dict(color='green', width=3),
            marker=dict(size=10)
        ))

        fig.update_layout(
            height=300,
            showlegend=True,
            xaxis_title='',
            yaxis_title='Amount ($)'
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Risk feed and top repos
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 🚨 Recent Risk Detections")

        for item in data['risk_feed']:
            with st.container():
                cols = st.columns([1, 3, 2, 1, 1])

                with cols[0]:
                    risk_class = f"risk-{item['risk'].lower()}"
                    st.markdown(
                        f'<span class="risk-badge {risk_class}">{item["risk"]}</span>',
                        unsafe_allow_html=True
                    )

                with cols[1]:
                    st.markdown(f"**{item['repo']}** #{item['pr']}")
                    st.caption(item['title'])

                with cols[2]:
                    st.write(item['impact'])

                with cols[3]:
                    st.write(item['status'])

                with cols[4]:
                    st.caption(item['time'])

                st.markdown("---")

    with col2:
        st.markdown("### 🎯 Top Repositories")

        for repo in data['top_repos']:
            with st.container():
                st.markdown(f"**{repo['repo']}**")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.caption(f"{repo['risks']} risks")
                with col_b:
                    st.caption(f"${repo['cost_impact']:,}")
                st.progress(repo['risks'] / 15)
                st.markdown("")

    st.divider()

    # ROI calculation
    st.markdown("## 💡 Return on Investment")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Outages Prevented")
        st.markdown(f"**{data['summary']['outages_prevented']}** incidents")
        st.caption("Avg cost per incident: $2M")
        st.markdown(f"### Total Value: **${data['summary']['outages_prevented'] * 2000000:,}**")

    with col2:
        st.markdown("### Cost Waste Avoided")
        st.markdown(f"**${data['summary']['cost_saved']:,}** this week")
        st.caption("Annualized: $22.3M")
        st.markdown("### Annual Savings: **$22.3M**")

    with col3:
        st.markdown("### Engineering Time Saved")
        st.markdown(f"**{data['summary']['auto_fixes']}** auto-fixes")
        st.caption("Avg 4 hours per fix")
        st.markdown(f"### Time Saved: **{data['summary']['auto_fixes'] * 4} hours**")

    # Footer
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} • IaC Guardian v1.0 • Powered by Claude & Datadog")


if __name__ == "__main__":
    main()
