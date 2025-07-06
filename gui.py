import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from models import Studiengang, Modul, Pruefungsleistung
from data import create_sample_data
import json
import os
from datetime import date


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


def validate_module_input(name: str, ects: int) -> tuple[bool, str]:
    """Validate module input and return (is_valid, error_message)."""
    if not name or not name.strip():
        return False, "Module name cannot be empty."
    
    if len(name.strip()) < 2:
        return False, "Module name must be at least 2 characters long."
    
    if len(name.strip()) > 100:
        return False, "Module name must be less than 100 characters."
    
    if ects < 1 or ects > 30:
        return False, "ECTS must be between 1 and 30."
    
    return True, ""


def validate_grade_input(grade: float) -> tuple[bool, str]:
    """Validate grade input and return (is_valid, error_message)."""
    if grade < 1.0 or grade > 5.0:
        return False, "Grade must be between 1.0 and 5.0."
    
    # Check if grade is in reasonable increments (0.1 steps)
    if round(grade * 10) != grade * 10:
        return False, "Grade must be in 0.1 increments (e.g., 1.0, 1.3, 2.7)."
    
    return True, ""


def check_duplicate_module(studiengang: Studiengang, module_name: str, exclude_module=None) -> bool:
    """Check if a module with the same name already exists in current semester."""
    aktuelles_semester = studiengang.get_aktuelles_semester()
    if not aktuelles_semester:
        return False
    
    for modul in aktuelles_semester.module:
        if modul != exclude_module and modul.name.lower().strip() == module_name.lower().strip():
            return True
    return False


def save_data():
    """Save current study data to JSON file."""
    try:
        st.session_state.studiengang.save_to_file('student_data.json')
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False


def show_add_module_form(studiengang: Studiengang):
    """Display form for adding new modules to current semester."""
    aktuelles_semester = studiengang.get_aktuelles_semester()
    
    if not aktuelles_semester:
        st.warning("⚠️ No current semester available to add modules to.")
        return
    
    with st.expander("➕ Add New Module", expanded=False):
        st.markdown(f"**Adding to Semester {aktuelles_semester.nummer}**")
        
        with st.form("add_module_form"):
            # Module details
            module_name = st.text_input("Module Name", placeholder="e.g., Web Development")
            ects = st.number_input("ECTS Credits", min_value=1, max_value=30, value=6, step=1)
            
            # Optional grade information
            st.markdown("**Optional: Add Grade Information**")
            has_grade = st.checkbox("This module is already completed with a grade")
            
            grade = None
            exam_date = None
            if has_grade:
                grade = st.number_input("Grade", min_value=1.0, max_value=5.0, value=2.0, step=0.1, 
                                      help="German grading system: 1.0 (best) to 5.0 (worst)")
                exam_date = st.date_input("Exam Date", value=date.today())
            
            # Submit button
            submitted = st.form_submit_button("Add Module", type="primary")
            
            if submitted:
                # Validate module input
                is_valid, error_msg = validate_module_input(module_name, ects)
                if not is_valid:
                    st.error(f"❌ {error_msg}")
                    return
                
                # Check for duplicates
                if check_duplicate_module(studiengang, module_name):
                    st.error(f"❌ A module named '{module_name}' already exists in this semester.")
                    return
                
                # Validate grade if provided
                if has_grade and grade is not None:
                    grade_valid, grade_error = validate_grade_input(grade)
                    if not grade_valid:
                        st.error(f"❌ {grade_error}")
                        return
                
                # Create new module
                try:
                    if has_grade and grade is not None:
                        pruefungsleistung = Pruefungsleistung(grade, exam_date, "bestanden")
                        new_module = Modul(module_name.strip(), ects, pruefungsleistung)
                    else:
                        new_module = Modul(module_name.strip(), ects)
                    
                    # Add to current semester
                    aktuelles_semester.add_modul(new_module)
                    
                    # Save data
                    if save_data():
                        st.success(f"✅ Module '{module_name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to save data.")
                        
                except Exception as e:
                    st.error(f"❌ Error creating module: {e}")


