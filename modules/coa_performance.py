"""
CoA (Certificate of Analysis) and Performance Plots Module
Provides CoA sheets and performance visualizations for battery materials
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import json
import os
from typing import Dict, List, Tuple, Optional
from .theme_colors import get_plotly_theme, get_current_theme


class CoAPerformanceManager:
    """Manages CoA sheets and performance plots for battery materials"""
    
    def __init__(self):
        self.plotly_theme = get_plotly_theme()[get_current_theme()]
        self.coa_file_path = "coa_data.json"
        self.coa_data = self._load_coa_data()
    
    def _load_coa_data(self) -> Dict:
        """Load CoA data from JSON file or initialize with defaults"""
        try:
            if os.path.exists(self.coa_file_path):
                with open(self.coa_file_path, 'r') as f:
                    return json.load(f)
            else:
                return self._get_default_coa_data()
        except Exception as e:
            st.error(f"Error loading CoA data: {e}")
            return self._get_default_coa_data()
    
    def _get_default_coa_data(self) -> Dict:
        """Get default CoA data"""
        return {
            'graphite': {
                'material_name': 'Synthetic Graphite',
                'grade': 'Battery Grade',
                'purity': '99.9%',
                'particle_size': 'D50: 15-20 μm',
                'specific_surface_area': '2-5 m²/g',
                'tap_density': '1.0-1.2 g/cm³',
                'moisture_content': '<0.1%',
                'ph_value': '6.5-7.5',
                'impurities': {
                    'Fe': '<50 ppm',
                    'Ni': '<20 ppm',
                    'Co': '<10 ppm',
                    'Cu': '<10 ppm',
                    'Al': '<20 ppm',
                    'Si': '<100 ppm'
                },
                'electrochemical_properties': {
                    'first_cycle_efficiency': '85-90%',
                    'capacity_retention_100_cycles': '>95%',
                    'rate_capability_2C': '>80%',
                    'low_temperature_performance': '>70% at -20°C'
                }
            },
            'nmc811': {
                'material_name': 'LiNi0.8Mn0.1Co0.1O2',
                'grade': 'Battery Grade',
                'purity': '99.5%',
                'particle_size': 'D50: 8-12 μm',
                'specific_surface_area': '0.3-0.8 m²/g',
                'tap_density': '2.2-2.5 g/cm³',
                'moisture_content': '<0.2%',
                'ph_value': '11.0-12.0',
                'impurities': {
                    'Fe': '<100 ppm',
                    'Na': '<50 ppm',
                    'K': '<50 ppm',
                    'Ca': '<100 ppm',
                    'Mg': '<50 ppm',
                    'Al': '<200 ppm'
                },
                'electrochemical_properties': {
                    'first_cycle_efficiency': '88-92%',
                    'capacity_retention_100_cycles': '>90%',
                    'rate_capability_2C': '>85%',
                    'low_temperature_performance': '>75% at -20°C'
                }
            },
            'lfp': {
                'material_name': 'LiFePO4',
                'grade': 'Battery Grade',
                'purity': '99.0%',
                'particle_size': 'D50: 1-3 μm',
                'specific_surface_area': '10-20 m²/g',
                'tap_density': '1.2-1.5 g/cm³',
                'moisture_content': '<0.3%',
                'ph_value': '8.0-9.0',
                'impurities': {
                    'Fe': '<500 ppm',
                    'Na': '<100 ppm',
                    'K': '<100 ppm',
                    'Ca': '<200 ppm',
                    'Mg': '<100 ppm',
                    'Al': '<300 ppm'
                },
                'electrochemical_properties': {
                    'first_cycle_efficiency': '95-98%',
                    'capacity_retention_100_cycles': '>98%',
                    'rate_capability_2C': '>90%',
                    'low_temperature_performance': '>80% at -20°C'
                }
            }
        }
    
    def save_coa_data(self):
        """Save CoA data to JSON file"""
        try:
            with open(self.coa_file_path, 'w') as f:
                json.dump(self.coa_data, f, indent=2)
            st.success("CoA data saved successfully!")
        except Exception as e:
            st.error(f"Error saving CoA data: {e}")
    
    def render_pdf_upload(self, material: str) -> None:
        """Render PDF upload interface"""
        st.markdown("#### 📄 Upload PDF CoA")
        
        uploaded_file = st.file_uploader(
            f"Upload CoA PDF for {material}",
            type="pdf",
            key=f"pdf_upload_{material}"
        )
        
        if uploaded_file is not None:
            st.success(f"PDF uploaded: {uploaded_file.name}")
            
            # Display PDF info
            st.info("""
            **PDF Uploaded Successfully!**
            
            **Next Steps:**
            - PDF parsing functionality would extract CoA data automatically
            - Review and confirm extracted values
            - Save to material database
            
            **Note**: PDF parsing is a placeholder for future implementation.
            """)
            
            # Placeholder for PDF parsing
            if st.button("🔍 Parse PDF Data", key=f"parse_{material}"):
                st.warning("PDF parsing functionality not yet implemented. This would extract and populate CoA fields automatically.")
    
    def render_editable_coa(self, material: str) -> None:
        """Render editable CoA form"""
        st.markdown("#### ✏️ Edit CoA Data")
        
        if material not in self.coa_data:
            st.error(f"No CoA data found for {material}")
            return
        
        coa = self.coa_data[material]
        
        # Create tabs for different property categories
        tab1, tab2, tab3 = st.tabs(["Basic Properties", "Physical Properties", "Electrochemical Properties"])
        
        with tab1:
            st.markdown("##### Basic Material Properties")
            
            col1, col2 = st.columns(2)
            
            with col1:
                material_name = st.text_input(
                    "Material Name:",
                    value=coa.get('material_name', ''),
                    key=f"name_{material}"
                )
                
                grade = st.text_input(
                    "Grade:",
                    value=coa.get('grade', ''),
                    key=f"grade_{material}"
                )
            
            with col2:
                purity = st.text_input(
                    "Purity:",
                    value=coa.get('purity', ''),
                    key=f"purity_{material}"
                )
                
                batch_no = st.text_input(
                    "Batch Number:",
                    value=str(np.random.randint(100000, 999999)),
                    key=f"batch_{material}"
                )
        
        with tab2:
            st.markdown("##### Physical Properties")
            
            col1, col2 = st.columns(2)
            
            with col1:
                particle_size = st.text_input(
                    "Particle Size:",
                    value=coa.get('particle_size', ''),
                    key=f"particle_size_{material}"
                )
                
                surface_area = st.text_input(
                    "Surface Area:",
                    value=coa.get('specific_surface_area', ''),
                    key=f"surface_area_{material}"
                )
            
            with col2:
                tap_density = st.text_input(
                    "Tap Density:",
                    value=coa.get('tap_density', ''),
                    key=f"tap_density_{material}"
                )
                
                moisture_content = st.text_input(
                    "Moisture Content:",
                    value=coa.get('moisture_content', ''),
                    key=f"moisture_{material}"
                )
        
        with tab3:
            st.markdown("##### Electrochemical Properties")
            
            col1, col2 = st.columns(2)
            
            with col1:
                first_cycle_eff = st.text_input(
                    "First Cycle Efficiency:",
                    value=coa.get('electrochemical_properties', {}).get('first_cycle_efficiency', ''),
                    key=f"first_cycle_{material}"
                )
                
                capacity_retention = st.text_input(
                    "Capacity Retention (100 cycles):",
                    value=coa.get('electrochemical_properties', {}).get('capacity_retention_100_cycles', ''),
                    key=f"capacity_ret_{material}"
                )
            
            with col2:
                rate_capability = st.text_input(
                    "Rate Capability (2C):",
                    value=coa.get('electrochemical_properties', {}).get('rate_capability_2C', ''),
                    key=f"rate_cap_{material}"
                )
                
                low_temp_perf = st.text_input(
                    "Low Temp Performance:",
                    value=coa.get('electrochemical_properties', {}).get('low_temperature_performance', ''),
                    key=f"low_temp_{material}"
                )
        
        # Save button
        if st.button("💾 Save CoA Data", key=f"save_{material}"):
            # Update CoA data
            updated_coa = {
                'material_name': material_name,
                'grade': grade,
                'purity': purity,
                'particle_size': particle_size,
                'specific_surface_area': surface_area,
                'tap_density': tap_density,
                'moisture_content': moisture_content,
                'ph_value': coa.get('ph_value', ''),
                'impurities': coa.get('impurities', {}),
                'electrochemical_properties': {
                    'first_cycle_efficiency': first_cycle_eff,
                    'capacity_retention_100_cycles': capacity_retention,
                    'rate_capability_2C': rate_capability,
                    'low_temperature_performance': low_temp_perf
                }
            }
            
            self.coa_data[material] = updated_coa
            self.save_coa_data()
            st.rerun()
    
    def render_coa_sheet(self, material: str) -> None:
        """Render Certificate of Analysis sheet in unified table format"""
        
        if material not in self.coa_data:
            st.error(f"CoA data not available for {material}")
            return
        
        coa = self.coa_data[material]
        
        st.markdown("### 📋 Certificate of Analysis (CoA)")
        
        # Material header
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**Material**: {coa['material_name']}")
            st.markdown(f"**Grade**: {coa['grade']}")
            st.markdown(f"**Purity**: {coa['purity']}")
        
        with col2:
            st.markdown(f"**Batch No.**: {np.random.randint(100000, 999999)}")
            st.markdown(f"**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d')}")
            st.markdown(f"**Valid Until**: {(pd.Timestamp.now() + pd.Timedelta(days=365)).strftime('%Y-%m-%d')}")
        
        # Create comprehensive CoA table
        st.markdown("#### Complete CoA Data Table")
        
        # Prepare data for the table
        coa_table_data = []
        
        # Basic Properties
        coa_table_data.extend([
            {"Category": "Basic Properties", "Property": "Material Name", "Value": coa.get('material_name', 'N/A'), "Unit": ""},
            {"Category": "Basic Properties", "Property": "Grade", "Value": coa.get('grade', 'N/A'), "Unit": ""},
            {"Category": "Basic Properties", "Property": "Purity", "Value": coa.get('purity', 'N/A'), "Unit": ""},
            {"Category": "Basic Properties", "Property": "Batch Number", "Value": str(np.random.randint(100000, 999999)), "Unit": ""},
            {"Category": "Basic Properties", "Property": "Manufacturing Date", "Value": pd.Timestamp.now().strftime('%Y-%m-%d'), "Unit": ""},
            {"Category": "Basic Properties", "Property": "Expiry Date", "Value": (pd.Timestamp.now() + pd.Timedelta(days=365)).strftime('%Y-%m-%d'), "Unit": ""}
        ])
        
        # Physical Properties
        coa_table_data.extend([
            {"Category": "Physical Properties", "Property": "Particle Size (D50)", "Value": coa.get('particle_size', 'N/A'), "Unit": "μm"},
            {"Category": "Physical Properties", "Property": "Specific Surface Area", "Value": coa.get('specific_surface_area', 'N/A'), "Unit": "m²/g"},
            {"Category": "Physical Properties", "Property": "Tap Density", "Value": coa.get('tap_density', 'N/A'), "Unit": "g/cm³"},
            {"Category": "Physical Properties", "Property": "True Density", "Value": coa.get('true_density', 'N/A'), "Unit": "g/cm³"},
            {"Category": "Physical Properties", "Property": "Moisture Content", "Value": coa.get('moisture_content', 'N/A'), "Unit": "%"},
            {"Category": "Physical Properties", "Property": "pH Value", "Value": coa.get('ph_value', 'N/A'), "Unit": ""},
            {"Category": "Physical Properties", "Property": "Particle Shape", "Value": "Spherical", "Unit": ""},
            {"Category": "Physical Properties", "Property": "Crystallinity", "Value": ">95%", "Unit": "%"}
        ])
        
        # Electrochemical Properties
        electrochem_props = coa.get('electrochemical_properties', {})
        coa_table_data.extend([
            {"Category": "Electrochemical Properties", "Property": "Theoretical Capacity", "Value": self._get_theoretical_capacity(material), "Unit": "mAh/g"},
            {"Category": "Electrochemical Properties", "Property": "First Cycle Efficiency", "Value": electrochem_props.get('first_cycle_efficiency', 'N/A'), "Unit": "%"},
            {"Category": "Electrochemical Properties", "Property": "Capacity Retention (100 cycles)", "Value": electrochem_props.get('capacity_retention_100_cycles', 'N/A'), "Unit": "%"},
            {"Category": "Electrochemical Properties", "Property": "Rate Capability (2C)", "Value": electrochem_props.get('rate_capability_2C', 'N/A'), "Unit": "%"},
            {"Category": "Electrochemical Properties", "Property": "Low Temperature Performance", "Value": electrochem_props.get('low_temperature_performance', 'N/A'), "Unit": "%"},
            {"Category": "Electrochemical Properties", "Property": "Nominal Voltage", "Value": self._get_nominal_voltage(material), "Unit": "V"},
            {"Category": "Electrochemical Properties", "Property": "Energy Density", "Value": self._get_energy_density(material), "Unit": "Wh/kg"},
            {"Category": "Electrochemical Properties", "Property": "Cycle Life", "Value": self._get_cycle_life(material), "Unit": "cycles"}
        ])
        
        # Impurities
        impurities = coa.get('impurities', {})
        for element, content in impurities.items():
            coa_table_data.append({
                "Category": "Impurity Analysis", 
                "Property": f"{element} Content", 
                "Value": content, 
                "Unit": "ppm"
            })
        
        # Additional Properties
        coa_table_data.extend([
            {"Category": "Additional Properties", "Property": "Storage Conditions", "Value": "Room temperature, dry", "Unit": ""},
            {"Category": "Additional Properties", "Property": "Safety Classification", "Value": "Non-hazardous", "Unit": ""},
            {"Category": "Additional Properties", "Property": "Certification", "Value": "ISO 9001:2015", "Unit": ""},
            {"Category": "Additional Properties", "Property": "Test Standards", "Value": "IEC 62660, UL 1642", "Unit": ""},
            {"Category": "Additional Properties", "Property": "Quality Status", "Value": "✅ Within specification", "Unit": ""}
        ])
        
        # Create DataFrame and display
        coa_df = pd.DataFrame(coa_table_data)
        
        # Display the complete table with merged category rows
        st.dataframe(
            coa_df,
            use_container_width=True,
            height=500,
            column_config={
                "Category": st.column_config.TextColumn("Category", width="medium"),
                "Property": st.column_config.TextColumn("Property", width="large"),
                "Value": st.column_config.TextColumn("Value", width="medium"),
                "Unit": st.column_config.TextColumn("Unit", width="small")
            },
            hide_index=True
        )
        
        # Add custom CSS for merged category rows and vertical alignment
        st.markdown("""
        <style>
        .stDataFrame {
            font-size: 14px;
        }
        .stDataFrame th {
            background-color: #f0f2f6 !important;
            font-weight: bold !important;
            text-align: center !important;
            vertical-align: middle !important;
        }
        .stDataFrame td {
            vertical-align: middle !important;
            padding: 8px !important;
        }
        .stDataFrame tr:nth-child(even) {
            background-color: #f8f9fa !important;
        }
        .stDataFrame tr:nth-child(odd) {
            background-color: #ffffff !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Download button
        csv = coa_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CoA Data as CSV",
            data=csv,
            file_name=f"coa_{material}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    def _get_theoretical_capacity(self, material: str) -> str:
        """Get theoretical capacity for material"""
        capacities = {
            'graphite': '372',
            'lto': '175',
            'silicon': '4200',
            'graphite_sio2': '450',
            'nmc811': '200',
            'lfp': '170',
            'nca': '200',
            'nmc532': '180',
            'lco': '140'
        }
        return capacities.get(material, 'N/A')
    
    def _get_nominal_voltage(self, material: str) -> str:
        """Get nominal voltage for material"""
        voltages = {
            'graphite': '0.1',
            'lto': '1.5',
            'silicon': '0.3',
            'graphite_sio2': '0.2',
            'nmc811': '3.8',
            'lfp': '3.4',
            'nca': '3.7',
            'nmc532': '3.7',
            'lco': '3.9'
        }
        return voltages.get(material, 'N/A')
    
    def _get_energy_density(self, material: str) -> str:
        """Get energy density for material"""
        energy_densities = {
            'graphite': '37',
            'lto': '263',
            'silicon': '1260',
            'graphite_sio2': '90',
            'nmc811': '760',
            'lfp': '578',
            'nca': '740',
            'nmc532': '666',
            'lco': '546'
        }
        return energy_densities.get(material, 'N/A')
    
    def _get_cycle_life(self, material: str) -> str:
        """Get cycle life for material"""
        cycle_lives = {
            'graphite': '1000+',
            'lto': '10000+',
            'silicon': '200+',
            'graphite_sio2': '800+',
            'nmc811': '500+',
            'lfp': '2000+',
            'nca': '400+',
            'nmc532': '600+',
            'lco': '300+'
        }
        return cycle_lives.get(material, 'N/A')
    
    def render_performance_plots(self, material: str) -> None:
        """Render performance plots for the material"""
        
        st.markdown("### 📊 Performance Analysis")
        
        # Create tabs for different performance metrics
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Cycle Life", "Rate Capability", "Temperature", "OCV Curve", "GITT", "EIS"])
        
        with tab1:
            self._render_cycle_life_plot(material)
        
        with tab2:
            self._render_rate_capability_plot(material)
        
        with tab3:
            self._render_temperature_plot(material)
        
        with tab4:
            self._render_ocv_plot(material)
        
        with tab5:
            self._render_gitt_plot(material)
        
        with tab6:
            self._render_eis_plot(material)
    
    def _render_cycle_life_plot(self, material: str) -> None:
        """Render cycle life performance plot"""
        
        # Generate realistic cycle life data
        cycles = np.arange(0, 501, 10)
        
        if material == 'graphite':
            # Graphite shows good cycle life
            capacity_retention = 100 - 0.02 * cycles + np.random.normal(0, 0.5, len(cycles))
            capacity_retention = np.clip(capacity_retention, 80, 100)
        elif material == 'nmc811':
            # NMC811 shows moderate degradation
            capacity_retention = 100 - 0.05 * cycles + np.random.normal(0, 1, len(cycles))
            capacity_retention = np.clip(capacity_retention, 70, 100)
        else:  # LFP
            # LFP shows excellent cycle life
            capacity_retention = 100 - 0.01 * cycles + np.random.normal(0, 0.3, len(cycles))
            capacity_retention = np.clip(capacity_retention, 90, 100)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=cycles,
            y=capacity_retention,
            mode='lines+markers',
            name='Capacity Retention',
            line=dict(color='#2ecc71', width=3),
            marker=dict(size=4)
        ))
        
        # Add degradation rate line
        if len(cycles) > 1:
            degradation_rate = (capacity_retention[-1] - capacity_retention[0]) / (cycles[-1] - cycles[0])
            fig.add_annotation(
                x=cycles[-1] * 0.7,
                y=capacity_retention[-1] * 0.8,
                text=f"Degradation Rate: {degradation_rate:.3f}%/cycle",
                showarrow=True,
                arrowhead=2,
                arrowcolor="red"
            )
        
        fig.update_layout(
            title="Cycle Life Performance",
            xaxis_title="Cycle Number",
            yaxis_title="Capacity Retention (%)",
            height=400,
            **self.plotly_theme['layout']
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_rate_capability_plot(self, material: str) -> None:
        """Render rate capability performance plot"""
        
        # Generate rate capability data
        rates = np.array([0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 5.0])
        
        if material == 'graphite':
            # Graphite has good rate capability
            capacity_retention = 100 - 5 * rates + np.random.normal(0, 2, len(rates))
            capacity_retention = np.clip(capacity_retention, 60, 100)
        elif material == 'nmc811':
            # NMC811 has moderate rate capability
            capacity_retention = 100 - 8 * rates + np.random.normal(0, 3, len(rates))
            capacity_retention = np.clip(capacity_retention, 50, 100)
        else:  # LFP
            # LFP has excellent rate capability
            capacity_retention = 100 - 3 * rates + np.random.normal(0, 1, len(rates))
            capacity_retention = np.clip(capacity_retention, 70, 100)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=rates,
            y=capacity_retention,
            mode='lines+markers',
            name='Capacity Retention',
            line=dict(color='#3498db', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Rate Capability Performance",
            xaxis_title="C-Rate",
            yaxis_title="Capacity Retention (%)",
            height=400,
            **self.plotly_theme['layout']
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_temperature_plot(self, material: str) -> None:
        """Render temperature performance plot"""
        
        # Generate temperature data
        temperatures = np.array([-20, -10, 0, 10, 25, 40, 50, 60])
        
        if material == 'graphite':
            # Graphite performance drops at low temperatures
            capacity_retention = 100 - 0.5 * (25 - temperatures) + np.random.normal(0, 2, len(temperatures))
            capacity_retention = np.clip(capacity_retention, 60, 100)
        elif material == 'nmc811':
            # NMC811 has good temperature stability
            capacity_retention = 100 - 0.3 * np.abs(temperatures - 25) + np.random.normal(0, 1.5, len(temperatures))
            capacity_retention = np.clip(capacity_retention, 70, 100)
        else:  # LFP
            # LFP has excellent temperature stability
            capacity_retention = 100 - 0.2 * np.abs(temperatures - 25) + np.random.normal(0, 1, len(temperatures))
            capacity_retention = np.clip(capacity_retention, 80, 100)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=temperatures,
            y=capacity_retention,
            mode='lines+markers',
            name='Capacity Retention',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=8)
        ))
        
        # Add reference line at 25°C
        fig.add_hline(y=100, line_dash="dash", line_color="gray", 
                     annotation_text="Reference (25°C)")
        
        fig.update_layout(
            title="Temperature Performance",
            xaxis_title="Temperature (°C)",
            yaxis_title="Capacity Retention (%)",
            height=400,
            **self.plotly_theme['layout']
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_ocv_plot(self, material: str) -> None:
        """Render OCV curve plot"""
        
        # Import OCV generator
        from .ocv_curves import OCVCurveGenerator
        
        ocv_gen = OCVCurveGenerator()
        
        # Generate OCV curve from database
        capacity, voltage = ocv_gen.generate_ocv_from_database(material, 25.0)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=capacity,
            y=voltage,
            mode='lines',
            name='OCV Curve',
            line=dict(color='#9b59b6', width=3)
        ))
        
        fig.update_layout(
            title="Open Circuit Voltage Curve",
            xaxis_title="Capacity (mAh/g)",
            yaxis_title="Voltage vs Li/Li+ (V)",
            height=400,
            **self.plotly_theme['layout']
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_gitt_plot(self, material: str) -> None:
        """Render GITT (Galvanostatic Intermittent Titration Technique) plot"""
        
        st.markdown("#### GITT Analysis")
        
        # Generate realistic GITT data
        time_points = np.linspace(0, 100, 1000)
        
        if material in ['graphite', 'lto', 'silicon', 'graphite_sio2']:
            # Anode materials - lower voltage range
            base_voltage = 0.1 if material == 'graphite' else (1.5 if material == 'lto' else 0.3)
            voltage = base_voltage + 0.1 * np.sin(2 * np.pi * time_points / 20) + np.random.normal(0, 0.01, len(time_points))
        else:
            # Cathode materials - higher voltage range
            base_voltage = 3.4 if material == 'lfp' else 3.8
            voltage = base_voltage + 0.2 * np.sin(2 * np.pi * time_points / 25) + np.random.normal(0, 0.02, len(time_points))
        
        # Create GITT plot
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=time_points,
            y=voltage,
            mode='lines',
            name='GITT Voltage Profile',
            line=dict(color='#e67e22', width=2)
        ))
        
        # Add current pulse indicators
        pulse_times = np.arange(0, 100, 10)
        for pulse_time in pulse_times:
            fig.add_vline(x=pulse_time, line_dash="dash", line_color="red", opacity=0.3)
        
        fig.update_layout(
            title="GITT (Galvanostatic Intermittent Titration Technique)",
            xaxis_title="Time (hours)",
            yaxis_title="Voltage vs Li/Li+ (V)",
            height=400,
            **self.plotly_theme['layout']
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # GITT parameters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Diffusion Coefficient", "1.2 × 10⁻¹⁰", "cm²/s")
        
        with col2:
            st.metric("Equilibrium Time", "2.5", "hours")
        
        with col3:
            st.metric("Pulse Duration", "0.5", "hours")
    
    def _render_eis_plot(self, material: str) -> None:
        """Render EIS (Electrochemical Impedance Spectroscopy) plot"""
        
        st.markdown("#### EIS Analysis")
        
        # Generate realistic EIS data (Nyquist plot)
        frequencies = np.logspace(-2, 4, 100)  # 0.01 Hz to 10 kHz
        
        if material in ['graphite', 'lto', 'silicon', 'graphite_sio2']:
            # Anode materials - different impedance characteristics
            if material == 'graphite':
                R_s = 2.5  # Series resistance
                R_ct = 15.0  # Charge transfer resistance
                C_dl = 1e-4  # Double layer capacitance
            elif material == 'lto':
                R_s = 1.8
                R_ct = 8.0
                C_dl = 2e-4
            elif material == 'silicon':
                R_s = 3.2
                R_ct = 25.0
                C_dl = 5e-5
            else:  # graphite_sio2
                R_s = 2.8
                R_ct = 18.0
                C_dl = 8e-5
        else:
            # Cathode materials
            if material == 'lfp':
                R_s = 1.5
                R_ct = 12.0
                C_dl = 1.5e-4
            elif material == 'nmc811':
                R_s = 2.0
                R_ct = 20.0
                C_dl = 1e-4
            elif material == 'nca':
                R_s = 1.8
                R_ct = 18.0
                C_dl = 1.2e-4
            else:  # nmc532, lco
                R_s = 1.7
                R_ct = 16.0
                C_dl = 1.1e-4
        
        # Calculate impedance (simplified Randles circuit)
        omega = 2 * np.pi * frequencies
        Z_real = R_s + R_ct / (1 + (omega * R_ct * C_dl)**2)
        Z_imag = (omega * R_ct**2 * C_dl) / (1 + (omega * R_ct * C_dl)**2)  # Positive imaginary for -Imaginary plot
        
        # Add some noise for realism
        Z_real += np.random.normal(0, 0.1, len(Z_real))
        Z_imag += np.random.normal(0, 0.1, len(Z_imag))
        
        # Create Nyquist plot
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=Z_real,
            y=Z_imag,
            mode='lines+markers',
            name='EIS Nyquist Plot',
            line=dict(color='#8e44ad', width=2),
            marker=dict(size=4)
        ))
        
        # Add frequency annotations at key points
        key_indices = [0, 25, 50, 75, 99]
        for idx in key_indices:
            fig.add_annotation(
                x=Z_real[idx],
                y=Z_imag[idx],
                text=f"{frequencies[idx]:.2f} Hz",
                showarrow=True,
                arrowhead=2,
                arrowcolor="red",
                font=dict(size=10)
            )
        
        fig.update_layout(
            title="EIS Nyquist Plot (Electrochemical Impedance Spectroscopy)",
            xaxis_title="Z' (Real Impedance) / Ω",
            yaxis_title="-Z'' (Imaginary Impedance) / Ω",
            height=400,
            **self.plotly_theme['layout']
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # EIS parameters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Series Resistance (Rₛ)", f"{R_s:.1f}", "Ω")
        
        with col2:
            st.metric("Charge Transfer (Rct)", f"{R_ct:.1f}", "Ω")
        
        with col3:
            st.metric("Double Layer (Cdl)", f"{C_dl*1e6:.1f}", "μF")
        
        with col4:
            st.metric("Warburg Coefficient", "0.8", "Ω·s⁻⁰·⁵")
        
        # Bode plot
        st.markdown("##### Bode Plot")
        
        # Calculate magnitude and phase
        Z_magnitude = np.sqrt(Z_real**2 + Z_imag**2)
        Z_phase = np.arctan2(Z_imag, Z_real) * 180 / np.pi
        
        # Create subplots for Bode plot
        from plotly.subplots import make_subplots
        
        fig_bode = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Impedance Magnitude", "Phase Angle"),
            vertical_spacing=0.1
        )
        
        # Magnitude plot
        fig_bode.add_trace(
            go.Scatter(
                x=frequencies,
                y=Z_magnitude,
                mode='lines',
                name='|Z|',
                line=dict(color='#27ae60', width=2)
            ),
            row=1, col=1
        )
        
        # Phase plot
        fig_bode.add_trace(
            go.Scatter(
                x=frequencies,
                y=Z_phase,
                mode='lines',
                name='Phase',
                line=dict(color='#e74c3c', width=2)
            ),
            row=2, col=1
        )
        
        fig_bode.update_xaxes(title_text="Frequency (Hz)", type="log", row=2, col=1)
        fig_bode.update_yaxes(title_text="|Z| (Ω)", type="log", row=1, col=1)
        fig_bode.update_yaxes(title_text="Phase (°)", row=2, col=1)
        
        fig_bode.update_layout(
            title="EIS Bode Plot",
            height=500,
            showlegend=False,
            **self.plotly_theme['layout']
        )
        
        st.plotly_chart(fig_bode, use_container_width=True)


