import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from models import Studiengang
from data import create_sample_data
import json
import os


# Color scheme from CLAUDE.md
COLORS = {
    'primary': '#F67280',
    'secondary': '#C06C84', 
    'third': '#6C5B7B',
    'fourth': '#355C7D'
}

# Accessible colors for light/dark modes with improved contrast
ACCESSIBLE_COLORS = {
    'light': {
        'bg': '#FFFFFF',
        'text': '#212529',          # Darker gray for better readability
        'success': '#155724',       # Darker green for better contrast
        'warning': '#856404',       # Dark gold instead of yellow
        'danger': '#721c24',        # Darker red for better contrast
        'info': '#0c5460',          # Dark teal for better contrast
        'muted': '#6c757d',         # For secondary text
        'border': '#dee2e6',        # Light borders
        'shadow': 'rgba(0,0,0,0.15)' # Stronger shadow for light mode
    },
    'dark': {
        'bg': '#1E1E1E',
        'text': '#FFFFFF', 
        'success': '#4CAF50',
        'warning': '#FF9800',
        'danger': '#F44336',
        'info': '#2196F3',
        'muted': '#adb5bd',         # For secondary text
        'border': '#495057',        # Dark borders
        'shadow': 'rgba(0,0,0,0.3)' # Stronger shadow for dark mode
    }
}


def init_session_state():
    """Initialize session state variables."""
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    if 'studiengang' not in st.session_state:
        # Try to load from file, otherwise create sample data
        if os.path.exists('student_data.json'):
            st.session_state.studiengang = Studiengang.load_from_file('student_data.json')
        else:
            st.session_state.studiengang = create_sample_data()


def toggle_theme():
    """Toggle between light and dark theme."""
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'