def show_grade_recording_form(studiengang: Studiengang):
    """Display form for adding grades to existing modules."""
    aktuelles_semester = studiengang.get_aktuelles_semester()
    
    if not aktuelles_semester:
        return
    
    # Find modules without grades
    modules_without_grades = [m for m in aktuelles_semester.module if m.pruefungsleistung is None]
    
    if not modules_without_grades:
        return
    
    with st.expander("📝 Record Grades", expanded=False):
        st.markdown("**Add grades to completed modules**")
        
        for i, modul in enumerate(modules_without_grades):
            with st.form(f"grade_form_{i}"):
                st.markdown(f"**{modul.name}** ({modul.ects} ECTS)")
                
                col1, col2 = st.columns(2)
                with col1:
                    grade = st.number_input(f"Grade", min_value=1.0, max_value=5.0, value=2.0, step=0.1,
                                          key=f"grade_{i}", help="German grading system: 1.0 (best) to 5.0 (worst)")
                with col2:
                    exam_date = st.date_input(f"Exam Date", value=date.today(), key=f"date_{i}")
                
                status = st.selectbox("Status", ["bestanden", "nicht bestanden"], key=f"status_{i}")
                
                submitted = st.form_submit_button(f"Record Grade for {modul.name}", type="primary")
                
                if submitted:
                    # Validate grade input
                    grade_valid, grade_error = validate_grade_input(grade)
                    if not grade_valid:
                        st.error(f"❌ {grade_error}")
                        continue
                    
                    try:
                        # Create and assign the grade
                        pruefungsleistung = Pruefungsleistung(grade, exam_date, status)
                        modul.pruefungsleistung = pruefungsleistung
                        
                        # Save data
                        if save_data():
                            st.success(f"✅ Grade recorded for '{modul.name}'!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to save data.")
                    except Exception as e:
                        st.error(f"❌ Error recording grade: {e}")
                
                st.divider()


def show_edit_module_form(studiengang: Studiengang):
    """Display form for editing existing module details."""
    aktuelles_semester = studiengang.get_aktuelles_semester()
    
    if not aktuelles_semester or not aktuelles_semester.module:
        return
    
    with st.expander("✏️ Edit Modules", expanded=False):
        st.markdown("**Edit module details**")
        
        for i, modul in enumerate(aktuelles_semester.module):
            with st.form(f"edit_form_{i}"):
                st.markdown(f"**Currently: {modul.name}** ({modul.ects} ECTS)")
                
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("Module Name", value=modul.name, key=f"edit_name_{i}")
                with col2:
                    new_ects = st.number_input("ECTS Credits", min_value=1, max_value=30, 
                                             value=modul.ects, step=1, key=f"edit_ects_{i}")
                
                col1, col2 = st.columns(2)
                with col1:
                    update_submitted = st.form_submit_button(f"Update {modul.name}", type="primary")
                with col2:
                    if st.form_submit_button(f"🗑️ Delete {modul.name}", type="secondary"):
                        if st.session_state.get(f"confirm_delete_{i}", False):
                            # Remove the module
                            aktuelles_semester.module.remove(modul)
                            if save_data():
                                st.success(f"✅ Module '{modul.name}' deleted!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to save data.")
                        else:
                            st.session_state[f"confirm_delete_{i}"] = True
                            st.warning(f"⚠️ Click again to confirm deletion of '{modul.name}'")
                
                if update_submitted:
                    # Validate module input
                    is_valid, error_msg = validate_module_input(new_name, new_ects)
                    if not is_valid:
                        st.error(f"❌ {error_msg}")
                        continue
                    
                    # Check for duplicates (excluding current module)
                    if check_duplicate_module(studiengang, new_name, exclude_module=modul):
                        st.error(f"❌ A module named '{new_name}' already exists in this semester.")
                        continue
                    
                    try:
                        # Update module details
                        old_name = modul.name
                        modul.name = new_name.strip()
                        modul.ects = new_ects
                        
                        # Save data
                        if save_data():
                            st.success(f"✅ Module updated from '{old_name}' to '{modul.name}'!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to save data.")
                    except Exception as e:
                        st.error(f"❌ Error updating module: {e}")
                
                st.divider()