def render_anode_page():
    """Render anode materials page with CoA and performance plots"""
    
    st.markdown("### ⚡ Anode Materials Analysis")
    
    # Material selection
    material = st.selectbox(
        "Select Anode Material:",
        ["graphite", "lto", "silicon", "graphite_sio2"],
        format_func=lambda x: {
            "graphite": "Graphite (C)",
            "lto": "LTO (Li4Ti5O12)",
            "silicon": "Silicon (Si)",
            "graphite_sio2": "Graphite + SiO2 Composite"
        }[x]
    )
    
    # Initialize CoA and Performance manager
    coa_perf = CoAPerformanceManager()
    
    # CoA Management Section
    st.markdown("#### 📋 CoA Management")
    
    # Action selection
    coa_action = st.radio(
        "Choose CoA Action:",
        ["View CoA Sheet", "Edit CoA Data", "Upload PDF CoA"],
        horizontal=True,
        key=f"coa_action_{material}"
    )
    
    # Create two-column layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # CoA management on the left
        if coa_action == "View CoA Sheet":
            coa_perf.render_coa_sheet(material)
        elif coa_action == "Edit CoA Data":
            coa_perf.render_editable_coa(material)
        elif coa_action == "Upload PDF CoA":
            coa_perf.render_pdf_upload(material)
    
    with col2:
        # Performance plots on the right
        coa_perf.render_performance_plots(material)
    
    # Back button
    if st.button("← Back to Home", key="back_to_home_anode"):
        st.session_state.current_page = 'home'
        st.rerun()


