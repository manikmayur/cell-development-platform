"""
AI Context Manager for the Cell Development Platform
Provides context-aware assistance based on current application state
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


class AIContextManager:
    """Manages AI context and application state for intelligent assistance"""
    
    def __init__(self):
        self.context_file = "data/ai_context.json"
        self.ensure_data_directory()
        self.load_context()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        if not os.path.exists("data"):
            os.makedirs("data")
    
    def load_context(self):
        """Load AI context from file"""
        if os.path.exists(self.context_file):
            try:
                with open(self.context_file, 'r') as f:
                    self.context = json.load(f)
            except:
                self.context = self.get_default_context()
        else:
            self.context = self.get_default_context()
    
    def save_context(self):
        """Save AI context to file"""
        with open(self.context_file, 'w') as f:
            json.dump(self.context, f, indent=2)
    
    def get_default_context(self) -> Dict[str, Any]:
        """Get default AI context"""
        return {
            "app_info": {
                "name": "Cell Development Platform",
                "version": "1.0.0",
                "description": "Advanced battery material analysis and optimization tools"
            },
            "available_pages": {
                "home": "Main dashboard with tool selection",
                "material_selector": "Select material type (cathode, anode, electrolyte, separator)",
                "cathode_materials": "Analyze cathode materials (NMC811, LCO, NCA)",
                "anode_materials": "Analyze anode materials (Graphite, Silicon, Tin)",
                "electrolyte_materials": "Electrolyte material analysis (coming soon)",
                "separator_materials": "Separator material analysis (coming soon)",
                "process_optimization": "Manufacturing process optimization (coming soon)",
                "performance_analysis": "Cell performance analysis (coming soon)",
                "cell_design": "Battery cell architecture design with form factor selection and simulation",
                "testing_protocol": "Testing procedure definition (coming soon)",
                "data_analytics": "Advanced data analysis tools (coming soon)",
                "lifecycle_analysis": "Battery lifecycle analysis (coming soon)",
                "thermal_management": "Thermal analysis and control (coming soon)",
                "fast_charging": "Fast charging optimization (coming soon)"
            },
            "material_types": {
                "cathode": {
                    "materials": ["NMC811", "LCO", "NCA"],
                    "properties": ["particle_size", "surface_area", "density", "capacity", "voltage", "cycle_life"],
                    "analysis": ["PSD", "OCV", "GITT", "EIS", "cycle_life", "coulombic_efficiency"]
                },
                "anode": {
                    "materials": ["Graphite", "Silicon", "Tin"],
                    "properties": ["particle_size", "surface_area", "density", "capacity", "voltage", "cycle_life"],
                    "analysis": ["PSD", "OCV", "GITT", "EIS"]
                }
            },
            "capabilities": {
                "data_editing": "Edit CoA (Certificate of Analysis) data with editable tables",
                "plotting": "Generate PSD plots, performance plots (OCV, GITT, EIS), cycle life analysis",
                "export": "Export data to Excel with multiple sheets",
                "json_storage": "Save and load data as JSON files for persistence",
                "material_comparison": "Compare different materials and their properties"
            },
            "user_session": {
                "current_page": "home",
                "selected_materials": {},
                "recent_actions": [],
                "session_start": datetime.now().isoformat()
            },
            "conversation_history": []
        }
    
    def update_page_context(self, current_page: str, additional_info: Dict[str, Any] = None):
        """Update current page context"""
        self.context["user_session"]["current_page"] = current_page
        if additional_info:
            self.context["user_session"].update(additional_info)
        self.save_context()
    
    def update_material_selection(self, material_type: str, material_name: str):
        """Update selected material context"""
        self.context["user_session"]["selected_materials"][material_type] = material_name
        self.save_context()
    
    def add_recent_action(self, action: str, details: Dict[str, Any] = None):
        """Add recent action to context"""
        action_entry = {
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "page": self.context["user_session"]["current_page"],
            "details": details or {}
        }
        self.context["user_session"]["recent_actions"].insert(0, action_entry)
        # Keep only last 10 actions
        self.context["user_session"]["recent_actions"] = self.context["user_session"]["recent_actions"][:10]
        self.save_context()
    
    def add_conversation(self, user_message: str, ai_response: str):
        """Add conversation to history"""
        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "ai": ai_response,
            "context": {
                "page": self.context["user_session"]["current_page"],
                "selected_materials": self.context["user_session"]["selected_materials"].copy()
            }
        }
        self.context["conversation_history"].append(conversation_entry)
        # Keep only last 20 conversations
        self.context["conversation_history"] = self.context["conversation_history"][-20:]
        self.save_context()
    
    def get_context_summary(self) -> str:
        """Get a summary of current context for AI"""
        current_page = self.context["user_session"]["current_page"]
        selected_materials = self.context["user_session"]["selected_materials"]
        recent_actions = self.context["user_session"]["recent_actions"][:3]  # Last 3 actions
        
        summary = f"""
