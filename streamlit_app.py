import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
import re # Added for milestone analysis

from github_client import GitHubClient
from data_processor import GrantDataProcessor
from database import GrantDatabase
from ai_evaluator import AIEvaluator

# Try to import config, with fallbacks
try:
    from config import GRANT_REPOSITORIES, STREAMLIT_CONFIG
except ImportError:
    # Fallback values if config module is not available
    GRANT_REPOSITORIES = {
        "w3f_grants": {
            "owner": "w3f",
            "repo": "Grants-Program",
            "type": "pull_request",
            "description": "Web3 Foundation Grants Program"
        },
        "polkadot_fast_grants": {
            "owner": "Polkadot-Fast-Grants",
            "repo": "apply",
            "type": "pull_request",
            "description": "Polkadot Fast Grants"
        },
        "use_inkubator": {
            "owner": "use-inkubator",
            "repo": "Ecosystem-Grants",
            "type": "pull_request",
            "description": "Use Inkubator Ecosystem Grants"
        },
        "polkadot_open_source": {
            "owner": "PolkadotOpenSourceGrants",
            "repo": "apply",
            "type": "pull_request",
            "description": "Polkadot Open Source Grants"
        }
    }
    STREAMLIT_CONFIG = {
        "page_title": "Polkadot Grant Analyzer",
        "page_icon": "📊",
        "layout": "wide"
    }

# Configure Streamlit page
st.set_page_config(
    page_title=STREAMLIT_CONFIG["page_title"],
    page_icon=STREAMLIT_CONFIG["page_icon"],
    layout=STREAMLIT_CONFIG["layout"]
)

# Initialize components
@st.cache_resource
def init_components():
    return {
        'github_client': GitHubClient(),
        'data_processor': GrantDataProcessor(),
        'database': GrantDatabase(),
        'ai_evaluator': AIEvaluator()
    }

components = init_components()

