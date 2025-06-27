# 🎓 Student Goal Dashboard

A Python-based dashboard application for students to track their study programs, modules, ECTS credits, and academic progress. This project demonstrates Object-Oriented Programming principles in Python with a modern, accessible web interface.

## ✨ Features

- **Progress Tracking**: Visual representation of overall study progress with ECTS completion
- **Semester Overview**: Detailed view of each semester with completion status
- **Current Modules**: Track ongoing and registered modules with grades
- **Grade Analysis**: Monitor GPA and academic performance against targets
- **Theme Support**: Light and dark mode for better accessibility
- **Alert System**: Warnings for grades below target and missing ECTS
- **Data Persistence**: JSON-based storage for demo purposes

## 🏗️ Architecture

The project follows a clean, object-oriented architecture:

- **`models.py`**: Core data models (Studiengang, Semester, Modul, Pruefungsleistung)
- **`gui.py`**: Streamlit-based dashboard interface with accessibility features
- **`data.py`**: Sample data creation and management
- **`main.py`**: Application entry point
- **`test_functionality.py`**: Comprehensive test suite

## 🎨 Design

- **Color Scheme**: Custom accessible color palette with proper contrast ratios
- **UI Framework**: Streamlit for modern, responsive dashboard interface
- **Accessibility**: WCAG-compliant design with keyboard navigation and screen reader support
- **Responsiveness**: Works on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download the project**
   ```bash
   cd goal-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```
   
   Or run directly with Streamlit:
   ```bash
   streamlit run gui.py
   ```

4. **Access the dashboard**
   - The dashboard will automatically open in your browser
   - Default URL: `http://localhost:8501`

## 🧪 Testing

Run the test suite to verify core functionality:

```bash
python test_functionality.py
```

This tests all components without requiring GUI dependencies.

## 📊 Sample Data

The application includes realistic sample data representing:
- 6-semester Computer Science Bachelor program (180 ECTS)
- Completed semesters 1-2 with various grades
- Current semester 3 with ongoing modules
- Planned future semesters

## 🎯 Key Components

### Data Models

- **`Studiengang`**: Complete study program with progress calculation
- **`Semester`**: Individual semester containing modules
- **`Modul`**: Course modules with ECTS credits and grades
- **`Pruefungsleistung`**: Exam/assessment results

### Dashboard Features

- **Progress Bar**: Visual ECTS completion tracking
- **Semester Cards**: Overview of all semesters with status indicators
- **Module List**: Current semester modules with completion status
- **Grade Metrics**: GPA tracking and target comparison
- **Alert System**: Automatic warnings for academic issues

## ♿ Accessibility Features

- High contrast color schemes for both light and dark modes
- Keyboard navigation support
- Screen reader compatibility with ARIA labels
- Focus indicators for interactive elements
- Semantic HTML structure

## 🎨 Customization

### Colors
The color scheme can be modified in `gui.py`:
```python
COLORS = {
    'primary': '#F67280',
    'secondary': '#C06C84', 
    'third': '#6C5B7B',
    'fourth': '#355C7D'
}
```

### Data
Modify `data.py` to create different sample data or integrate with real data sources.

## 🔧 Technical Details

- **Frontend**: Streamlit with Plotly for visualizations
- **Data Storage**: JSON files for persistence
- **Testing**: Comprehensive unit tests for all components
- **Architecture**: Clean separation of concerns with OOP principles

## 📱 Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile-responsive design
- Works with screen readers and assistive technologies

## 🤝 Contributing

This is a demo project showcasing OOP principles in Python. Feel free to:
- Extend the data models
- Add new visualization features
- Implement additional accessibility improvements
- Create new themes or color schemes

## 📄 License

This project is for educational purposes demonstrating Object-Oriented Programming in Python.