def show_add_module_form_for_semester(studiengang: Studiengang, semester: 'Semester'):
    """Display form for adding new modules to specific semester."""
    with st.expander(f"➕ Add New Module to Semester {semester.nummer}", expanded=False):
        st.markdown(f"**Adding to Semester {semester.nummer}**")
        
        with st.form(f"add_module_form_semester_{semester.nummer}"):
            # Module details
            module_name = st.text_input("Module Name", placeholder="e.g., Web Development")
            ects = st.number_input("ECTS Credits", min_value=1, max_value=30, value=6, step=1)
            
            # Optional grade information
            st.markdown("**Optional: Add Grade Information**")
            has_grade = st.checkbox("This module is already completed with a grade")
            
            grade = None
            exam_date = None
            if has_grade:
                grade = st.number_input("Grade", min_value=1.0, max_value=5.0, value=2.0, step=0.1, 
                                      help="German grading system: 1.0 (best) to 5.0 (worst)")
                exam_date = st.date_input("Exam Date", value=date.today())
            
            # Submit button
            submitted = st.form_submit_button("Add Module", type="primary")
            
            if submitted:
                # Validate module input
                is_valid, error_msg = validate_module_input(module_name, ects)
                if not is_valid:
                    st.error(f"❌ {error_msg}")
                    return
                
                # Check for duplicates in this semester
                if any(m.name.lower().strip() == module_name.lower().strip() for m in semester.module):
                    st.error(f"❌ A module named '{module_name}' already exists in this semester.")
                    return
                
                # Validate grade if provided
                if has_grade and grade is not None:
                    grade_valid, grade_error = validate_grade_input(grade)
                    if not grade_valid:
                        st.error(f"❌ {grade_error}")
                        return
                
                # Create new module
                try:
                    if has_grade and grade is not None:
                        pruefungsleistung = Pruefungsleistung(grade, exam_date, "bestanden")
                        new_module = Modul(module_name.strip(), ects, pruefungsleistung)
                    else:
                        new_module = Modul(module_name.strip(), ects)
                    
                    # Add to specific semester
                    semester.add_modul(new_module)
                    
                    # Save data
                    if save_data():
                        st.success(f"✅ Module '{module_name}' added to Semester {semester.nummer}!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to save data.")
                        
                except Exception as e:
                    st.error(f"❌ Error creating module: {e}")


def show_grade_recording_form_for_semester(studiengang: Studiengang, semester: 'Semester'):
    """Display form for adding grades to existing modules in specific semester."""
    # Find modules without grades
    modules_without_grades = [m for m in semester.module if m.pruefungsleistung is None]
    
    if not modules_without_grades:
        return
    
    with st.expander(f"📝 Record Grades for Semester {semester.nummer}", expanded=False):
        st.markdown(f"**Add grades for modules in Semester {semester.nummer}:**")
        
        with st.form(f"grade_recording_form_semester_{semester.nummer}"):
            selected_module_name = st.selectbox(
                "Select Module",
                options=[m.name for m in modules_without_grades],
                help="Choose a module to record a grade for"
            )
            
            grade = st.number_input(
                "Grade", 
                min_value=1.0, 
                max_value=5.0, 
                value=2.0, 
                step=0.1,
                help="German grading system: 1.0 (best) to 5.0 (worst)"
            )
            
            exam_date = st.date_input("Exam Date", value=date.today())
            
            submitted = st.form_submit_button("Record Grade", type="primary")
            
            if submitted:
                # Validate grade
                grade_valid, grade_error = validate_grade_input(grade)
                if not grade_valid:
                    st.error(f"❌ {grade_error}")
                    return
                
                # Find the selected module
                selected_module = None
                for modul in modules_without_grades:
                    if modul.name == selected_module_name:
                        selected_module = modul
                        break
                
                if selected_module:
                    try:
                        # Add grade to module
                        status = "bestanden" if grade <= 4.0 else "nicht bestanden"
                        selected_module.pruefungsleistung = Pruefungsleistung(grade, exam_date, status)
                        
                        # Save data
                        if save_data():
                            st.success(f"✅ Grade {grade} recorded for '{selected_module.name}' in Semester {semester.nummer}!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to save data.")
                    except Exception as e:
                        st.error(f"❌ Error recording grade: {e}")