def main():
    st.title("🚀 Polkadot Grant Analyzer")
    st.markdown("Comprehensive analysis of Polkadot grant proposals across multiple programs")
    
    # Sidebar for controls
    st.sidebar.header("Controls")
    
    # Data refresh section
    st.sidebar.subheader("Data Management")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Data"):
            # Create progress containers
            progress_container = st.empty()
            stats_container = st.empty()
            status_container = st.empty()
            
            try:
                # Step 1: Fetching data
                status_container.info("🔄 Fetching grant proposals from GitHub...")
                progress_container.progress(0)
                
                # Fetch data with progress updates
                proposals = {}
                total_repos = 4  # W3F, Fast Grants, Use Inkubator, Open Source
                current_repo = 0
                
                # Import GRANT_REPOSITORIES from config or use fallback
                try:
                    from config import GRANT_REPOSITORIES
                except ImportError:
                    GRANT_REPOSITORIES = {
                        "w3f_grants": {
                            "owner": "w3f",
                            "repo": "Grants-Program",
                            "type": "pull_request",
                            "description": "Web3 Foundation Grants Program"
                        },
                        "polkadot_fast_grants": {
                            "owner": "Polkadot-Fast-Grants",
                            "repo": "apply",
                            "type": "pull_request",
                            "description": "Polkadot Fast Grants"
                        },
                        "use_inkubator": {
                            "owner": "use-inkubator",
                            "repo": "Ecosystem-Grants",
                            "type": "pull_request",
                            "description": "Use Inkubator Ecosystem Grants"
                        },
                        "polkadot_open_source": {
                            "owner": "PolkadotOpenSourceGrants",
                            "repo": "apply",
                            "type": "pull_request",
                            "description": "Polkadot Open Source Grants"
                        }
                    }
                
                # Fetch all proposals with progress updates
                status_container.info("📥 Fetching all grant proposals...")
                progress_container.progress(0.25)
                
                try:
                    proposals = components['github_client'].fetch_all_grant_proposals()
                    
                    # Update real-time stats
                    total_proposals = sum(len(props) for props in proposals.values())
                    stats_container.metric("Proposals Fetched", total_proposals)
                    
                    # Show progress for each repository
                    for i, (repo_name, repo_proposals) in enumerate(proposals.items()):
                        repo_config = GRANT_REPOSITORIES.get(repo_name, {})
                        repo_description = repo_config.get('description', repo_name)
                        status_container.info(f"✅ Fetched {len(repo_proposals)} proposals from {repo_description}")
                        
                except Exception as e:
                    st.error(f"❌ Error fetching proposals: {e}")
                    return
                
                # Step 2: Processing data
                status_container.info("⚙️ Processing proposals and calculating metrics...")
                progress_container.progress(0.5)
                
                # Process data
                df = components['data_processor'].process_proposals(proposals)
                
                # Update stats
                stats_container.metric("Proposals Processed", len(df))
                
                # Step 3: Saving data
                status_container.info("💾 Saving data to storage...")
                progress_container.progress(0.75)
                
                # Save to storage - pass the DataFrame directly since it has all calculated fields
                success = components['database'].save_proposals(df)
                if success:
                    # Calculate and save metrics
                    summary_stats = components['data_processor'].get_summary_stats(df)
                    program_stats = components['data_processor'].get_program_stats(df)
                    curator_stats = components['data_processor'].get_curator_stats(df)
                    
                    metrics = {
                        'summary_stats': summary_stats,
                        'program_stats': program_stats,
                        'curator_stats': curator_stats
                    }
                    components['database'].save_metrics(metrics)
                    
                    # Final progress
                    progress_container.progress(1.0)
                    status_container.success("✅ Data refresh completed!")
                    
                    # Show final statistics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Proposals", len(df))
                    with col2:
                        approved = len(df[df['category'] == 'APPROVED'])
                        st.metric("Approved", approved)
                    with col3:
                        rejected = len(df[df['category'] == 'REJECTED'])
                        st.metric("Rejected", rejected)
                    with col4:
                        approval_rate = (approved / len(df)) * 100 if len(df) > 0 else 0
                        st.metric("Approval Rate", f"{approval_rate:.1f}%")
                    
                    # Show program breakdown
                    st.subheader("📊 Program Breakdown")
                    program_counts = df['repository'].value_counts()
                    for program, count in program_counts.items():
                        st.write(f"• **{program}**: {count} proposals")
                    
                    st.success(f"✅ Successfully loaded {len(df)} proposals from {len(proposals)} repositories!")
                else:
                    progress_container.progress(1.0)
                    status_container.error("❌ Failed to save data to storage.")
                
                # Clear progress containers after a delay
                import time
                time.sleep(3)
                progress_container.empty()
                stats_container.empty()
                status_container.empty()
                
                st.rerun()
                
            except Exception as e:
                progress_container.empty()
                stats_container.empty()
                status_container.error(f"❌ Error refreshing data: {e}")
                st.error(f"Error refreshing data: {e}")
    
    with col2:
        if st.button("🗑️ Clear Storage"):
            if st.sidebar.checkbox("Confirm clear"):
                components['database'].clear_database()
                st.success("Storage cleared!")
                st.rerun()
    
    # Show storage info
    storage_info = components['database'].get_database_info()
    st.sidebar.subheader("Storage Info")
    st.sidebar.write(f"**Type:** {storage_info.get('storage_type', 'Unknown')}")
    st.sidebar.write(f"**Proposals:** {storage_info.get('proposals_count', 0)}")
    st.sidebar.write(f"**Metrics:** {storage_info.get('metrics_count', 0)}")
    
    if storage_info.get('last_updated'):
        st.sidebar.write(f"**Last Updated:** {storage_info.get('last_updated', 'Unknown')}")
    
    # Real-time statistics section
    st.sidebar.subheader("📊 Real-time Stats")
    
    # Auto-refresh stats every 30 seconds
    if st.sidebar.checkbox("🔄 Auto-refresh stats", value=True):
        st.sidebar.write("Stats will update automatically")
    
    # Load data
    try:
        df = components['database'].load_proposals()
        metrics = components['database'].load_metrics()
        
        if df.empty:
            st.warning("📊 No data available. Please click '🔄 Refresh Data' to fetch the latest grant proposals.")
            st.info("💡 This will fetch real data from GitHub repositories including W3F Grants, Polkadot Fast Grants, Use Inkubator, and Polkadot Open Source Grants.")
            return
            
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("💡 Try refreshing the data or check your GitHub token configuration.")
        return
    
    # Show real-time statistics
    if not df.empty:
        # Calculate real-time stats
        total_proposals = len(df)
        approved_proposals = len(df[df['category'] == 'APPROVED'])
        rejected_proposals = len(df[df['category'] == 'REJECTED'])
        pending_proposals = len(df[df['category'] == 'PENDING'])
        stale_proposals = len(df[df['category'] == 'STALE'])
        approval_rate = (approved_proposals / total_proposals * 100) if total_proposals > 0 else 0
        
        # Display real-time stats in sidebar
        st.sidebar.metric("📈 Total Proposals", total_proposals)
        st.sidebar.metric("✅ Approved", approved_proposals)
        st.sidebar.metric("❌ Rejected", rejected_proposals)
        st.sidebar.metric("⏳ Pending", pending_proposals)
        st.sidebar.metric("🔄 Stale", stale_proposals)
        st.sidebar.metric("📊 Approval Rate", f"{approval_rate:.1f}%")
        
        # Show recent activity
        if 'created_at' in df.columns:
            recent_proposals = df.sort_values('created_at', ascending=False).head(3)
            st.sidebar.subheader("🕒 Recent Activity")
            for _, proposal in recent_proposals.iterrows():
                st.sidebar.write(f"• **{proposal['title'][:30]}...** ({proposal['category']})")
        
        # Show top repositories
        repo_counts = df['repository'].value_counts().head(3)
        st.sidebar.subheader("🏆 Top Programs")
        for repo, count in repo_counts.items():
            st.sidebar.write(f"• **{repo}**: {count} proposals")
    
    # Program selection
    st.sidebar.subheader("Program Selection")
    all_programs = ['All Programs'] + list(df['repository'].unique())
    selected_programs = st.sidebar.multiselect(
        "Select Grant Programs",
        all_programs,
        default=['All Programs']
    )
    
    # Filter data based on selected programs
    if 'All Programs' in selected_programs or not selected_programs:
        filtered_df = df
    else:
        filtered_df = df[df['repository'].isin(selected_programs)]
    
    # Main dashboard
    st.header("📊 Live Grant Analysis Dashboard")
    
    # Real-time progress indicator
    if st.checkbox("🔄 Show live updates", value=True):
        st.info("📡 Dashboard is updating in real-time")
    
    # Auto-refresh the page every 30 seconds for live updates
    if st.checkbox("🔄 Auto-refresh dashboard", value=False):
        st.write("Dashboard will refresh every 30 seconds")
    
    # Live statistics with better formatting
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📈 Total Proposals", 
            len(filtered_df),
            delta=f"+{len(filtered_df)} total"
        )
    
    with col2:
        approved = len(filtered_df[filtered_df['category'] == 'APPROVED'])
        st.metric(
            "✅ Approved Proposals", 
            approved,
            delta=f"{approved} approved"
        )
    
    with col3:
        rejected = len(filtered_df[filtered_df['category'] == 'REJECTED'])
        st.metric(
            "❌ Rejected Proposals", 
            rejected,
            delta=f"{rejected} rejected"
        )
    
    with col4:
        approval_rate = (approved / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
        st.metric(
            "📊 Approval Rate", 
            f"{approval_rate:.1f}%",
            delta=f"{approval_rate:.1f}% rate"
        )
    
    # Additional live metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pending = len(filtered_df[filtered_df['category'] == 'PENDING'])
        st.metric("⏳ Pending", pending)
    
    with col2:
        stale = len(filtered_df[filtered_df['category'] == 'STALE'])
        st.metric("🔄 Stale", stale)
    
    with col3:
        unique_authors = filtered_df['author'].nunique()
        st.metric("👤 Unique Authors", unique_authors)
    
    with col4:
        avg_approval_time = filtered_df[filtered_df['approval_time_days'].notna()]['approval_time_days'].mean()
        st.metric("⏱️ Avg Approval Time", f"{avg_approval_time:.1f} days" if not pd.isna(avg_approval_time) else "N/A")
    
    # Live activity feed
    st.subheader("🕒 Live Activity Feed")
    
    # Show recent proposals
    recent_proposals = filtered_df.sort_values('created_at', ascending=False).head(5)
    for _, proposal in recent_proposals.iterrows():
        with st.expander(f"📄 {proposal['title'][:50]}... - {proposal['author']}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Status:** {proposal['category']}")
            with col2:
                st.write(f"**Repository:** {proposal['repository']}")
            with col3:
                st.write(f"**Created:** {proposal['created_at'].strftime('%Y-%m-%d')}")
            
            if proposal['approval_time_days'] and not pd.isna(proposal['approval_time_days']):
                st.write(f"**Approval Time:** {proposal['approval_time_days']:.1f} days")
    
    # Show warning if no data
    if filtered_df.empty:
        st.warning("No proposals found. Please check your data or filters.")
        return
    
    # Charts section
    st.header("📊 Grant Analysis Dashboard")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "Overview", "Repository Analysis", "Author Analysis", 
        "Curator Analysis", "Performance Trends", "AI Evaluation", 
        "AI Milestone Analysis", "Detailed Data", "Grant Programs"
    ])
    
    with tab1:
        show_overview_charts(filtered_df, metrics)
    
    with tab2:
        show_repository_analysis(filtered_df)
    
    with tab3:
        show_author_analysis(filtered_df)
    
    with tab4:
        show_curator_analysis(filtered_df)
    
    with tab5:
        show_performance_trends(filtered_df)
    
    with tab6:
        show_ai_evaluation(filtered_df)
    
    with tab7:
        show_ai_milestone_analysis(filtered_df)
    
    with tab8:
        show_detailed_data(filtered_df)
    
    with tab9:
        show_grant_program_details(filtered_df)