def render_cathode_page():
    """Render cathode materials page with CoA and performance plots"""
    
    st.markdown("### ⚡ Cathode Materials Analysis")
    
    # Material selection
    material = st.selectbox(
        "Select Cathode Material:",
        ["nmc811", "lfp", "nca", "nmc532", "lco"],
        format_func=lambda x: {
            "nmc811": "NMC811 (LiNi0.8Mn0.1Co0.1O2)",
            "lfp": "LFP (LiFePO4)",
            "nca": "NCA (LiNi0.8Co0.15Al0.05O2)",
            "nmc532": "NMC532 (LiNi0.5Mn0.3Co0.2O2)",
            "lco": "LCO (LiCoO2)"
        }[x]
    )
    
    # Initialize CoA and Performance manager
    coa_perf = CoAPerformanceManager()
    
    # CoA Management Section
    st.markdown("#### 📋 CoA Management")
    
    # Action selection
    coa_action = st.radio(
        "Choose CoA Action:",
        ["View CoA Sheet", "Edit CoA Data", "Upload PDF CoA"],
        horizontal=True,
        key=f"coa_action_{material}"
    )
    
    # Create two-column layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # CoA management on the left
        if coa_action == "View CoA Sheet":
            coa_perf.render_coa_sheet(material)
        elif coa_action == "Edit CoA Data":
            coa_perf.render_editable_coa(material)
        elif coa_action == "Upload PDF CoA":
            coa_perf.render_pdf_upload(material)
    
    with col2:
        # Performance plots on the right
        coa_perf.render_performance_plots(material)
    
    # Back button
    if st.button("← Back to Home", key="back_to_home_cathode"):
        st.session_state.current_page = 'home'
        st.rerun()