CURRENT APPLICATION CONTEXT:
- Current Page: {current_page} ({self.context['available_pages'].get(current_page, 'Unknown page')})
- Selected Materials: {selected_materials if selected_materials else 'None'}
- Recent Actions: {[action['action'] for action in recent_actions] if recent_actions else 'None'}

AVAILABLE CAPABILITIES:
- Data Editing: Edit CoA data with interactive tables
- Plotting: Generate PSD, OCV, GITT, EIS plots
- Export: Export data to Excel format
- Material Analysis: Compare and analyze different materials
- JSON Storage: Persistent data storage and retrieval

MATERIAL TYPES AND OPTIONS:
- Cathode Materials: {', '.join(self.context['material_types']['cathode']['materials'])}
- Anode Materials: {', '.join(self.context['material_types']['anode']['materials'])}
- Analysis Types: {', '.join(self.context['material_types']['cathode']['analysis'])}

APPLICATION PURPOSE:
{self.context['app_info']['description']}
"""
        return summary
    
    def get_page_specific_help(self, page: str) -> str:
        """Get page-specific help information"""
        page_help = {
            "home": """
HOME PAGE HELP:
- This is the main dashboard with 9 different tools
- Click any button to navigate to that tool
- Available tools: Material Selector, Process Optimization, Performance Analysis, 
  Cell Design, Testing Protocol, Data Analytics, Lifecycle Analysis, Thermal Management, Fast Charging
- Use the AI Assistant on the right for guidance
""",
            "material_selector": """
MATERIAL SELECTOR HELP:
- Choose between 4 material types: Cathode, Anode, Electrolyte, Separator
- Cathode materials: NMC811, LCO, NCA (fully functional)
- Anode materials: Graphite, Silicon, Tin (fully functional)
- Electrolyte and Separator pages are coming soon
""",
            "cathode_materials": """
CATHODE MATERIALS HELP:
- Select from NMC811, LCO, or NCA materials
- Edit CoA data using the interactive table
- Generate PSD (Particle Size Distribution) plots
- View performance data: OCV, GITT, EIS plots
- Export data to Excel format
- All data is saved as JSON files for persistence
""",
            "anode_materials": """
ANODE MATERIALS HELP:
- Select from Graphite, Silicon, or Tin materials
- Edit CoA data using the interactive table
- Generate PSD (Particle Size Distribution) plots
- View performance data: OCV, GITT, EIS plots
- Export data to Excel format
- All data is saved as JSON files for persistence
""",
            "cell_design": """
CELL DESIGN HELP:
- Select form factor: Cylindrical, Pouch, or Prismatic
- Adjust dimensions with interactive sliders
- View 3D visualization of selected form factor
- Choose cathode and anode materials
- Select electrolyte and separator
- Run performance and life simulation
- Get estimated capacity and energy density
"""
        }
        return page_help.get(page, "No specific help available for this page.")
    
    def get_material_info(self, material_type: str, material_name: str) -> str:
        """Get detailed information about a specific material"""
        if material_type == "cathode":
            material_info = {
                "NMC811": """
NMC811 (LiNi0.8Mn0.1Co0.1O2):
- High energy density cathode material
- Typical capacity: ~200 mAh/g
- Operating voltage: ~3.8V
- Good cycle life: ~1000 cycles
- Used in electric vehicles and energy storage
""",
                "LCO": """