def show_overview_charts(df, metrics):
    """Show overview charts and metrics"""
    
    # Category distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Proposal Categories")
        category_counts = df['category'].value_counts()
        fig = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title="Distribution by Category"
        )
        st.plotly_chart(fig, use_container_width=True, key="overview_categories")
    
    with col2:
        st.subheader("Repository Distribution")
        repo_counts = df['repository'].value_counts()
        fig = px.bar(
            x=repo_counts.index,
            y=repo_counts.values,
            title="Proposals by Repository"
        )
        fig.update_layout(xaxis_title="Repository", yaxis_title="Number of Proposals")
        st.plotly_chart(fig, use_container_width=True, key="overview_repositories")
    
    # Program-specific metrics
    if 'program_stats' in metrics and metrics['program_stats']:
        st.subheader("Program-Specific Performance")
        
        program_data = []
        for repo, repo_metrics in metrics['program_stats'].items():
            program_data.append({
                'Program': repo,
                'Total': repo_metrics['total_proposals'],
                'Approved': repo_metrics['approved_proposals'],
                'Rejected': repo_metrics['rejected_proposals'],
                'Pending': repo_metrics['pending_proposals'],
                'Stale': repo_metrics['stale_proposals'],
                'Approval Rate': (repo_metrics['approved_proposals'] / repo_metrics['total_proposals'] * 100) if repo_metrics['total_proposals'] > 0 else 0,
                'Avg Approval Time': repo_metrics['avg_approval_time'],
                'Unique Authors': repo_metrics['total_authors'],
                'Unique Curators': repo_metrics['total_curators']
            })
        
        program_df = pd.DataFrame(program_data)
        
        if not program_df.empty:
            fig = px.bar(
                program_df,
                x='Program',
                y=['Approved', 'Rejected', 'Pending', 'Stale'],
                title="Program Performance Comparison",
                barmode='stack'
            )
            st.plotly_chart(fig, use_container_width=True, key="program_performance")
    
    # Approval time analysis
    st.subheader("⏱️ Approval Time Analysis")
    approval_times = df[df['approval_time_days'].notna()]['approval_time_days']
    
    if len(approval_times) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.histogram(
                x=approval_times,
                nbins=20,
                title="Approval Time Distribution",
                labels={'x': 'Days to Approval', 'y': 'Count'}
            )
            st.plotly_chart(fig, use_container_width=True, key="approval_time_histogram")
        
        with col2:
            # Approval time statistics
            st.metric("Average Approval Time", f"{approval_times.mean():.1f} days")
            st.metric("Median Approval Time", f"{approval_times.median():.1f} days")
            st.metric("Fastest Approval", f"{approval_times.min():.1f} days")
    else:
        st.info("No approval time data available for analysis.")
    
    # Milestone analysis (using milestone column)
    st.subheader("📊 Milestone Analysis")
    milestone_data = df[df['milestone'].notna() & (df['milestone'] != '')]
    
    if len(milestone_data) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            milestone_counts = milestone_data['milestone'].value_counts().head(10)
            fig = px.bar(
                x=milestone_counts.values,
                y=milestone_counts.index,
                orientation='h',
                title="Most Common Milestones"
            )
            st.plotly_chart(fig, use_container_width=True, key="milestone_distribution")
        
        with col2:
            # Milestone statistics
            st.metric("Proposals with Milestones", len(milestone_data))
            st.metric("Unique Milestones", milestone_data['milestone'].nunique())
            st.metric("Milestone Coverage", f"{(len(milestone_data) / len(df) * 100):.1f}%")
    else:
        st.info("No milestone data available for analysis.")
    
    # Performance score analysis
    st.subheader("📈 Performance Score Analysis")
    performance_scores = df[df['performance_score'].notna()]['performance_score']
    
    if len(performance_scores) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.histogram(
                x=performance_scores,
                nbins=20,
                title="Performance Score Distribution",
                labels={'x': 'Performance Score', 'y': 'Count'}
            )
            st.plotly_chart(fig, use_container_width=True, key="performance_score_histogram")
        
        with col2:
            # Performance statistics
            st.metric("Average Performance Score", f"{performance_scores.mean():.1f}")
            st.metric("Top Performance Score", f"{performance_scores.max():.1f}")
            st.metric("High Performers (>15)", len(performance_scores[performance_scores > 15]))
    else:
        st.info("No performance score data available for analysis.")

