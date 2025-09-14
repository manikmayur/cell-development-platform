# 🔋 Cell Development Platform

A comprehensive Streamlit web application for battery cell development, material analysis, and design optimization.

## Features

### 🏠 Landing Page
- **80:20 Layout**: Main content area with integrated chat interface
- **3x3 Grid**: Interactive cards for different development tools
- **Material Selector**: Primary entry point for material analysis

### 🔬 Material Analysis
- **Cathode Materials**: NMC811, LCO, NCA with comprehensive data
- **Interactive Plots**: OCV, GITT, EIS performance visualization
- **CoA Sheets**: Certificate of Analysis data tables
- **Cycle Life Analysis**: Capacity retention and coulombic efficiency plots

### 🤖 AI Chat Interface
- **Natural Language Control**: Control app navigation via chat commands
- **Material Selection**: Voice/text commands to select specific materials
- **Smart Navigation**: Seamless integration with main interface

### 📊 Data Export
- **Excel Export**: Generate comprehensive model parameter files
- **Multiple Sheets**: OCV, TOCV, Diffusion Coefficient, Charge Transfer Kinetics
- **Professional Format**: Ready for research and development use

## Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd cell-development-platform
   ```

2. **Install dependencies**:
   ```bash
   pip install -r cell_development_requirements.txt
   ```

3. **Run the application**:
   ```bash
   python run_cell_development_app.py
   ```
   
   Or directly with Streamlit:
   ```bash
   streamlit run cell_development_app.py
   ```

4. **Open your browser** to `http://localhost:8501`

### Usage

1. **Navigate**: Use the 3x3 grid or chat interface to explore features
2. **Select Materials**: Click "Material Selector" → "Cathode Materials"
3. **Choose Material**: Use dropdown to select NMC811, LCO, or NCA
4. **Analyze Data**: View CoA table, performance plots, and cycle life data
5. **Export Parameters**: Click "Get Model Parameters" to download Excel file
6. **Chat Control**: Use natural language in the chat panel to navigate

### Chat Commands

- `"go to material selector"` - Navigate to material selection
- `"show cathode materials"` - Open cathode materials page
- `"select NMC811"` - Choose specific cathode material
- `"go home"` - Return to main page

## Architecture

### File Structure
```
cell-development-platform/
├── cell_development_app.py          # Main Streamlit application
├── run_cell_development_app.py      # Application launcher
├── cell_development_requirements.txt # Python dependencies
├── README_CELL_DEVELOPMENT.md       # This file
└── data/                            # Sample data (if needed)
```

### Key Components

1. **Session State Management**: Tracks current page and selections
2. **Material Database**: Comprehensive cathode material data
3. **Interactive Plotting**: Plotly-based visualizations
4. **Excel Generation**: Dynamic parameter file creation
5. **Chat Integration**: Natural language processing for navigation

## Material Database

### Supported Cathode Materials

| Material | Formula | Capacity | Voltage | Energy Density |
|----------|---------|----------|---------|----------------|
| NMC811   | LiNi₀.₈Mn₀.₁Co₀.₁O₂ | 200 mAh/g | 3.8V | 760 Wh/kg |
| LCO      | LiCoO₂ | 140 mAh/g | 3.9V | 546 Wh/kg |
| NCA      | LiNi₀.₈Co₀.₁₅Al₀.₀₅O₂ | 190 mAh/g | 3.7V | 703 Wh/kg |

### Performance Data Types

- **OCV**: Open Circuit Voltage vs Capacity
- **GITT**: Galvanostatic Intermittent Titration Technique
- **EIS**: Electrochemical Impedance Spectroscopy
- **Cycle Life**: Capacity retention over cycles
- **Coulombic Efficiency**: Charge efficiency over cycles

## Technical Requirements

- Python 3.8+
- Streamlit 1.28+
- Pandas 1.5+
- Plotly 5.15+
- OpenPyXL 3.1+

## Development

### Adding New Materials

1. Add material data to `CATHODE_MATERIALS` dictionary
2. Include performance data, CoA information, and cycle life data
3. Update dropdown options in the UI

### Extending Functionality

- **Anode Materials**: Follow cathode materials pattern
- **Electrolyte Analysis**: Add new material type pages
- **Advanced Analytics**: Extend plotting capabilities
- **Data Import**: Add CSV/Excel import functionality

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions, issues, or feature requests, please open an issue on GitHub.

---

**Built with ❤️ for the battery research community**
