import os
import streamlit as st
import tempfile
import pandas as pd
import sys
from pathlib import Path
import re

# Disable AgentOps telemetry at the environment level
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

# Monkey patch AgentOps to completely disable it
try:
    import agentops
    # Create a dummy session object that does nothing
    class DummySession:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    
    # Replace the init function with one that returns our dummy session
    def dummy_init(*args, **kwargs):
        return DummySession()
    
    # Apply the monkey patch
    agentops.init = dummy_init
    print("AgentOps successfully patched to disable telemetry")
except ImportError:
    print("AgentOps not found, no need to patch")

# Remove CrewAI's AgentOps event listeners
try:
    from crewai.utilities.events import crewai_event_bus
    from crewai.utilities.events.third_party.agentops_listener import AgentOpsListener
    
    # Find and remove any AgentOps listeners
    for event_type, handlers in list(crewai_event_bus._event_handlers.items()):
        for handler in list(handlers):
            if isinstance(handler, AgentOpsListener) or "agentops" in str(handler).lower():
                crewai_event_bus._event_handlers[event_type].remove(handler)
                print(f"Removed AgentOps listener from {event_type} events")
    
    print("Successfully disabled CrewAI's AgentOps integration")
except Exception as e:
    print(f"Note: Could not disable CrewAI event listeners: {str(e)}")

# Alternative approach to fix import path issues
current_file = Path(__file__).resolve()

# Try different path configurations
# Option 1: Add the conference directory to path
conference_dir = current_file.parent.parent.parent
sys.path.append(str(conference_dir))

# Import the flow components - try different import formats

    # Try direct import first
from conference.main import AttendeeFlow
from conference.crews.pharma_crew.pharma_crew import PharmaCrew

def strip_ansi_codes(text):
    """Remove ANSI escape sequences from text"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

st.set_page_config(
    page_title="Conference Agent",
    page_icon="👥",
    layout="wide"
)

st.title("Conference Attendee Analyzer")
st.markdown("""
This application analyzes conference attendee data to extract insights.
Upload your attendee report (CSV or Excel) to get started.
""")

# File upload section
st.header("1. Upload Attendee Data")
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx", "xls"])

# Parameters section
st.header("2. Analysis Parameters")
col1, col2 = st.columns(2)

with col1:
    batch_size = st.slider("Batch Size", min_value=1, max_value=10, value=3, 
                        help="Number of attendees to analyze in each batch (also determines number of concurrent batches)")

with col2:
    max_concurrent_searches = st.slider("Concurrent Web Searches per Batch", min_value=1, max_value=10, value=5,
                                   help="Maximum number of web searches to run concurrently within each batch")

# Set up processing mode
st.subheader("Processing Settings")
col1, col2 = st.columns(2)

with col1:
    use_async_processing = st.checkbox("Use Asynchronous Processing", value=True,
                                   help="Process attendees asynchronously within each batch for faster results")

with col2:
    verbose_logging = st.checkbox("Verbose Logging", value=True,
                          help="Display detailed search results in the logs")

run_pharma_analysis = st.checkbox("Run Pharmaceutical Industry Analysis", value=True,
                               help="Analyze attendees for pharmaceutical industry connections")

# Process the data
if uploaded_file is not None:
    # Create a temporary file to store the upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_file_path = tmp_file.name
    
    # Display a spinner while processing
    if st.button("Run Analysis"):
        st.subheader("3. Analysis Results")
        
        with st.spinner("Processing attendee data..."):
            # Create the flow
            flow = AttendeeFlow()
            flow.state.csv_file_path = temp_file_path
            flow.state.output_json_path = None  # No need to save to file
            
            # Run the flow
            with st.expander("Processing Log", expanded=True):
                log_placeholder = st.empty()
                import io
                from contextlib import redirect_stdout
                
                f = io.StringIO()
                with redirect_stdout(f):
                    result = flow.kickoff()
                
                # Strip ANSI codes before displaying
                clean_log = strip_ansi_codes(f.getvalue())
                log_placeholder.text(clean_log)
            
            # Display basic analysis results
            if flow.state.processed:
                st.success(f"Successfully processed {len(flow.state.attendees)} attendees")
                
                # Display organization analysis
                st.subheader("Organization Analysis")
                if flow.state.attendees:
                    # Count attendees by organization
                    org_counts = {}
                    for attendee in flow.state.attendees:
                        org = attendee.get('organization', 'Unknown')
                        if org in org_counts:
                            org_counts[org] += 1
                        else:
                            org_counts[org] = 1
                    
                    # Convert to DataFrame for display
                    org_df = pd.DataFrame({"Organization": org_counts.keys(), "Attendees": org_counts.values()})
                    org_df = org_df.sort_values("Attendees", ascending=False).reset_index(drop=True)
                    
                    # Display as chart and table
                    st.bar_chart(org_df.set_index("Organization")["Attendees"])
                    st.dataframe(org_df)
                
                # Run pharma analysis if requested
                if run_pharma_analysis:
                    st.subheader("Pharmaceutical Industry Analysis")
                    
                    # Always analyze all attendees
                    analyze_attendees = flow.state.attendees
                    
                    with st.spinner(f"Analyzing {len(analyze_attendees)} attendees for pharmaceutical connections..."):
                        pharma_crew = PharmaCrew(
                            attendees=analyze_attendees,
                            output_file=None,  # No need to save
                            batch_size=batch_size,
                            max_workers=batch_size,
                            max_concurrent_searches=max_concurrent_searches,
                            use_async_processing=use_async_processing,
                            verbose=verbose_logging
                        )
                        
                        # Capture the output
                        f = io.StringIO()
                        with redirect_stdout(f):
                            pharma_results = pharma_crew.analyze(skip_csv_export=True)
                        
                        # Strip ANSI codes before displaying
                        clean_log = strip_ansi_codes(f.getvalue())
                        with st.expander("Pharmaceutical Analysis Log", expanded=False):
                            st.text(clean_log)
                        
                        # Display results in a table
                        if pharma_results:
                            st.success(f"Analysis completed for {len(pharma_results)} attendees")
                            pharma_df = pd.DataFrame(pharma_results)
                            st.dataframe(pharma_df)
                            
                            # Show additional insights if available
                            if 'industry_sector' in pharma_df.columns:
                                st.subheader("Industry Sector Distribution")
                                sector_counts = pharma_df['industry_sector'].value_counts()
                                st.bar_chart(sector_counts)
            else:
                st.error("Failed to process the attendee data. Please check the processing log for details.")
    
    # Clean up the temporary file
    import os
    os.unlink(temp_file_path) 