def show_repository_analysis(df):
    """Show repository-specific analysis"""
    
    st.subheader("Repository Performance")
    
    # Repository selector
    repositories = df['repository'].unique()
    selected_repo = st.selectbox("Select Repository", repositories)
    
    if selected_repo:
        repo_data = df[df['repository'] == selected_repo]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Proposals", len(repo_data))
        
        with col2:
            approved = len(repo_data[repo_data['category'] == 'APPROVED'])
            st.metric("Approved", approved)
        
        with col3:
            approval_rate = (approved / len(repo_data)) * 100 if len(repo_data) > 0 else 0
            st.metric("Approval Rate", f"{approval_rate:.1f}%")
        
        # Repository timeline
        st.subheader("Proposal Timeline")
        timeline_data = repo_data.groupby(repo_data['created_at'].dt.to_period('M')).size().reset_index()
        timeline_data.columns = ['Month', 'Count']
        timeline_data['Month'] = timeline_data['Month'].astype(str)
        
        fig = px.line(
            timeline_data,
            x='Month',
            y='Count',
            title=f"Proposals Over Time - {selected_repo}"
        )
        st.plotly_chart(fig, use_container_width=True, key="repo_timeline")

def show_author_analysis(df):
    """Show author-specific analysis"""
    
    st.subheader("👤 Author Performance")
    
    # Top authors
    top_authors = df['author'].value_counts().head(10)
    
    if len(top_authors) > 0:
        fig = px.bar(
            x=top_authors.values,
            y=top_authors.index,
            orientation='h',
            title="Top 10 Authors by Number of Proposals"
        )
        fig.update_layout(xaxis_title="Number of Proposals", yaxis_title="Author")
        st.plotly_chart(fig, use_container_width=True, key="top_authors")
        
        # Author statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Authors", len(df['author'].unique()))
        
        with col2:
            avg_proposals = len(df) / len(df['author'].unique()) if len(df['author'].unique()) > 0 else 0
            st.metric("Avg Proposals per Author", f"{avg_proposals:.1f}")
        
        with col3:
            most_active = top_authors.index[0] if len(top_authors) > 0 else "N/A"
            st.metric("Most Active Author", most_active)
    else:
        st.info("No author data available for analysis.")
    
    # Author selector for detailed analysis
    authors = df['author'].unique()
    selected_author = st.selectbox("Select Author for Detailed Analysis", authors)
    
    if selected_author:
        author_data = df[df['author'] == selected_author]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Proposals", len(author_data))
        
        with col2:
            approved = len(author_data[author_data['category'] == 'APPROVED'])
            st.metric("Approved", approved)
        
        with col3:
            approval_rate = (approved / len(author_data)) * 100 if len(author_data) > 0 else 0
            st.metric("Success Rate", f"{approval_rate:.1f}%")
        
        # Show author's proposals
        st.subheader(f"Proposals by {selected_author}")
        author_proposals = author_data[['title', 'repository', 'category', 'created_at']].copy()
        author_proposals['created_at'] = author_proposals['created_at'].dt.strftime('%Y-%m-%d')
        st.dataframe(author_proposals, use_container_width=True)

def show_performance_trends(df):
    """Show performance trends over time"""
    
    st.subheader("Performance Trends")
    
    # Monthly trends
    df_monthly = df.copy()
    df_monthly['month'] = df_monthly['created_at'].dt.to_period('M')
    
    monthly_stats = df_monthly.groupby('month').agg({
        'id': 'count',
        'category': lambda x: (x == 'APPROVED').sum()
    }).reset_index()
    monthly_stats.columns = ['Month', 'Total_Proposals', 'Approved_Proposals']
    monthly_stats['Approval_Rate'] = (monthly_stats['Approved_Proposals'] / monthly_stats['Total_Proposals']) * 100
    monthly_stats['Month'] = monthly_stats['Month'].astype(str)
    
    # Create subplot
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Monthly Proposal Volume', 'Monthly Approval Rate'),
        vertical_spacing=0.1
    )
    
    # Volume chart
    fig.add_trace(
        go.Scatter(x=monthly_stats['Month'], y=monthly_stats['Total_Proposals'], 
                  mode='lines+markers', name='Total Proposals'),
        row=1, col=1
    )
    
    # Approval rate chart
    fig.add_trace(
        go.Scatter(x=monthly_stats['Month'], y=monthly_stats['Approval_Rate'], 
                  mode='lines+markers', name='Approval Rate (%)'),
        row=2, col=1
    )
    
    fig.update_layout(height=600, showlegend=False)
    st.plotly_chart(fig, use_container_width=True, key="performance_trends")
    
    # Category trends
    st.subheader("Category Trends")
    category_trends = df_monthly.groupby(['month', 'category']).size().unstack(fill_value=0)
    category_trends.index = category_trends.index.astype(str)
    
    fig = px.line(
        category_trends,
        title="Category Trends Over Time"
    )
    st.plotly_chart(fig, use_container_width=True, key="category_trends")

