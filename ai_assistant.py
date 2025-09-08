"""
Enhanced AI Assistant for the Cell Development Platform
Provides context-aware, intelligent assistance with full LLM experience
"""
import streamlit as st
import openai
from typing import List, Dict, Any, Optional
from ai_context import AIContextManager


class EnhancedAIAssistant:
    """Enhanced AI Assistant with context awareness and LLM integration"""
    
    def __init__(self):
        self.context_manager = AIContextManager()
        self.setup_openai()
    
    def setup_openai(self):
        """Setup OpenAI API (with fallback to local model)"""
        try:
            # Try to get OpenAI API key from environment or Streamlit secrets
            api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
            if api_key:
                openai.api_key = api_key
                self.use_openai = True
            else:
                self.use_openai = False
                st.warning("OpenAI API key not found. Using local AI responses.")
        except:
            self.use_openai = False
    
    def generate_response(self, user_message: str, current_page: str, selected_materials: Dict[str, str]) -> str:
        """Generate AI response with full context awareness"""
        # Update context
        self.context_manager.update_page_context(current_page, {"selected_materials": selected_materials})
        
        # Get context summary
        context_summary = self.context_manager.get_context_summary()
        
        # Generate response
        if self.use_openai:
            response = self._generate_openai_response(user_message, context_summary)
        else:
            response = self._generate_local_response(user_message, context_summary)
        
        # Add to conversation history
        self.context_manager.add_conversation(user_message, response)
        
        return response
    
    def _generate_openai_response(self, user_message: str, context_summary: str) -> str:
        """Generate response using OpenAI API"""
        try:
            system_prompt = f"""
You are an expert AI assistant for the Cell Development Platform, a battery material analysis and optimization application.

{context_summary}

Your role is to:
1. Help users navigate the application and understand its features
2. Explain battery materials, their properties, and analysis methods
3. Guide users through data analysis and interpretation
4. Provide technical insights about battery technology
5. Suggest next steps and best practices

Guidelines:
- Be helpful, accurate, and professional
- Use technical terms appropriately but explain them when needed
- Provide specific, actionable advice
- Reference the current page and context when relevant
- If you don't know something, say so and suggest where to find the information
- Keep responses concise but comprehensive
- Use emojis sparingly and appropriately

Current user message: {user_message}
"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"Error with OpenAI API: {str(e)}")
            return self._generate_local_response(user_message, context_summary)
    
    def _generate_local_response(self, user_message: str, context_summary: str) -> str:
        """Generate response using local AI logic"""
        user_lower = user_message.lower()
        current_page = self.context_manager.context["user_session"]["current_page"]
        
        # Navigation commands
        if any(word in user_lower for word in ["go to", "navigate to", "open", "show"]):
            return self._handle_navigation(user_message, user_lower)
        
        # Material information requests
        elif any(word in user_lower for word in ["material", "nmc811", "lco", "nca", "graphite", "silicon", "tin"]):
            return self._handle_material_questions(user_message, user_lower)
        
        # Analysis help
        elif any(word in user_lower for word in ["psd", "ocv", "gitt", "eis", "plot", "analysis"]):
            return self._handle_analysis_questions(user_message, user_lower)
        
        # Help requests
        elif any(word in user_lower for word in ["help", "how", "what", "explain"]):
            return self._handle_help_requests(user_message, user_lower, current_page)
        
        # Data editing questions
        elif any(word in user_lower for word in ["edit", "data", "coa", "table"]):
            return self._handle_data_questions(user_message, user_lower)
        
        # Export questions
        elif any(word in user_lower for word in ["export", "download", "excel", "save"]):
            return self._handle_export_questions(user_message, user_lower)
        
        # General conversation
        else:
            return self._handle_general_conversation(user_message, user_lower, current_page)
    
    def _handle_navigation(self, user_message: str, user_lower: str) -> str:
        """Handle navigation requests"""
        if "home" in user_lower or "main" in user_lower:
            return "I'll take you to the home page where you can access all the tools. Click the 'Home' button or use the navigation."
        elif "material" in user_lower and "selector" in user_lower:
            return "I'll navigate you to the Material Selector where you can choose between Cathode, Anode, Electrolyte, or Separator materials."
        elif "cathode" in user_lower:
            return "I'll take you to the Cathode Materials page where you can analyze NMC811, LCO, or NCA materials."
        elif "anode" in user_lower:
            return "I'll take you to the Anode Materials page where you can analyze Graphite, Silicon, or Tin materials."
        else:
            return "I can help you navigate to different sections. Try saying 'go to home', 'show cathode materials', or 'open material selector'."
    
    def _handle_material_questions(self, user_message: str, user_lower: str) -> str:
        """Handle material-related questions"""
        # Check for specific materials
        materials = {
            "nmc811": ("cathode", "NMC811"),
            "lco": ("cathode", "LCO"),
            "nca": ("cathode", "NCA"),
            "graphite": ("anode", "Graphite"),
            "silicon": ("anode", "Silicon"),
            "tin": ("anode", "Tin")
        }
        
        for material_key, (material_type, material_name) in materials.items():
            if material_key in user_lower:
                info = self.context_manager.get_material_info(material_type, material_name)
                return f"Here's information about {material_name}:\n\n{info}\n\nTo analyze this material, navigate to the {material_type.title()} Materials page and select {material_name}."
        
        # General material questions
        if "cathode" in user_lower:
            return "Cathode materials are the positive electrode in lithium-ion batteries. Available options are NMC811, LCO, and NCA. Each has different properties like capacity, voltage, and cycle life. Would you like to know about a specific cathode material?"
        elif "anode" in user_lower:
            return "Anode materials are the negative electrode in lithium-ion batteries. Available options are Graphite, Silicon, and Tin. Each has different capacity and performance characteristics. Would you like to know about a specific anode material?"
        else:
            return "I can help you understand different battery materials. We have cathode materials (NMC811, LCO, NCA) and anode materials (Graphite, Silicon, Tin). What specific material would you like to know about?"
    
    def _handle_analysis_questions(self, user_message: str, user_lower: str) -> str:
        """Handle analysis-related questions"""
        if "psd" in user_lower:
            help_text = self.context_manager.get_analysis_help("PSD")
            return f"{help_text}\n\nTo generate PSD plots, go to the Materials page, select a material, and choose 'Particle Size Distribution' from the plot options."
        elif "ocv" in user_lower:
            help_text = self.context_manager.get_analysis_help("OCV")
            return f"{help_text}\n\nTo view OCV data, go to the Materials page, select a material, and choose 'OCV' from the performance data options."
        elif "gitt" in user_lower:
            help_text = self.context_manager.get_analysis_help("GITT")
            return f"{help_text}\n\nTo view GITT data, go to the Materials page, select a material, and choose 'GITT' from the performance data options."
        elif "eis" in user_lower:
            help_text = self.context_manager.get_analysis_help("EIS")
            return f"{help_text}\n\nTo view EIS data, go to the Materials page, select a material, and choose 'EIS' from the performance data options."
        elif "plot" in user_lower:
            return "I can help you with different types of plots:\n\n• PSD (Particle Size Distribution) - Shows particle size distribution\n• OCV (Open Circuit Voltage) - Shows voltage vs capacity\n• GITT - Shows voltage response over time\n• EIS - Shows impedance vs frequency\n\nNavigate to a Materials page to generate these plots."
        else:
            return "I can help you understand different analysis methods. We have PSD analysis, OCV curves, GITT measurements, and EIS analysis. What specific analysis would you like to know about?"
    
    def _handle_help_requests(self, user_message: str, user_lower: str, current_page: str) -> str:
        """Handle help requests"""
        if "help" in user_lower:
            page_help = self.context_manager.get_page_specific_help(current_page)
            suggestions = self.context_manager.get_suggestions(current_page, user_message)
            
            response = f"Here's how I can help you:\n\n{page_help}\n\nSUGGESTIONS:\n"
            for i, suggestion in enumerate(suggestions, 1):
                response += f"{i}. {suggestion}\n"
            
            response += "\nYou can also ask me about:\n• Specific materials and their properties\n• How to interpret different types of plots\n• Data editing and export features\n• Navigation and app features"
            
            return response
        else:
            return "I'm here to help! You can ask me about:\n• Navigation and app features\n• Battery materials and their properties\n• Data analysis and interpretation\n• How to use specific tools\n• Technical questions about battery technology\n\nWhat would you like to know?"
    
    def _handle_data_questions(self, user_message: str, user_lower: str) -> str:
        """Handle data editing questions"""
        if "coa" in user_lower:
            return "CoA (Certificate of Analysis) data includes material properties like particle size, surface area, density, capacity, and chemical composition. You can edit this data using the interactive table in the Materials pages. Changes are automatically saved as JSON files."
        elif "edit" in user_lower:
            return "To edit data, go to a Materials page, select a material, and use the 'CoA Data Editor' table. You can modify values directly in the table and click 'Update CoA Data' to save changes."
        else:
            return "I can help you with data editing. The app allows you to edit CoA (Certificate of Analysis) data for different materials. Navigate to a Materials page to access the data editor."
    
    def _handle_export_questions(self, user_message: str, user_lower: str) -> str:
        """Handle export questions"""
        return "You can export data in Excel format with multiple sheets including CoA data, OCV, GITT, EIS, and material properties. Go to a Materials page, select a material, and click 'Export to Excel' to download the data."
    
    def _handle_general_conversation(self, user_message: str, user_lower: str, current_page: str) -> str:
        """Handle general conversation"""
        suggestions = self.context_manager.get_suggestions(current_page, user_message)
        
        response = f"I understand you're asking about: '{user_message}'\n\n"
        response += "Here are some things I can help you with:\n"
        for i, suggestion in enumerate(suggestions, 1):
            response += f"{i}. {suggestion}\n"
        
        response += "\nFeel free to ask me about materials, analysis methods, or how to use the app!"
        
        return response
    
    def get_contextual_suggestions(self, current_page: str) -> List[str]:
        """Get contextual suggestions for the current page"""
        return self.context_manager.get_suggestions(current_page, "")
    
    def get_recent_actions(self) -> List[Dict[str, Any]]:
        """Get recent user actions"""
        return self.context_manager.context["user_session"]["recent_actions"]
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.context_manager.context["conversation_history"]