def show_edit_module_form_for_semester(studiengang: Studiengang, semester: 'Semester'):
    """Display form for editing existing modules in specific semester."""
    if not semester.module:
        return
    
    with st.expander(f"✏️ Edit Modules in Semester {semester.nummer}", expanded=False):
        st.markdown(f"**Edit modules in Semester {semester.nummer}:**")
        
        for i, modul in enumerate(semester.module):
            with st.form(f"edit_module_{semester.nummer}_{i}"):
                st.markdown(f"**Editing: {modul.name}**")
                
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("Module Name", value=modul.name, key=f"edit_name_{semester.nummer}_{i}")
                with col2:
                    new_ects = st.number_input("ECTS Credits", min_value=1, max_value=30, 
                                             value=modul.ects, step=1, key=f"edit_ects_{semester.nummer}_{i}")
                
                col1, col2 = st.columns(2)
                with col1:
                    update_submitted = st.form_submit_button(f"Update {modul.name}", type="primary")
                with col2:
                    if st.form_submit_button(f"🗑️ Delete {modul.name}", type="secondary"):
                        if st.session_state.get(f"confirm_delete_{semester.nummer}_{i}", False):
                            # Remove the module
                            semester.module.remove(modul)
                            if save_data():
                                st.success(f"✅ Module '{modul.name}' deleted from Semester {semester.nummer}!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to save data.")
                        else:
                            st.session_state[f"confirm_delete_{semester.nummer}_{i}"] = True
                            st.warning(f"⚠️ Click again to confirm deletion of '{modul.name}'")
                
                if update_submitted:
                    # Validate module input
                    is_valid, error_msg = validate_module_input(new_name, new_ects)
                    if not is_valid:
                        st.error(f"❌ {error_msg}")
                        continue
                    
                    # Check for duplicates (excluding current module)
                    if any(m != modul and m.name.lower().strip() == new_name.lower().strip() for m in semester.module):
                        st.error(f"❌ A module named '{new_name}' already exists in this semester.")
                        continue
                    
                    try:
                        # Update module details
                        old_name = modul.name
                        modul.name = new_name.strip()
                        modul.ects = new_ects
                        
                        # Save data
                        if save_data():
                            st.success(f"✅ Module updated from '{old_name}' to '{modul.name}' in Semester {semester.nummer}!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to save data.")
                    except Exception as e:
                        st.error(f"❌ Error updating module: {e}")
                
                st.divider()


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
    if 'selected_semester' not in st.session_state:
        # Initialize with current semester
        aktuelles_semester = st.session_state.studiengang.get_aktuelles_semester()
        st.session_state.selected_semester = aktuelles_semester.nummer if aktuelles_semester else 1


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
        textfont=dict(color='white' if st.session_state.theme == 'dark' else '#212529', size=12, family='Arial Black'),
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
    """Display semester overview section with clickable semesters."""
    st.subheader("📚 Semesterübersicht")
    st.markdown("**Klicken Sie auf ein Semester, um es zu bearbeiten:**")
    
    cols = st.columns(len(studiengang.semester))
    
    for i, semester in enumerate(studiengang.semester):
        with cols[i % len(cols)]:
            status_icon = "✅" if semester.ist_abgeschlossen() else "⏳" if semester == studiengang.get_aktuelles_semester() else "📅"
            
            ects_erreicht = semester.berechne_ects()
            durchschnitt = semester.get_durchschnittsnote()
            note_display = f"{durchschnitt:.1f}" if durchschnitt is not None else "N/A"
            
            # Make semester clickable
            is_selected = st.session_state.selected_semester == semester.nummer
            button_type = "primary" if is_selected else "secondary"
            
            if st.button(
                f"{status_icon} Semester {semester.nummer}\nECTS: {ects_erreicht}/{semester.geplante_ects}\nØ Note: {note_display}",
                key=f"semester_{semester.nummer}",
                type=button_type,
                use_container_width=True
            ):
                st.session_state.selected_semester = semester.nummer
                st.rerun()