def show_ai_evaluation(df):
    """Show AI evaluation of proposals"""
    
    st.subheader("🤖 AI Proposal Evaluation")
    st.markdown("AI-powered analysis of grant proposals using multiple criteria")
    
    if df.empty:
        st.warning("No proposals available for AI evaluation.")
        return
    
    # Proposal selector
    proposals = df[['title', 'author', 'repository', 'category', 'body']].copy()
    proposals['display_title'] = proposals['title'].apply(lambda x: x[:50] + "..." if len(x) > 50 else x)
    
    selected_proposal_idx = st.selectbox(
        "Select a proposal for AI evaluation",
        range(len(proposals)),
        format_func=lambda x: f"{proposals.iloc[x]['display_title']} - {proposals.iloc[x]['author']}"
    )
    
    if selected_proposal_idx is not None:
        selected_proposal = df.iloc[selected_proposal_idx]
        
        # AI evaluation
        ai_evaluator = components['ai_evaluator']
        evaluation = ai_evaluator.analyze_proposal_content(selected_proposal)
        
        # Display evaluation results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Overall Score", f"{evaluation['overall_score']:.2f}/1.00")
        
        with col2:
            st.metric("Risk Level", evaluation['risk_level'])
        
        with col3:
            st.metric("Approval Probability", f"{evaluation['estimated_approval_probability']:.1%}")
        
        # Criteria scores
        st.subheader("Evaluation Criteria")
        criteria_scores = evaluation['criteria_scores']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Radar chart for criteria scores
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=list(criteria_scores.values()),
                theta=list(criteria_scores.keys()),
                fill='toself',
                name='Proposal Score'
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )),
                showlegend=False,
                title="Evaluation Criteria Radar Chart"
            )
            st.plotly_chart(fig, use_container_width=True, key="ai_radar_chart")
        
        with col2:
            # Bar chart for criteria scores
            fig = px.bar(
                x=list(criteria_scores.keys()),
                y=list(criteria_scores.values()),
                title="Criteria Scores",
                labels={'x': 'Criteria', 'y': 'Score'}
            )
            fig.update_layout(yaxis_range=[0, 1])
            st.plotly_chart(fig, use_container_width=True, key="ai_criteria_scores")
        
        # Strengths and weaknesses
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Strengths")
            if evaluation['strengths']:
                for strength in evaluation['strengths']:
                    st.write(f"• {strength}")
            else:
                st.write("No significant strengths identified")
        
        with col2:
            st.subheader("⚠️ Areas for Improvement")
            if evaluation['weaknesses']:
                for weakness in evaluation['weaknesses']:
                    st.write(f"• {weakness}")
            else:
                st.write("No significant weaknesses identified")
        
        # Recommendations
        st.subheader("💡 Recommendations")
        if evaluation['recommendations']:
            for rec in evaluation['recommendations']:
                st.write(f"• {rec}")
        else:
            st.write("No specific recommendations")
        
        # AI Recommendation
        st.subheader("🤖 AI Recommendation")
        if evaluation['estimated_approval_probability'] > 0.6:
            st.success("**APPROVE** - High approval probability")
        elif evaluation['estimated_approval_probability'] < 0.3:
            st.error("**REJECT** - Low approval probability")
        else:
            st.warning("**REVIEW FURTHER** - Requires additional consideration")
        
        # Detailed report
        with st.expander("📋 Detailed AI Curator Report"):
            report = ai_evaluator.generate_curator_report(selected_proposal, evaluation)
            st.markdown(report)
        
        # Proposal details
        with st.expander("📄 Proposal Details"):
            st.write(f"**Title**: {selected_proposal['title']}")
            st.write(f"**Author**: {selected_proposal['author']}")
            st.write(f"**Repository**: {selected_proposal['repository']}")
            st.write(f"**Category**: {selected_proposal['category']}")
            st.write(f"**Milestone**: {selected_proposal.get('milestone', 'Not specified')}")
            st.write(f"**Description**:")
            st.text(selected_proposal['body'][:500] + "..." if len(selected_proposal['body']) > 500 else selected_proposal['body'])