LCO (LiCoO2):
- Traditional cathode material
- Lower capacity: ~140 mAh/g
- Higher voltage: ~3.9V
- Moderate cycle life: ~500 cycles
- Used in consumer electronics
""",
                "NCA": """
NCA (LiNi0.8Co0.15Al0.05O2):
- High capacity cathode material
- Capacity: ~190 mAh/g
- Operating voltage: ~3.7V
- Good cycle life: ~800 cycles
- Used in Tesla vehicles
"""
            }
        elif material_type == "anode":
            material_info = {
                "Graphite": """
Graphite (C):
- Standard anode material
- Capacity: ~372 mAh/g
- Low voltage: ~0.1V
- Excellent cycle life: ~2000 cycles
- Most common in commercial batteries
""",
                "Silicon": """
Silicon (Si):
- High capacity anode material
- Very high capacity: ~4200 mAh/g
- Moderate voltage: ~0.4V
- Limited cycle life: ~500 cycles
- Used in next-generation batteries
""",
                "Tin": """
Tin (Sn):
- Alternative anode material
- Capacity: ~994 mAh/g
- Moderate voltage: ~0.6V
- Limited cycle life: ~300 cycles
- Research material for future batteries
"""
            }
        else:
            return f"No detailed information available for {material_type} material {material_name}"
        
        return material_info.get(material_name, f"No detailed information available for {material_name}")
    
    def get_analysis_help(self, analysis_type: str) -> str:
        """Get help for specific analysis types"""
        analysis_help = {
            "PSD": """
Particle Size Distribution (PSD) Analysis:
- Shows the distribution of particle sizes in the material
- D10, D50, D90 values represent 10%, 50%, 90% of particles below that size
- Important for electrode manufacturing and performance
- Can view as normal distribution, cumulative distribution, or both
""",
            "OCV": """
Open Circuit Voltage (OCV) Analysis:
- Shows voltage vs capacity relationship
- Important for understanding energy density
- Helps in battery design and optimization
- Measured at equilibrium conditions
""",
            "GITT": """
Galvanostatic Intermittent Titration Technique (GITT):
- Shows voltage response over time during charging/discharging
- Used to measure diffusion coefficients
- Important for understanding kinetic properties
- Helps optimize charging protocols
""",
            "EIS": """
Electrochemical Impedance Spectroscopy (EIS):
- Shows impedance vs frequency relationship
- Identifies different resistance components
- Important for understanding cell resistance
- Helps in cell design optimization
"""
        }
        return analysis_help.get(analysis_type, f"No help available for {analysis_type} analysis")
    
    def get_suggestions(self, current_page: str, user_input: str) -> List[str]:
        """Get contextual suggestions based on current page and user input"""
        suggestions = []
        
        if current_page == "home":
            suggestions = [
                "Navigate to Material Selector to analyze battery materials",
                "Try 'show me cathode materials' to go directly to cathode analysis",
                "Ask about specific materials like 'tell me about NMC811'",
                "Use 'help' to get general guidance"
            ]
        elif current_page == "material_selector":
            suggestions = [
                "Select 'Cathode Materials' to analyze NMC811, LCO, or NCA",
                "Select 'Anode Materials' to analyze Graphite, Silicon, or Tin",
                "Ask about specific materials or analysis types",
                "Try 'compare cathode materials' for material comparison"
            ]
        elif current_page in ["cathode_materials", "anode_materials"]:
            suggestions = [
                "Edit CoA data using the interactive table",
                "Generate PSD plots to analyze particle size distribution",
                "View OCV, GITT, or EIS performance data",
                "Export data to Excel for further analysis",
                "Try 'show me PSD plot' or 'generate OCV plot'"
            ]
        
        # Add general suggestions based on user input
        if "help" in user_input.lower():
            suggestions.append("I can help you navigate the app, explain materials, and guide you through analysis")
        if "material" in user_input.lower():
            suggestions.append("I can explain different materials and their properties")
        if "plot" in user_input.lower():
            suggestions.append("I can help you generate and interpret different types of plots")
        
        return suggestions[:4]  # Return top 4 suggestions
