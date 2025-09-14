# 🔋 Cell Development Platform

A comprehensive Streamlit web application for battery cell development, material analysis, and design optimization.

## 📁 Project Structure

```
cell-development-platform/
├── main.py                          # Main entry point
├── core/                            # Core application files
│   ├── __init__.py
│   ├── app.py                       # Main Streamlit application
│   └── pages.py                     # Page rendering functions
├── modules/                         # Supporting modules
│   ├── __init__.py
│   ├── ai_assistant.py              # AI chat functionality
│   ├── ai_context.py                # AI context management
│   ├── cell_design.py               # Cell design workflow
│   ├── coa_manager.py               # CoA management
│   ├── coa_performance.py           # CoA performance analysis
│   ├── electrode_design.py          # Electrode design
│   ├── electrode_materials.py       # Electrode materials
│   ├── material_data.py             # Material data
│   ├── ocv_curves.py                # OCV curve generation
│   ├── plotting.py                  # Plotting functions
│   ├── schematic_generator.py       # Schematic generation
│   ├── theme_colors.py              # Theme management
│   └── utils.py                     # Utility functions
├── data/                            # Data files
│   ├── material_database.json       # Material database
│   ├── material_lib/                # Material library
│   └── electrode_material_lib/      # Electrode material library
├── docs/                            # Documentation
│   ├── README.md                    # Main documentation
│   └── ENV_SETUP.md                 # Environment setup guide
├── cell_development_requirements.txt # Dependencies
├── pyproject.toml                   # Project configuration
└── uv.lock                          # Lock file
```

## 🚀 Quick Start

### Installation

1. **Install dependencies**:
   ```bash
   pip install -r cell_development_requirements.txt
   ```

2. **Run the application**:
   ```bash
   python main.py
   ```
   
   Or directly with Streamlit:
   ```bash
   streamlit run main.py
   ```

3. **Open your browser** to `http://localhost:8501`

## 🏗️ Architecture

### Core Module (`core/`)
- **`app.py`**: Main Streamlit application with page configuration and routing
- **`pages.py`**: All page rendering functions (home, material selector, cell design, etc.)

### Modules (`modules/`)
- **AI Components**: `ai_assistant.py`, `ai_context.py`
- **Design Components**: `cell_design.py`, `schematic_generator.py`, `electrode_design.py`
- **Data Components**: `material_data.py`, `coa_manager.py`, `coa_performance.py`
- **Utility Components**: `plotting.py`, `theme_colors.py`, `utils.py`

### Data (`data/`)
- **`material_database.json`**: Main material database
- **`material_lib/`**: Material library files
- **`electrode_material_lib/`**: Electrode material library files

### Documentation (`docs/`)
- **`README.md`**: Main documentation
- **`ENV_SETUP.md`**: Environment setup instructions

## 🔧 Development

The modular structure makes it easy to:
- Add new features by creating modules in the `modules/` folder
- Maintain clean separation of concerns
- Test individual components
- Scale the application

## 📋 Features

- **Material Analysis**: Comprehensive cathode material analysis (NMC811, LCO, NCA)
- **Cell Design**: Interactive cell design workflow with form factor selection
- **AI Assistant**: Context-aware chat interface for guidance
- **Data Export**: Excel export functionality for model parameters
- **CoA Management**: Certificate of Analysis data management
- **Performance Visualization**: OCV curves, GITT, EIS, and cycle life plots