def show_curator_analysis(df):
    """Show curator analysis and performance"""
    
    st.subheader("👥 Curator Analysis")
    st.markdown("Analysis of curators and their review patterns across grant programs")
    
    # Extract all curators from the data with program information
    all_curators = []
    curator_proposals = {}
    curator_programs = {}  # Track which programs each curator works with
    
    for idx, row in df.iterrows():
        curators = row.get('curators', [])
        if isinstance(curators, str):
            try:
                curators = json.loads(curators)
            except:
                curators = []
        
        if isinstance(curators, list):
            for curator in curators:
                all_curators.append(curator)
                if curator not in curator_proposals:
                    curator_proposals[curator] = []
                    curator_programs[curator] = set()
                
                curator_proposals[curator].append({
                    'title': row['title'],
                    'repository': row['repository'],
                    'category': row['category'],
                    'author': row['author'],
                    'created_at': row['created_at'],
                    'approval_time_days': row.get('approval_time_days'),
                    'url': f"https://github.com/{row['repository']}/issues/{row.get('number', '')}"
                })
                curator_programs[curator].add(row['repository'])
    
    if not all_curators:
        st.info("No curator data available. Curators are extracted from comments and reviews.")
        return
    
    # Curator statistics
    curator_counts = pd.Series(all_curators).value_counts()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Curators", len(curator_counts))
    
    with col2:
        st.metric("Total Reviews", len(all_curators))
    
    with col3:
        avg_reviews = len(all_curators) / len(curator_counts) if len(curator_counts) > 0 else 0
        st.metric("Avg Reviews per Curator", f"{avg_reviews:.1f}")
    
    # Program-specific curator analysis
    st.subheader("🎯 Curators by Grant Program")
    
    # Create program-curator matrix
    programs = df['repository'].unique()
    program_curator_data = []
    
    for program in programs:
        program_data = df[df['repository'] == program]
        program_curators = set()
        
        for _, row in program_data.iterrows():
            curators = row.get('curators', [])
            if isinstance(curators, str):
                try:
                    curators = json.loads(curators)
                except:
                    curators = []
            
            if isinstance(curators, list):
                program_curators.update(curators)
        
        program_curator_data.append({
            'Program': program,
            'Total Curators': len(program_curators),
            'Total Proposals': len(program_data),
            'Curators per Proposal': len(program_curators) / len(program_data) if len(program_data) > 0 else 0
        })
    
    program_curator_df = pd.DataFrame(program_curator_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            program_curator_df,
            x='Program',
            y='Total Curators',
            title="Curators per Grant Program",
            color='Total Curators',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            program_curator_df,
            x='Program',
            y='Curators per Proposal',
            title="Average Curators per Proposal",
            color='Curators per Proposal',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Program curator details
    st.subheader("📊 Detailed Program Curator Analysis")
    selected_program = st.selectbox("Select Grant Program", ['All Programs'] + list(programs))
    
    if selected_program != 'All Programs':
        program_data = df[df['repository'] == selected_program]
        program_curators = {}
        
        for _, row in program_data.iterrows():
            curators = row.get('curators', [])
            if isinstance(curators, str):
                try:
                    curators = json.loads(curators)
                except:
                    curators = []
            
            if isinstance(curators, list):
                for curator in curators:
                    if curator not in program_curators:
                        program_curators[curator] = []
                    program_curators[curator].append({
                        'title': row['title'],
                        'category': row['category'],
                        'author': row['author'],
                        'created_at': row['created_at'],
                        'approval_time_days': row.get('approval_time_days')
                    })
        
        if program_curators:
            # Top curators for this program
            curator_counts_program = {k: len(v) for k, v in program_curators.items()}
            top_curators_program = dict(sorted(curator_counts_program.items(), key=lambda x: x[1], reverse=True)[:10])
            
            fig = px.bar(
                x=list(top_curators_program.values()),
                y=list(top_curators_program.keys()),
                orientation='h',
                title=f"Top Curators for {selected_program}"
            )
            fig.update_layout(xaxis_title="Number of Reviews", yaxis_title="Curator")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No curator data available for {selected_program}")
    
    # Top curators across all programs
    st.subheader("🏆 Top Curators Across All Programs")
    top_curators = curator_counts.head(10)
    
    fig = px.bar(
        x=top_curators.values,
        y=top_curators.index,
        orientation='h',
        title="Top 10 Curators by Number of Reviews"
    )
    fig.update_layout(xaxis_title="Number of Reviews", yaxis_title="Curator")
    st.plotly_chart(fig, use_container_width=True)
    
    # Curator selector for detailed analysis
    st.subheader("👤 Individual Curator Analysis")
    curators_list = list(curator_counts.index)
    selected_curator = st.selectbox("Select Curator for Detailed Analysis", curators_list)
    
    if selected_curator:
        curator_data = curator_proposals[selected_curator]
        curator_program_list = list(curator_programs[selected_curator])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Reviews", len(curator_data))
        
        with col2:
            approved = len([p for p in curator_data if p['category'] == 'APPROVED'])
            st.metric("Approved", approved)
        
        with col3:
            approval_rate = (approved / len(curator_data)) * 100 if len(curator_data) > 0 else 0
            st.metric("Approval Rate", f"{approval_rate:.1f}%")
        
        with col4:
            avg_time = np.mean([p['approval_time_days'] for p in curator_data if p['approval_time_days'] is not None])
            st.metric("Avg Approval Time", f"{avg_time:.1f} days" if not np.isnan(avg_time) else "N/A")
        
        # Show curator's programs
        st.write(f"**Programs**: {', '.join(curator_program_list)}")
        
        # Curator approval/rejection statistics
        st.subheader("📊 Curator Decision Statistics")
        
        # Calculate approval/rejection stats
        curator_stats = {}
        for proposal in curator_data:
            category = proposal['category']
            if category not in curator_stats:
                curator_stats[category] = 0
            curator_stats[category] += 1
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            approved_count = curator_stats.get('APPROVED', 0)
            st.metric("Approved", approved_count)
        
        with col2:
            rejected_count = curator_stats.get('REJECTED', 0)
            st.metric("Rejected", rejected_count)
        
        with col3:
            pending_count = curator_stats.get('PENDING', 0)
            st.metric("Pending", pending_count)
        
        with col4:
            stale_count = curator_stats.get('STALE', 0)
            st.metric("Stale", stale_count)
        
        # Approval rate chart
        if curator_stats:
            fig = px.pie(
                values=list(curator_stats.values()),
                names=list(curator_stats.keys()),
                title=f"Decision Distribution - {selected_curator}"
            )
            st.plotly_chart(fig, use_container_width=True, key=f"curator_decisions_{selected_curator}")
        
        # Show curator's reviewed proposals
        st.subheader(f"Proposals Reviewed by {selected_curator}")
        
        # Create clickable links
        curator_df = pd.DataFrame(curator_data)
        if not curator_df.empty:
            curator_df['created_at'] = pd.to_datetime(curator_df['created_at']).dt.strftime('%Y-%m-%d')
            curator_df['approval_time_days'] = curator_df['approval_time_days'].apply(
                lambda x: f"{x:.1f}" if x is not None else "N/A"
            )
            
            # Create clickable links
            curator_df['Link'] = curator_df['url'].apply(
                lambda x: f"[View Proposal]({x})"
            )
            
            # Display with markdown links
            for _, row in curator_df.iterrows():
                with st.expander(f"{row['title']} - {row['repository']}"):
                    st.write(f"**Author**: {row['author']}")
                    st.write(f"**Category**: {row['category']}")
                    st.write(f"**Created**: {row['created_at']}")
                    st.write(f"**Approval Time**: {row['approval_time_days']} days")
                    st.markdown(f"**Link**: {row['Link']}")

def show_ai_milestone_analysis(df):
    """Show AI-powered milestone analysis"""
    
    st.subheader("🤖 AI Milestone Analysis")
    st.markdown("AI-powered analysis of proposal milestones and timelines")
    
    if df.empty:
        st.warning("No proposals available for milestone analysis.")
        return
    
    # Proposal selector
    proposals = df[['title', 'author', 'repository', 'body']].copy()
    proposals['display_title'] = proposals['title'].apply(lambda x: x[:50] + "..." if len(x) > 50 else x)
    
    selected_proposal_idx = st.selectbox(
        "Select a proposal for milestone analysis",
        range(len(proposals)),
        format_func=lambda x: f"{proposals.iloc[x]['display_title']} - {proposals.iloc[x]['author']}"
    )
    
    if selected_proposal_idx is not None:
        selected_proposal = df.iloc[selected_proposal_idx]
        
        # AI evaluation
        ai_evaluator = components['ai_evaluator']
        evaluation = ai_evaluator.analyze_proposal_content(selected_proposal)
        
        # Display milestone-specific analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Milestone Score", f"{evaluation['criteria_scores'].get('milestones', 0):.2f}/1.00")
            
            # Milestone breakdown
            milestones_score = evaluation['criteria_scores'].get('milestones', 0)
            if milestones_score > 0.7:
                st.success("✅ Well-defined milestones")
            elif milestones_score > 0.5:
                st.warning("⚠️ Moderate milestone quality")
            else:
                st.error("❌ Poor milestone definition")
        
        with col2:
            st.metric("Feasibility Score", f"{evaluation['criteria_scores'].get('feasibility', 0):.2f}/1.00")
            
            # Feasibility assessment
            feasibility_score = evaluation['criteria_scores'].get('feasibility', 0)
            if feasibility_score > 0.7:
                st.success("✅ Highly feasible project")
            elif feasibility_score > 0.5:
                st.warning("⚠️ Moderately feasible")
            else:
                st.error("❌ Feasibility concerns")
        
        # Detailed milestone analysis
        st.subheader("📋 Detailed Milestone Analysis")
        
        # Extract milestone information from body
        body = selected_proposal.get('body', '')
        milestones_found = []
        
        # Look for milestone patterns
        milestone_patterns = [
            r'milestone\s*(\d+)',
            r'phase\s*(\d+)',
            r'stage\s*(\d+)',
            r'(\d+)\s*week',
            r'(\d+)\s*month'
        ]
        
        for pattern in milestone_patterns:
            matches = re.findall(pattern, body, re.IGNORECASE)
            milestones_found.extend(matches)
        
        if milestones_found:
            st.write(f"**Milestones Found**: {len(set(milestones_found))}")
            st.write("**Milestone References**: " + ", ".join(set(milestones_found)))
        else:
            st.write("**Milestones Found**: No explicit milestones detected")
        
        # Timeline analysis
        timeline_patterns = [
            r'(\d+)\s*(week|month|day)s?',
            r'timeline',
            r'schedule',
            r'deadline'
        ]
        
        timeline_mentions = []
        for pattern in timeline_patterns:
            if re.search(pattern, body, re.IGNORECASE):
                timeline_mentions.append(pattern)
        
        if timeline_mentions:
            st.write(f"**Timeline References**: {len(timeline_mentions)} found")
        else:
            st.write("**Timeline References**: No timeline information detected")
        
        # Recommendations
        st.subheader("💡 Milestone Recommendations")
        if evaluation['recommendations']:
            for rec in evaluation['recommendations']:
                if 'milestone' in rec.lower() or 'timeline' in rec.lower():
                    st.write(f"• {rec}")
        else:
            st.write("• Define clear, measurable milestones with timelines")
            st.write("• Include specific deliverables for each milestone")
            st.write("• Provide realistic time estimates")
        
        # Show original body
        with st.expander("📄 Original Proposal Description"):
            st.text(body)

def show_grant_program_details(df):
    """Show detailed information about each grant program"""
    
    st.subheader("🏛️ Grant Program Details")
    st.markdown("Comprehensive information about each Polkadot grant program")
    
    # Program selector
    programs = df['repository'].unique()
    selected_program = st.selectbox("Select Grant Program", programs)
    
    if selected_program:
        program_data = df[df['repository'] == selected_program]
        
        # Program overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Proposals", len(program_data))
        
        with col2:
            approved = len(program_data[program_data['category'] == 'APPROVED'])
            st.metric("Approved", approved)
        
        with col3:
            approval_rate = (approved / len(program_data)) * 100 if len(program_data) > 0 else 0
            st.metric("Approval Rate", f"{approval_rate:.1f}%")
        
        with col4:
            unique_authors = program_data['author'].nunique()
            st.metric("Unique Authors", unique_authors)
        
        # Program statistics
        col1, col2 = st.columns(2)
        
        with col1:
            # Category distribution
            category_counts = program_data['category'].value_counts()
            fig = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title=f"Proposal Categories - {selected_program}"
            )
            st.plotly_chart(fig, use_container_width=True, key=f"program_categories_{selected_program}")
        
        with col2:
            # Timeline
            timeline_data = program_data.groupby(program_data['created_at'].dt.to_period('M')).size().reset_index()
            timeline_data.columns = ['Month', 'Count']
            timeline_data['Month'] = timeline_data['Month'].astype(str)
            
            fig = px.line(
                timeline_data,
                x='Month',
                y='Count',
                title=f"Proposals Over Time - {selected_program}"
            )
            st.plotly_chart(fig, use_container_width=True, key=f"program_timeline_{selected_program}")
        
        # Program-specific metrics
        st.subheader("📊 Program-Specific Metrics")
        
        # Approval time analysis
        approval_times = pd.to_numeric(program_data['approval_time_days'], errors='coerce')
        approval_times = approval_times[approval_times.notna()]
        
        if len(approval_times) > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Avg Approval Time", f"{approval_times.mean():.1f} days")
            
            with col2:
                st.metric("Median Approval Time", f"{approval_times.median():.1f} days")
            
            with col3:
                st.metric("Fastest Approval", f"{approval_times.min():.1f} days")
            
            # Approval time distribution
            fig = px.histogram(
                x=approval_times,
                nbins=20,
                title=f"Approval Time Distribution - {selected_program}",
                labels={'x': 'Days to Approval', 'y': 'Count'}
            )
            st.plotly_chart(fig, use_container_width=True, key=f"program_approval_times_{selected_program}")
        
        # Bounty analysis (removed since bounty_amount not available in new structure)
        # Note: Bounty amount data is not available in the current data structure
        
        # Top authors for this program
        st.subheader("👤 Top Authors")
        top_authors = program_data['author'].value_counts().head(10)
        
        fig = px.bar(
            x=top_authors.values,
            y=top_authors.index,
            orientation='h',
            title=f"Top Authors - {selected_program}"
        )
        fig.update_layout(xaxis_title="Number of Proposals", yaxis_title="Author")
        st.plotly_chart(fig, use_container_width=True, key=f"program_top_authors_{selected_program}")
        
        # Program curator analysis
        st.subheader("👥 Program Curators")
        
        program_curators = {}
        for _, row in program_data.iterrows():
            curators = row.get('curators', [])
            if isinstance(curators, str):
                try:
                    curators = json.loads(curators)
                except:
                    curators = []
            
            if isinstance(curators, list):
                for curator in curators:
                    if curator not in program_curators:
                        program_curators[curator] = []
                    program_curators[curator].append({
                        'title': row['title'],
                        'category': row['category'],
                        'author': row['author'],
                        'created_at': row['created_at']
                    })
        
        if program_curators:
            curator_counts = {k: len(v) for k, v in program_curators.items()}
            top_curators = dict(sorted(curator_counts.items(), key=lambda x: x[1], reverse=True)[:10])
            
            fig = px.bar(
                x=list(top_curators.values()),
                y=list(top_curators.keys()),
                orientation='h',
                title=f"Top Curators - {selected_program}"
            )
            fig.update_layout(xaxis_title="Number of Reviews", yaxis_title="Curator")
            st.plotly_chart(fig, use_container_width=True, key=f"program_top_curators_{selected_program}")
            
            # Curator decision statistics for this program
            st.subheader("📊 Curator Decision Statistics for This Program")
            
            # Calculate program-specific curator stats
            program_curator_stats = {}
            for curator, proposals in program_curators.items():
                curator_approved = len([p for p in proposals if p['category'] == 'APPROVED'])
                curator_rejected = len([p for p in proposals if p['category'] == 'REJECTED'])
                curator_pending = len([p for p in proposals if p['category'] == 'PENDING'])
                curator_stale = len([p for p in proposals if p['category'] == 'STALE'])
                
                program_curator_stats[curator] = {
                    'Approved': curator_approved,
                    'Rejected': curator_rejected,
                    'Pending': curator_pending,
                    'Stale': curator_stale,
                    'Total': len(proposals)
                }
            
            # Show top curators with their decision breakdown
            if program_curator_stats:
                curator_breakdown_data = []
                for curator, stats in list(program_curator_stats.items())[:10]:  # Top 10
                    curator_breakdown_data.append({
                        'Curator': curator,
                        'Approved': stats['Approved'],
                        'Rejected': stats['Rejected'],
                        'Pending': stats['Pending'],
                        'Stale': stats['Stale'],
                        'Total': stats['Total']
                    })
                
                breakdown_df = pd.DataFrame(curator_breakdown_data)
                st.dataframe(breakdown_df, use_container_width=True)
        else:
            st.info(f"No curator data available for {selected_program}")
        
        # Recent proposals
        st.subheader("📋 Recent Proposals")
        recent_proposals = program_data.sort_values('created_at', ascending=False).head(10)
        
        for _, proposal in recent_proposals.iterrows():
            with st.expander(f"{proposal['title']} - {proposal['author']}"):
                st.write(f"**Category**: {proposal['category']}")
                st.write(f"**Created**: {proposal['created_at'].strftime('%Y-%m-%d')}")
                st.write(f"**Approval Time**: {proposal['approval_time_days']:.1f} days" if proposal['approval_time_days'] else "**Approval Time**: N/A")
                
                # Show curators
                curators = proposal.get('curators', [])
                if isinstance(curators, str):
                    try:
                        curators = json.loads(curators)
                    except:
                        curators = []
                
                if curators:
                    st.write(f"**Curators**: {', '.join(curators)}")
                else:
                    st.write("**Curators**: None")