def show_semester_modules(studiengang: Studiengang):
    """Display and edit modules for the selected semester."""
    selected_semester_num = st.session_state.selected_semester
    selected_semester = None
    
    # Find the selected semester
    for semester in studiengang.semester:
        if semester.nummer == selected_semester_num:
            selected_semester = semester
            break
    
    if not selected_semester:
        st.error("❌ Ausgewähltes Semester nicht gefunden.")
        return
    
    st.subheader(f"📝 Semester {selected_semester.nummer}")
    
    # Display semester info
    ects_erreicht = selected_semester.berechne_ects()
    durchschnitt = selected_semester.get_durchschnittsnote()
    note_display = f"{durchschnitt:.1f}" if durchschnitt is not None else "N/A"
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("ECTS erreicht", f"{ects_erreicht}/{selected_semester.geplante_ects}")
    with col2:
        st.metric("Durchschnittsnote", note_display)
    with col3:
        completion_percentage = (ects_erreicht / selected_semester.geplante_ects * 100) if selected_semester.geplante_ects > 0 else 0
        st.metric("Abschluss", f"{completion_percentage:.0f}%")
    
    st.divider()
    
    # Display and edit modules
    if selected_semester.module:
        st.markdown("**Module in diesem Semester:**")
        
        # Find the first module without grade (considered in progress)
        modules_without_grade = [m for m in selected_semester.module if m.pruefungsleistung is None]
        first_in_progress = modules_without_grade[0] if modules_without_grade else None
        
        for modul in selected_semester.module:
            cols = st.columns([3, 1, 1, 1])
            
            with cols[0]:
                st.markdown(f'<div class="module-name">• {modul.name}</div>', unsafe_allow_html=True)
            
            with cols[1]:
                st.markdown(f'<div class="module-ects">[{modul.ects} ECTS]</div>', unsafe_allow_html=True)
            
            with cols[2]:
                if modul.ist_bestanden():
                    st.markdown('<div class="module-status status-completed">✅ bestanden</div>', unsafe_allow_html=True)
                elif modul.pruefungsleistung is None:
                    if modul == first_in_progress:
                        st.markdown('<div class="module-status status-in-progress">⏳ laufend</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="module-status status-registered">📝 angemeldet</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="module-status status-failed">❌ nicht bestanden</div>', unsafe_allow_html=True)
            
            with cols[3]:
                note = modul.get_note()
                if note:
                    st.markdown(f'<div class="module-grade">{note:.1f}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="module-grade">-</div>', unsafe_allow_html=True)
        
        st.divider()
    else:
        st.info("📝 Keine Module in diesem Semester vorhanden.")
    
    # Add module form for selected semester
    show_add_module_form_for_semester(studiengang, selected_semester)
    
    # Grade recording form for selected semester
    show_grade_recording_form_for_semester(studiengang, selected_semester)
    
    # Module editing form for selected semester
    show_edit_module_form_for_semester(studiengang, selected_semester)



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
    
    # Grade analysis section
    show_grade_analysis(studiengang)
    
    st.divider()
    
    # Semester overview section
    show_semester_overview(studiengang)
    
    st.divider()
    
    # Selected semester modules section
    show_semester_modules(studiengang)
    
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
    
    /* Override Streamlit's default text colors - more specific */
    .stMarkdown p, .stText p, .element-container p {{
        color: {colors['text']} !important;
    }}
    
    /* Ensure headings are visible */
    h1, h2, h3, h4, h5, h6 {{
        color: {colors['text']} !important;
        font-weight: 700;
    }}
    
    /* Module display styling with proper contrast */
    .module-name {{
        color: {colors['text']} !important;
        font-weight: 500;
        font-size: 1rem;
        line-height: 1.4;
    }}
    
    .module-ects {{
        color: {colors['muted']} !important;
        font-size: 0.9rem;
        font-weight: 600;
        background-color: {'#f8f9fa' if theme == 'light' else '#495057'};
        padding: 2px 6px;
        border-radius: 4px;
        display: inline-block;
    }}
    
    .module-grade {{
        color: {colors['text']} !important;
        font-weight: 600;
        font-size: 1rem;
        text-align: center;
    }}
    
    .module-status {{
        font-size: 0.85rem;
        font-weight: 600;
        padding: 2px 6px;
        border-radius: 4px;
        text-align: center;
        display: inline-block;
        min-width: 80px;
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
    
    /* Module status indicators with better visibility and backgrounds */
    .status-completed {{
        color: {'#0f5132' if theme == 'light' else colors['success']} !important;
        background-color: {'#d1edcc' if theme == 'light' else '#1e4620'} !important;
        border: 1px solid {'#a3d977' if theme == 'light' else colors['success']};
    }}
    
    .status-in-progress {{
        color: {'#664d03' if theme == 'light' else colors['warning']} !important;
        background-color: {'#fff3cd' if theme == 'light' else '#332701'} !important;
        border: 1px solid {'#ffec8b' if theme == 'light' else colors['warning']};
    }}
    
    .status-registered {{
        color: {'#055160' if theme == 'light' else colors['info']} !important;
        background-color: {'#cff4fc' if theme == 'light' else '#032830'} !important;
        border: 1px solid {'#9eeaf9' if theme == 'light' else colors['info']};
    }}
    
    .status-failed {{
        color: {'#58151c' if theme == 'light' else colors['danger']} !important;
        background-color: {'#f8d7da' if theme == 'light' else '#2c0b0e'} !important;
        border: 1px solid {'#f1aeb5' if theme == 'light' else colors['danger']};
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
    
    /* Form styling improvements for better contrast */
    .stTextInput > div > div > input {{
        color: {colors['text']} !important;
        background-color: {'#ffffff' if theme == 'light' else colors['bg']} !important;
        border: 2px solid {'#adb5bd' if theme == 'light' else colors['border']} !important;
        border-radius: 6px !important;
        font-size: 1rem !important;
        padding: 10px 14px !important;
        transition: all 0.2s ease !important;
    }}
    
    .stTextInput > div > div > input:hover {{
        border-color: {'#6c757d' if theme == 'light' else '#6c757d'} !important;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: {colors['info']} !important;
        box-shadow: 0 0 0 3px {'rgba(12, 84, 96, 0.2)' if theme == 'light' else 'rgba(33, 150, 243, 0.2)'} !important;
        outline: none !important;
        background-color: {'#ffffff' if theme == 'light' else colors['bg']} !important;
    }}
    
    .stNumberInput > div > div > input {{
        color: {colors['text']} !important;
        background-color: {'#ffffff' if theme == 'light' else colors['bg']} !important;
        border: 2px solid {'#adb5bd' if theme == 'light' else colors['border']} !important;
        border-radius: 6px !important;
        font-size: 1rem !important;
        padding: 10px 14px !important;
        transition: all 0.2s ease !important;
    }}
    
    .stNumberInput > div > div > input:hover {{
        border-color: {'#6c757d' if theme == 'light' else '#6c757d'} !important;
    }}
    
    .stNumberInput > div > div > input:focus {{
        border-color: {colors['info']} !important;
        box-shadow: 0 0 0 3px {'rgba(12, 84, 96, 0.15)' if theme == 'light' else 'rgba(33, 150, 243, 0.15)'} !important;
        outline: none !important;
    }}
    
    .stSelectbox > div > div > div {{
        color: {colors['text']} !important;
        background-color: {'#ffffff' if theme == 'light' else colors['bg']} !important;
        border: 2px solid {'#adb5bd' if theme == 'light' else colors['border']} !important;
        border-radius: 6px !important;
        padding: 10px 14px !important;
        transition: all 0.2s ease !important;
    }}
    
    .stSelectbox > div > div > div:hover {{
        border-color: {'#6c757d' if theme == 'light' else '#6c757d'} !important;
    }}
    
    .stSelectbox > div > div > div:focus {{
        border-color: {colors['info']} !important;
        box-shadow: 0 0 0 3px {'rgba(12, 84, 96, 0.2)' if theme == 'light' else 'rgba(33, 150, 243, 0.2)'} !important;
        background-color: {'#ffffff' if theme == 'light' else colors['bg']} !important;
    }}
    
    .stDateInput > div > div > input {{
        color: {colors['text']} !important;
        background-color: {'#ffffff' if theme == 'light' else colors['bg']} !important;
        border: 2px solid {'#adb5bd' if theme == 'light' else colors['border']} !important;
        border-radius: 6px !important;
        font-size: 1rem !important;
        padding: 10px 14px !important;
        transition: all 0.2s ease !important;
    }}
    
    .stDateInput > div > div > input:hover {{
        border-color: {'#6c757d' if theme == 'light' else '#6c757d'} !important;
    }}
    
    .stDateInput > div > div > input:focus {{
        border-color: {colors['info']} !important;
        box-shadow: 0 0 0 3px {'rgba(12, 84, 96, 0.2)' if theme == 'light' else 'rgba(33, 150, 243, 0.2)'} !important;
        outline: none !important;
        background-color: {'#ffffff' if theme == 'light' else colors['bg']} !important;
    }}
    
    .stCheckbox > label {{
        color: {colors['text']} !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: color 0.2s ease !important;
        padding: 4px 0 !important;
    }}
    
    .stCheckbox > label:hover {{
        color: {colors['info']} !important;
    }}
    
    .stCheckbox > label > div {{
        color: {colors['text']} !important;
    }}
    
    .stCheckbox input[type="checkbox"] {{
        accent-color: {colors['info']} !important;
        transform: scale(1.1) !important;
    }}
    
    /* Enhanced button hover effects */
    .stButton > button {{
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }}
    
    .stButton > button:active {{
        transform: translateY(1px) !important;
        box-shadow: 0 2px 4px {colors['shadow']} !important;
    }}
    
    /* Loading state improvements */
    .stSpinner {{
        color: {colors['info']} !important;
    }}
    
    /* Enhanced visual feedback */
    .stSuccess {{
        background-color: {'#d1edcc' if theme == 'light' else '#0f5132'} !important;
        border: 2px solid {colors['success']} !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        font-weight: 500 !important;
    }}
    
    .stError {{
        background-color: {'#f8d7da' if theme == 'light' else '#2c0b0e'} !important;
        border: 2px solid {colors['danger']} !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        font-weight: 500 !important;
    }}
    
    .stWarning {{
        background-color: {'#fff3cd' if theme == 'light' else '#664d03'} !important;
        border: 2px solid {colors['warning']} !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        font-weight: 500 !important;
    }}
    
    .stInfo {{
        background-color: {'#d1ecf1' if theme == 'light' else '#055160'} !important;
        border: 2px solid {colors['info']} !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        font-weight: 500 !important;
    }}
    
    /* Form labels with stronger visibility */
    .stTextInput > label, .stNumberInput > label, .stSelectbox > label, .stDateInput > label {{
        color: {colors['text']} !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        margin-bottom: 4px !important;
    }}
    
    /* Placeholder text visibility */
    .stTextInput > div > div > input::placeholder {{
        color: {colors['muted']} !important;
        opacity: 0.7 !important;
    }}
    
    /* Form submit buttons */
    .stButton > button[kind="primary"] {{
        background-color: {COLORS['primary']} !important;
        color: white !important;
        border: 2px solid {COLORS['primary']} !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }}
    
    .stButton > button[kind="primary"]:hover {{
        background-color: {COLORS['secondary']} !important;
        border-color: {COLORS['secondary']} !important;
        transform: translateY(-1px) !important;
    }}
    
    .stButton > button[kind="secondary"] {{
        background-color: {'#6c757d' if theme == 'light' else '#495057'} !important;
        color: white !important;
        border: 2px solid {'#6c757d' if theme == 'light' else '#495057'} !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }}
    
    .stButton > button[kind="secondary"]:hover {{
        background-color: {'#5a6268' if theme == 'light' else '#3d4246'} !important;
        border-color: {'#5a6268' if theme == 'light' else '#3d4246'} !important;
        transform: translateY(-1px) !important;
    }}
    
    /* Enhanced Expander styling for better light mode visibility */
    .stExpander {{
        border: 2px solid {colors['border']} !important;
        border-radius: 8px !important;
        background-color: {colors['bg']} !important;
        box-shadow: 0 2px 4px {colors['shadow']} !important;
        margin: 8px 0 !important;
    }}
    
    .stExpander > div > div > div:first-child {{
        background-color: {'#f8f9fa' if theme == 'light' else '#2d2d2d'} !important;
        border: none !important;
        border-bottom: 2px solid {colors['border']} !important;
        border-radius: 6px 6px 0 0 !important;
        padding: 12px 16px !important;
        font-weight: 600 !important;
        color: {colors['text']} !important;
    }}
    
    .stExpander > div > div > div:first-child:hover {{
        background-color: {'#e9ecef' if theme == 'light' else '#3a3a3a'} !important;
        transition: background-color 0.2s ease !important;
    }}
    
    .stExpander > div > div > div > div > p {{
        color: {colors['text']} !important;
        margin: 0 !important;
        font-weight: 600 !important;
    }}
    
    .stExpander[data-testid="stExpander"] > div:last-child {{
        background-color: {colors['bg']} !important;
        border-radius: 0 0 6px 6px !important;
        padding: 16px !important;
    }}
    
    /* Expander content area */
    .stExpander[data-testid="stExpander"][aria-expanded="true"] {{
        border-color: {colors['info']} !important;
    }}
    
    /* Form container styling for better visual separation */
    .stForm {{
        background-color: {'#ffffff' if theme == 'light' else '#1e1e1e'} !important;
        border: 1px solid {colors['border']} !important;
        border-radius: 8px !important;
        padding: 20px !important;
        margin: 12px 0 !important;
        box-shadow: 0 2px 8px {colors['shadow']} !important;
    }}
    
    .stForm > div {{
        background-color: transparent !important;
    }}
    
    /* Form section headers */
    .stForm .stMarkdown h4, 
    .stForm .stMarkdown h5,
    .stForm .stMarkdown strong {{
        color: {colors['text']} !important;
        font-weight: 600 !important;
        margin-bottom: 8px !important;
    }}
    
    /* Form dividers */
    .stForm .stDivider {{
        margin: 16px 0 !important;
    }}
    
    .stForm .stDivider > div {{
        border-color: {colors['border']} !important;
        opacity: 0.6 !important;
    }}
    
    /* Enhanced form field grouping */
    .stForm .stColumns {{
        margin: 8px 0 !important;
    }}
    
    /* Form field labels enhancement */
    .stForm label {{
        color: {colors['text']} !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        margin-bottom: 6px !important;
        display: block !important;
    }}
    
    /* Submit button area */
    .stForm .stButton {{
        margin-top: 16px !important;
    }}
    
    /* Info/warning/error message improvements */
    .stAlert {{
        border-radius: 8px;
        border-width: 2px;
        font-weight: 500;
    }}
    
    /* Ensure proper text contrast for inherited elements */
    .element-container {{
        color: {colors['text']};
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