def create_progress_bar(value: float, max_value: float, label: str) -> go.Figure:
    """Create a horizontal progress bar using Plotly with proper theming."""
    percentage = (value / max_value) * 100 if max_value > 0 else 0
    remaining = max_value - value
    
    # Get current theme colors
    theme = st.session_state.get('theme', 'light')
    colors = ACCESSIBLE_COLORS[theme]
    
    fig = go.Figure()
    
    # Create a stacked bar chart for better visual representation
    fig.add_trace(go.Bar(
        x=[value],
        y=[label],
        orientation='h',
        marker=dict(
            color=COLORS['primary'],
            line=dict(color=colors['border'], width=1)
        ),
        name='Completed',
        showlegend=False,
        text=f'{value}/{max_value} ECTS ({percentage:.0f}%)',
        textposition='inside',
        textfont=dict(color='white', size=12, family='Arial Black'),
        hovertemplate=f'Completed: {value} ECTS<br>Percentage: {percentage:.1f}%<extra></extra>'
    ))
    
    # Add remaining portion
    if remaining > 0:
        fig.add_trace(go.Bar(
            x=[remaining],
            y=[label],
            orientation='h',
            marker=dict(
                color=colors['border'],
                line=dict(color=colors['border'], width=1),
                pattern=dict(shape="/", bgcolor=colors['bg'], fgcolor=colors['muted'])
            ),
            name='Remaining',
            showlegend=False,
            text=f'{remaining} ECTS',
            textposition='inside',
            textfont=dict(color=colors['muted'], size=10),
            hovertemplate=f'Remaining: {remaining} ECTS<extra></extra>'
        ))
    
    fig.update_layout(
        barmode='stack',  # Stack bars instead of overlay
        height=50,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(
            showgrid=False, 
            showticklabels=False, 
            zeroline=False,
            range=[0, max_value],  # Ensure full range is visible
            fixedrange=True
        ),
        yaxis=dict(
            showgrid=False, 
            showticklabels=False,
            fixedrange=True
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text']),
        hoverlabel=dict(
            bgcolor=colors['bg'],
            bordercolor=colors['border'],
            font_color=colors['text']
        )
    )
    
    return fig


def show_semester_overview(studiengang: Studiengang):
    """Display semester overview section."""
    st.subheader("📚 Semesterübersicht")
    
    cols = st.columns(len(studiengang.semester))
    
    for i, semester in enumerate(studiengang.semester):
        with cols[i % len(cols)]:
            status_icon = "✅" if semester.ist_abgeschlossen() else "⏳" if semester == studiengang.get_aktuelles_semester() else "📅"
            
            ects_erreicht = semester.berechne_ects()
            durchschnitt = semester.get_durchschnittsnote()
            note_display = f"{durchschnitt:.1f}" if durchschnitt is not None else "N/A"
            
            st.markdown(f"""
            **{status_icon} Semester {semester.nummer}**  
            ECTS: {ects_erreicht}/{semester.geplante_ects}  
            Ø Note: {note_display}
            """)


def show_current_modules(studiengang: Studiengang):
    """Display current semester modules."""
    aktuelles_semester = studiengang.get_aktuelles_semester()
    
    if aktuelles_semester:
        st.subheader(f"📝 Aktuelle Module (Semester {aktuelles_semester.nummer})")
        
        for modul in aktuelles_semester.module:
            cols = st.columns([3, 1, 1, 1])
            
            with cols[0]:
                st.write(f"• {modul.name}")
            
            with cols[1]:
                st.write(f"[{modul.ects} ECTS]")
            
            with cols[2]:
                if modul.ist_bestanden():
                    st.write("✅")
                elif modul.pruefungsleistung is None:
                    st.write("⏳ laufend" if "Algorithmen" in modul.name else "📝 angemeldet")
                else:
                    st.write("❌")
            
            with cols[3]:
                note = modul.get_note()
                if note:
                    st.write(f"{note:.1f}")
                else:
                    st.write("-")


def show_grade_analysis(studiengang: Studiengang):
    """Display grade analysis section."""
    st.subheader("📊 Notenschnitt")
    
    current_avg = studiengang.berechne_notenschnitt()
    target_grade = 2.0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Aktuell", f"{current_avg:.1f}")
    
    with col2:
        st.metric("Ziel", f"{target_grade:.1f}")
    
    with col3:
        difference = current_avg - target_grade
        status = "⚠️" if difference > 0 else "✅"
        st.metric("Status", f"{status} {difference:+.1f}")


def show_alerts(studiengang: Studiengang):
    """Display alert messages."""
    aktuelles_semester = studiengang.get_aktuelles_semester()
    current_avg = studiengang.berechne_notenschnitt()
    
    alerts = []
    
    # Grade warning
    if current_avg > 2.0:
        alerts.append(("⚠️", "warning", f"Notenschnitt über Ziel - Fokus auf gute Noten!"))
    
    # Missing ECTS warning
    if aktuelles_semester:
        missing_ects = aktuelles_semester.geplante_ects - aktuelles_semester.berechne_ects()
        if missing_ects > 0:
            alerts.append(("⚠️", "warning", f"{missing_ects} ECTS fehlen in Semester {aktuelles_semester.nummer}"))
    
    for icon, level, message in alerts:
        if level == "warning":
            st.warning(f"{icon} {message}")
        elif level == "info":
            st.info(f"{icon} {message}")


def show_main_dashboard():
    """Display the main dashboard."""
    studiengang = st.session_state.studiengang
    
    # Header with theme toggle
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title("🎓 STUDIUM DASHBOARD")
    
    with col2:
        if st.button("🌙/☀️ Theme"):
            toggle_theme()
            st.rerun()
    
    # Main progress section
    st.subheader("📈 Gesamtfortschritt")
    
    erreichte_ects = studiengang.get_erreichte_ects()
    gesamt_ects = studiengang.ects_gesamt
    fortschritt_prozent = studiengang.berechne_gesamtfortschritt()
    
    # Progress bar
    fig = create_progress_bar(erreichte_ects, gesamt_ects, "ECTS")
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Accessible progress information
    st.markdown(f"""
    <div role="progressbar" aria-valuenow="{erreichte_ects}" aria-valuemin="0" aria-valuemax="{gesamt_ects}" aria-label="Study Progress">
        <span class="sr-only">Study progress: {erreichte_ects} out of {gesamt_ects} ECTS completed, {fortschritt_prozent:.0f} percent</span>
        <strong>{fortschritt_prozent:.0f}% ({erreichte_ects}/{gesamt_ects} ECTS)</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Current semester info
    aktuelles_semester = studiengang.get_aktuelles_semester()
    if aktuelles_semester:
        st.markdown(f"**Aktuelles Semester: {aktuelles_semester.nummer} von {len(studiengang.semester)}**")
    
    st.divider()
    
    # Two column layout for main content
    col1, col2 = st.columns(2)
    
    with col1:
        show_grade_analysis(studiengang)
        st.divider()
        show_semester_overview(studiengang)
    
    with col2:
        show_current_modules(studiengang)
    
    st.divider()
    
    # Alerts at the bottom
    show_alerts(studiengang)


def apply_theme():
    """Apply the selected theme with accessibility improvements."""
    theme = st.session_state.theme
    colors = ACCESSIBLE_COLORS[theme]
    
    # Enhanced CSS for accessibility and visual improvements
    st.markdown(f"""
    <style>
    /* Main app styling with theme-aware colors */
    .stApp {{
        background-color: {colors['bg']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Override Streamlit's default text colors */
    .stMarkdown, .stText, p, div, span {{
        color: {colors['text']} !important;
    }}
    
    /* Ensure headings are visible */
    h1, h2, h3, h4, h5, h6 {{
        color: {colors['text']} !important;
        font-weight: 700;
    }}
    
    /* Button styling with high contrast */
    .stButton > button {{
        background-color: {COLORS['fourth']} !important;
        color: white !important;
        border: 2px solid {COLORS['fourth']} !important;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        background-color: {COLORS['third']} !important;
        border-color: {COLORS['third']} !important;
        transform: translateY(-1px);
    }}
    
    /* Focus indicators for keyboard navigation */
    .stButton > button:focus {{
        outline: 3px solid {colors['info']} !important;
        outline-offset: 2px;
    }}
    
    /* Metric styling with theme-aware colors */
    .stMetric {{
        background-color: {colors['bg']};
        border: 1px solid {colors['border']};
        border-radius: 8px;
        padding: 12px;
        box-shadow: 0 2px 4px {colors['shadow']};
    }}
    
    .stMetric > div {{
        color: {colors['text']} !important;
    }}
    
    .stMetric label {{
        color: {colors['muted']} !important;
        font-size: 0.875rem;
    }}
    
    .stMetric [data-testid="metric-value"] {{
        color: {colors['text']} !important;
        font-size: 1.5rem;
        font-weight: 600;
    }}
    
    /* Progress bar with theme-aware styling */
    .progress-container {{
        background-color: {colors['border']};
        border-radius: 10px;
        height: 30px;
        margin: 10px 0;
        position: relative;
        overflow: hidden;
    }}
    
    .progress-bar {{
        background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['secondary']});
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }}
    
    /* Alert styling with proper contrast */
    .stAlert {{
        border-radius: 8px;
        border: 1px solid {colors['border']};
    }}
    
    .stAlert[data-baseweb="notification"] {{
        background-color: {colors['bg']};
        color: {colors['text']};
    }}
    
    /* Warning alerts */
    .stWarning {{
        background-color: {'#fff3cd' if theme == 'light' else '#664d03'} !important;
        color: {colors['warning']} !important;
        border-color: {colors['warning']} !important;
    }}
    
    /* Success alerts */
    .stSuccess {{
        background-color: {'#d1edcc' if theme == 'light' else '#0f5132'} !important;
        color: {colors['success']} !important;
        border-color: {colors['success']} !important;
    }}
    
    /* Info alerts */
    .stInfo {{
        background-color: {'#d1ecf1' if theme == 'light' else '#055160'} !important;
        color: {colors['info']} !important;
        border-color: {colors['info']} !important;
    }}
    
    /* Module status indicators with better visibility */
    .status-completed {{
        color: {colors['success']} !important;
        font-size: 1.2em;
        font-weight: bold;
    }}
    
    .status-in-progress {{
        color: {colors['warning']} !important;
        font-size: 1.2em;
        font-weight: bold;
    }}
    
    .status-registered {{
        color: {colors['info']} !important;
        font-size: 1.2em;
        font-weight: bold;
    }}
    
    /* Divider styling */
    .stDivider > div {{
        border-color: {colors['border']} !important;
    }}
    
    /* Sidebar styling if used */
    .css-1d391kg {{
        background-color: {colors['bg']};
        color: {colors['text']};
    }}
    
    /* DataFrame styling */
    .stDataFrame {{
        color: {colors['text']};
    }}
    
    /* Plotly chart background */
    .js-plotly-plot .plotly .modebar {{
        background-color: {colors['bg']};
    }}
    
    /* Ensure all text elements are visible */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {colors['bg']};
    }}
    
    .stTabs [data-baseweb="tab"] {{
        color: {colors['text']};
    }}
    
    /* Screen reader only text */
    .sr-only {{
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0,0,0,0);
        white-space: nowrap;
        border: 0;
    }}
    
    /* Ensure proper text contrast for all elements */
    * {{
        color: inherit;
    }}
    </style>
    """, unsafe_allow_html=True)


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Student Dashboard - Goal Tracking",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Add accessibility meta tags
    st.markdown("""
    <meta name="description" content="Student Goal Dashboard for tracking study progress, ECTS credits, and academic performance">
    <meta name="keywords" content="student, dashboard, ECTS, study progress, academic tracking">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    """, unsafe_allow_html=True)
    
    init_session_state()
    apply_theme()
    show_main_dashboard()


if __name__ == "__main__":
    main()