def show_detailed_data(df):
    """Show detailed data table with filters"""
    
    st.subheader("Detailed Proposal Data")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ['All'] + list(df['category'].unique())
        selected_category = st.selectbox("Filter by Category", categories)
    
    with col2:
        repositories = ['All'] + list(df['repository'].unique())
        selected_repo = st.selectbox("Filter by Repository", repositories)
    
    with col3:
        date_range = st.date_input(
            "Filter by Date Range",
            value=(df['created_at'].min().date(), df['created_at'].max().date()),
            min_value=df['created_at'].min().date(),
            max_value=df['created_at'].max().date()
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    if selected_repo != 'All':
        filtered_df = filtered_df[filtered_df['repository'] == selected_repo]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['created_at'].dt.date >= start_date) &
            (filtered_df['created_at'].dt.date <= end_date)
        ]
    
    # Display filtered data
    st.write(f"Showing {len(filtered_df)} proposals")
    
    # Debug: Show available columns
    if st.checkbox("🔍 Show Debug Information"):
        st.write("**Available columns:**", list(filtered_df.columns))
        st.write("**Data types:**", filtered_df.dtypes.to_dict())
        st.write("**Sample data:**")
        st.write(filtered_df.head(3))
    
    # Prepare data for display with all relevant columns
    display_columns = [
        'title', 'author', 'repository', 'category', 'created_at', 
        'approval_time_days', 'curators', 'comments_count', 'review_comments_count',
        'commits_count', 'additions_count', 'deletions_count', 'changed_files_count',
        'performance_score', 'is_stale', 'state'
    ]
    
    # Only include columns that exist in the dataframe
    available_columns = [col for col in display_columns if col in filtered_df.columns]
    display_df = filtered_df[available_columns].copy()
    
    # Format date columns
    if 'created_at' in display_df.columns:
        display_df['created_at'] = display_df['created_at'].dt.strftime('%Y-%m-%d')
    
    # Handle approval_time_days safely
    if 'approval_time_days' in display_df.columns:
        display_df['approval_time_days'] = pd.to_numeric(display_df['approval_time_days'], errors='coerce').round(1)
        display_df['approval_time_days'] = display_df['approval_time_days'].apply(
            lambda x: f"{x:.1f}" if pd.notna(x) else "N/A"
        )
    
    # Format curators column
    if 'curators' in display_df.columns:
        display_df['curators'] = display_df['curators'].apply(
            lambda x: ', '.join(x) if isinstance(x, list) and x else 'None'
        )
    
    # Format performance score
    if 'performance_score' in display_df.columns:
        display_df['performance_score'] = display_df['performance_score'].apply(
            lambda x: f"{x:.1f}" if pd.notna(x) else "N/A"
        )
    
    # Format boolean columns
    if 'is_stale' in display_df.columns:
        display_df['is_stale'] = display_df['is_stale'].apply(lambda x: "Yes" if x else "No")
    
    # Add GitHub links
    if 'number' in filtered_df.columns:
        display_df['GitHub Link'] = filtered_df['number'].apply(
            lambda x: f"https://github.com/{filtered_df.iloc[0]['repository']}/issues/{x}" if pd.notna(x) else ""
        )
    
    st.dataframe(display_df, use_container_width=True)
    
    # Show data summary
    st.subheader("📊 Data Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Proposals", len(filtered_df))
    
    with col2:
        approved = len(filtered_df[filtered_df['category'] == 'APPROVED'])
        st.metric("Approved", approved)
    
    with col3:
        rejected = len(filtered_df[filtered_df['category'] == 'REJECTED'])
        st.metric("Rejected", rejected)
    
    with col4:
        pending = len(filtered_df[filtered_df['category'] == 'PENDING'])
        st.metric("Pending", pending)
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name=f"polkadot_grants_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main() 