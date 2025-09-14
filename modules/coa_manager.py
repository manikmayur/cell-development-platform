"""
Enhanced CoA (Certificate of Analysis) Manager
Provides unified CoA table, PDF loading, and editable functionality
"""

import streamlit as st
import pandas as pd
import json
import os
from typing import Dict, List, Optional, Any
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from .theme_colors import get_plotly_theme, get_current_theme


class COAManager:
    """Manages Certificate of Analysis data with unified table and editing capabilities"""
    
    def __init__(self):
        self.plotly_theme = get_plotly_theme()[get_current_theme()]
        self.material_database = self._load_material_database()
        self.coa_data = self._load_coa_data()
    
    def _load_material_database(self) -> Dict:
        """Load material database from JSON file"""
        try:
            database_path = "data/material_database.json"
            if os.path.exists(database_path):
                with open(database_path, 'r') as f:
                    return json.load(f)
            else:
                st.error(f"Material database not found at {database_path}")
                return {"materials": {}}
        except Exception as e:
            st.error(f"Error loading material database: {e}")
            return {"materials": {}}
    
    def _load_coa_data(self) -> Dict:
        """Load CoA data from JSON file"""
        try:
            coa_path = "coa_data.json"
            if os.path.exists(coa_path):
                with open(coa_path, 'r') as f:
                    return json.load(f)
            else:
                # Initialize with default CoA data from material database
                return self._initialize_coa_data()
        except Exception as e:
            st.error(f"Error loading CoA data: {e}")
            return self._initialize_coa_data()
    
    def _initialize_coa_data(self) -> Dict:
        """Initialize CoA data from material database"""
        coa_data = {}
        materials = self.material_database.get("materials", {})
        
        for material_id, material_info in materials.items():
            coa_data[material_id] = {
                "material_name": material_info["name"],
                "material_type": material_info["type"],
                "purity": material_info["purity"],
                "theoretical_capacity": material_info["theoretical_capacity"],
                "physical_properties": material_info["physical_properties"].copy(),
                "electrochemical_properties": material_info["electrochemical_properties"].copy(),
                "additional_properties": {
                    "moisture_content": 0.1,
                    "ph_value": 7.0,
                    "conductivity": 1.0,
                    "impurities": "None detected",
                    "batch_number": "BATCH-001",
                    "manufacturing_date": "2024-01-01",
                    "expiry_date": "2025-01-01",
                    "storage_conditions": "Room temperature, dry",
                    "safety_data": "MSDS available",
                    "certification": "ISO 9001:2015"
                }
            }
        
        return coa_data
    
    def save_coa_data(self):
        """Save CoA data to JSON file"""
        try:
            with open("coa_data.json", 'w') as f:
                json.dump(self.coa_data, f, indent=2)
            st.success("CoA data saved successfully!")
        except Exception as e:
            st.error(f"Error saving CoA data: {e}")
    
    def get_available_materials(self) -> List[str]:
        """Get list of available materials"""
        return list(self.coa_data.keys())
    
    def get_material_coa(self, material_id: str) -> Dict:
        """Get CoA data for a specific material"""
        return self.coa_data.get(material_id, {})
    
    def update_material_coa(self, material_id: str, updated_data: Dict):
        """Update CoA data for a specific material"""
        if material_id in self.coa_data:
            self.coa_data[material_id].update(updated_data)
    
    def create_unified_coa_table(self) -> pd.DataFrame:
        """Create unified CoA table for all materials"""
        data = []
        
        for material_id, coa_info in self.coa_data.items():
            row = {
                "Material ID": material_id,
                "Material Name": coa_info.get("material_name", ""),
                "Type": coa_info.get("material_type", ""),
                "Purity (%)": coa_info.get("purity", ""),
                "Theoretical Capacity (mAh/g)": coa_info.get("theoretical_capacity", 0),
                "Particle Size D50 (μm)": coa_info.get("physical_properties", {}).get("particle_size_d50", 0),
                "Surface Area (m²/g)": coa_info.get("physical_properties", {}).get("surface_area", 0),
                "Tap Density (g/cm³)": coa_info.get("physical_properties", {}).get("tap_density", 0),
                "True Density (g/cm³)": coa_info.get("physical_properties", {}).get("true_density", 0),
                "First Cycle Efficiency (%)": coa_info.get("electrochemical_properties", {}).get("first_cycle_efficiency", 0),
                "Cycle Life": coa_info.get("electrochemical_properties", {}).get("cycle_life", 0),
                "Rate Capability 2C (%)": coa_info.get("electrochemical_properties", {}).get("rate_capability_2C", 0),
                "Low Temp Performance (%)": coa_info.get("electrochemical_properties", {}).get("low_temp_performance", 0),
                "Moisture Content (%)": coa_info.get("additional_properties", {}).get("moisture_content", 0),
                "pH Value": coa_info.get("additional_properties", {}).get("ph_value", 0),
                "Conductivity (S/cm)": coa_info.get("additional_properties", {}).get("conductivity", 0),
                "Impurities": coa_info.get("additional_properties", {}).get("impurities", ""),
                "Batch Number": coa_info.get("additional_properties", {}).get("batch_number", ""),
                "Manufacturing Date": coa_info.get("additional_properties", {}).get("manufacturing_date", ""),
                "Expiry Date": coa_info.get("additional_properties", {}).get("expiry_date", ""),
                "Storage Conditions": coa_info.get("additional_properties", {}).get("storage_conditions", ""),
                "Safety Data": coa_info.get("additional_properties", {}).get("safety_data", ""),
                "Certification": coa_info.get("additional_properties", {}).get("certification", "")
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def render_coa_management_page(self):
        """Render the main CoA management page"""
        st.title("📋 Certificate of Analysis (CoA) Management")
        
        # Sidebar for material selection and actions
        st.sidebar.header("CoA Management")
        
        # Material selection
        available_materials = self.get_available_materials()
        selected_material = st.sidebar.selectbox(
            "Select Material:",
            available_materials,
            format_func=lambda x: self.coa_data[x].get("material_name", x)
        )
        
        # Action selection
        action = st.sidebar.radio(
            "Choose Action:",
            ["View Unified Table", "Edit Material CoA", "Load PDF CoA", "Export CoA Data"]
        )
        
        if action == "View Unified Table":
            self._render_unified_table()
        elif action == "Edit Material CoA":
            self._render_editable_coa(selected_material)
        elif action == "Load PDF CoA":
            self._render_pdf_loader(selected_material)
        elif action == "Export CoA Data":
            self._render_export_options()
    
    def _render_unified_table(self):
        """Render unified CoA table"""
        st.markdown("### 📊 Unified CoA Table")
        st.markdown("Complete Certificate of Analysis data for all materials")
        
        # Create and display table
        df = self.create_unified_coa_table()
        
        # Add filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            material_type_filter = st.selectbox(
                "Filter by Type:",
                ["All"] + list(df["Type"].unique())
            )
        
        with col2:
            capacity_range = st.slider(
                "Theoretical Capacity Range:",
                min_value=float(df["Theoretical Capacity (mAh/g)"].min()),
                max_value=float(df["Theoretical Capacity (mAh/g)"].max()),
                value=(float(df["Theoretical Capacity (mAh/g)"].min()), 
                       float(df["Theoretical Capacity (mAh/g)"].max()))
            )
        
        with col3:
            show_columns = st.multiselect(
                "Select Columns to Display:",
                df.columns.tolist(),
                default=df.columns.tolist()[:10]  # Show first 10 columns by default
            )
        
        # Apply filters
        filtered_df = df.copy()
        
        if material_type_filter != "All":
            filtered_df = filtered_df[filtered_df["Type"] == material_type_filter]
        
        filtered_df = filtered_df[
            (filtered_df["Theoretical Capacity (mAh/g)"] >= capacity_range[0]) &
            (filtered_df["Theoretical Capacity (mAh/g)"] <= capacity_range[1])
        ]
        
        # Display filtered table
        if show_columns:
            filtered_df = filtered_df[show_columns]
        
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CoA Data as CSV",
            data=csv,
            file_name="coa_data.csv",
            mime="text/csv"
        )
    
    def _render_editable_coa(self, material_id: str):
        """Render editable CoA form for selected material"""
        st.markdown(f"### ✏️ Edit CoA: {self.coa_data[material_id].get('material_name', material_id)}")
        
        coa_info = self.get_material_coa(material_id)
        
        # Create tabs for different property categories
        tab1, tab2, tab3, tab4 = st.tabs(["Basic Properties", "Physical Properties", "Electrochemical Properties", "Additional Properties"])
        
        with tab1:
            st.markdown("#### Basic Material Properties")
            
            col1, col2 = st.columns(2)
            
            with col1:
                material_name = st.text_input(
                    "Material Name:",
                    value=coa_info.get("material_name", ""),
                    key=f"name_{material_id}"
                )
                
                material_type = st.selectbox(
                    "Material Type:",
                    ["anode", "cathode"],
                    index=0 if coa_info.get("material_type") == "anode" else 1,
                    key=f"type_{material_id}"
                )
            
            with col2:
                purity = st.text_input(
                    "Purity:",
                    value=coa_info.get("purity", ""),
                    key=f"purity_{material_id}"
                )
                
                theoretical_capacity = st.number_input(
                    "Theoretical Capacity (mAh/g):",
                    value=float(coa_info.get("theoretical_capacity", 0)),
                    key=f"capacity_{material_id}"
                )
        
        with tab2:
            st.markdown("#### Physical Properties")
            
            col1, col2 = st.columns(2)
            
            with col1:
                particle_size = st.number_input(
                    "Particle Size D50 (μm):",
                    value=float(coa_info.get("physical_properties", {}).get("particle_size_d50", 0)),
                    key=f"particle_size_{material_id}"
                )
                
                surface_area = st.number_input(
                    "Surface Area (m²/g):",
                    value=float(coa_info.get("physical_properties", {}).get("surface_area", 0)),
                    key=f"surface_area_{material_id}"
                )
            
            with col2:
                tap_density = st.number_input(
                    "Tap Density (g/cm³):",
                    value=float(coa_info.get("physical_properties", {}).get("tap_density", 0)),
                    key=f"tap_density_{material_id}"
                )
                
                true_density = st.number_input(
                    "True Density (g/cm³):",
                    value=float(coa_info.get("physical_properties", {}).get("true_density", 0)),
                    key=f"true_density_{material_id}"
                )
        
        with tab3:
            st.markdown("#### Electrochemical Properties")
            
            col1, col2 = st.columns(2)
            
            with col1:
                first_cycle_eff = st.number_input(
                    "First Cycle Efficiency (%):",
                    value=float(coa_info.get("electrochemical_properties", {}).get("first_cycle_efficiency", 0)),
                    key=f"first_cycle_{material_id}"
                )
                
                cycle_life = st.number_input(
                    "Cycle Life:",
                    value=float(coa_info.get("electrochemical_properties", {}).get("cycle_life", 0)),
                    key=f"cycle_life_{material_id}"
                )
            
            with col2:
                rate_capability = st.number_input(
                    "Rate Capability 2C (%):",
                    value=float(coa_info.get("electrochemical_properties", {}).get("rate_capability_2C", 0)),
                    key=f"rate_cap_{material_id}"
                )
                
                low_temp_perf = st.number_input(
                    "Low Temp Performance (%):",
                    value=float(coa_info.get("electrochemical_properties", {}).get("low_temp_performance", 0)),
                    key=f"low_temp_{material_id}"
                )
        
        with tab4:
            st.markdown("#### Additional Properties")
            
            col1, col2 = st.columns(2)
            
            with col1:
                moisture_content = st.number_input(
                    "Moisture Content (%):",
                    value=float(coa_info.get("additional_properties", {}).get("moisture_content", 0)),
                    key=f"moisture_{material_id}"
                )
                
                ph_value = st.number_input(
                    "pH Value:",
                    value=float(coa_info.get("additional_properties", {}).get("ph_value", 0)),
                    key=f"ph_{material_id}"
                )
                
                conductivity = st.number_input(
                    "Conductivity (S/cm):",
                    value=float(coa_info.get("additional_properties", {}).get("conductivity", 0)),
                    key=f"conductivity_{material_id}"
                )
                
                impurities = st.text_input(
                    "Impurities:",
                    value=coa_info.get("additional_properties", {}).get("impurities", ""),
                    key=f"impurities_{material_id}"
                )
            
            with col2:
                batch_number = st.text_input(
                    "Batch Number:",
                    value=coa_info.get("additional_properties", {}).get("batch_number", ""),
                    key=f"batch_{material_id}"
                )
                
                manufacturing_date = st.text_input(
                    "Manufacturing Date:",
                    value=coa_info.get("additional_properties", {}).get("manufacturing_date", ""),
                    key=f"manufacturing_{material_id}"
                )
                
                expiry_date = st.text_input(
                    "Expiry Date:",
                    value=coa_info.get("additional_properties", {}).get("expiry_date", ""),
                    key=f"expiry_{material_id}"
                )
                
                storage_conditions = st.text_input(
                    "Storage Conditions:",
                    value=coa_info.get("additional_properties", {}).get("storage_conditions", ""),
                    key=f"storage_{material_id}"
                )
        
        # Save button
        if st.button("💾 Save CoA Data", key=f"save_{material_id}"):
            # Update CoA data
            updated_data = {
                "material_name": material_name,
                "material_type": material_type,
                "purity": purity,
                "theoretical_capacity": theoretical_capacity,
                "physical_properties": {
                    "particle_size_d50": particle_size,
                    "surface_area": surface_area,
                    "tap_density": tap_density,
                    "true_density": true_density
                },
                "electrochemical_properties": {
                    "first_cycle_efficiency": first_cycle_eff,
                    "cycle_life": cycle_life,
                    "rate_capability_2C": rate_capability,
                    "low_temp_performance": low_temp_perf
                },
                "additional_properties": {
                    "moisture_content": moisture_content,
                    "ph_value": ph_value,
                    "conductivity": conductivity,
                    "impurities": impurities,
                    "batch_number": batch_number,
                    "manufacturing_date": manufacturing_date,
                    "expiry_date": expiry_date,
                    "storage_conditions": storage_conditions,
                    "safety_data": coa_info.get("additional_properties", {}).get("safety_data", ""),
                    "certification": coa_info.get("additional_properties", {}).get("certification", "")
                }
            }
            
            self.update_material_coa(material_id, updated_data)
            self.save_coa_data()
    
    def _render_pdf_loader(self, material_id: str):
        """Render PDF CoA loader"""
        st.markdown(f"### 📄 Load PDF CoA: {self.coa_data[material_id].get('material_name', material_id)}")
        
        st.markdown("#### Upload PDF CoA Document")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            key=f"pdf_upload_{material_id}"
        )
        
        if uploaded_file is not None:
            st.success(f"PDF uploaded: {uploaded_file.name}")
            
            # Display PDF info
            st.markdown("#### PDF Information")
            st.info("""
            **Note**: PDF parsing functionality would be implemented here to extract CoA data.
            This would typically involve:
            - PDF text extraction
            - Data parsing and validation
            - Automatic field mapping
            - Manual review and confirmation
            """)
            
            # Placeholder for PDF parsing results
            if st.button("🔍 Parse PDF CoA Data", key=f"parse_{material_id}"):
                st.warning("PDF parsing functionality not yet implemented. This would extract and populate CoA fields automatically.")
    
    def _render_export_options(self):
        """Render export options"""
        st.markdown("### 📤 Export CoA Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Export Formats")
            
            # JSON export
            if st.button("📄 Export as JSON"):
                json_data = json.dumps(self.coa_data, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name="coa_data.json",
                    mime="application/json"
                )
            
            # CSV export
            if st.button("📊 Export as CSV"):
                df = self.create_unified_coa_table()
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name="coa_data.csv",
                    mime="text/csv"
                )
        
        with col2:
            st.markdown("#### Export Options")
            
            # Material selection for individual export
            selected_materials = st.multiselect(
                "Select materials to export:",
                self.get_available_materials(),
                default=self.get_available_materials()
            )
            
            if st.button("📋 Export Selected Materials"):
                if selected_materials:
                    selected_data = {mat: self.coa_data[mat] for mat in selected_materials}
                    json_data = json.dumps(selected_data, indent=2)
                    st.download_button(
                        label="Download Selected Materials JSON",
                        data=json_data,
                        file_name="selected_coa_data.json",
                        mime="application/json"
                    )
                else:
                    st.warning("Please select at least one material to export.")


def render_coa_management_page():
    """Render the CoA management page"""
    coa_manager = COAManager()
    coa_manager.render_coa_management_page()
