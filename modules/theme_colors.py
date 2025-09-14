"""
Theme Colors Module for Cell Development Platform
Provides color schemes that work well in both dark and light modes
"""

# Color palette optimized for both dark and light themes
COLORS = {
    # Primary brand colors - work well in both themes
    "primary": {
        "50": "#f0f4ff",   # Very light blue
        "100": "#e0e9ff",  # Light blue
        "200": "#c7d6ff",  # Lighter blue
        "300": "#a5b8ff",  # Light blue
        "400": "#8b9cff",  # Medium light blue
        "500": "#667eea",  # Primary blue
        "600": "#5a6fd8",  # Medium blue
        "700": "#4c5bc6",  # Darker blue
        "800": "#3f4bb3",  # Dark blue
        "900": "#2a3d8c",  # Very dark blue
    },
    
    # Secondary colors - purple gradient
    "secondary": {
        "50": "#faf5ff",   # Very light purple
        "100": "#f3e8ff",  # Light purple
        "200": "#e9d5ff",  # Lighter purple
        "300": "#d8b4fe",  # Light purple
        "400": "#c084fc",  # Medium light purple
        "500": "#764ba2",  # Primary purple
        "600": "#6b4190",  # Medium purple
        "700": "#5f377e",  # Darker purple
        "800": "#532d6c",  # Dark purple
        "900": "#3d1f4f",  # Very dark purple
    },
    
    # Accent colors
    "accent": {
        "green": "#10b981",    # Success green
        "red": "#ef4444",      # Error red
        "yellow": "#f59e0b",   # Warning yellow
        "blue": "#3b82f6",     # Info blue
        "purple": "#8b5cf6",   # Purple accent
        "orange": "#f97316",   # Orange accent
    },
    
    # Neutral colors - theme-aware
    "neutral": {
        "white": "#ffffff",
        "black": "#000000",
        "gray": {
            "50": "#f9fafb",   # Very light gray
            "100": "#f3f4f6",  # Light gray
            "200": "#e5e7eb",  # Lighter gray
            "300": "#d1d5db",  # Light gray
            "400": "#9ca3af",  # Medium light gray
            "500": "#6b7280",  # Medium gray
            "600": "#4b5563",  # Medium dark gray
            "700": "#374151",  # Dark gray
            "800": "#1f2937",  # Darker gray
            "900": "#111827",  # Very dark gray
        }
    },
    
    # Background colors - theme-aware
    "background": {
        "light": {
            "primary": "#ffffff",
            "secondary": "#f8fafc",
            "tertiary": "#f1f5f9",
            "card": "#ffffff",
            "overlay": "rgba(0, 0, 0, 0.1)",
        },
        "dark": {
            "primary": "#0f172a",      # Very dark blue-gray
            "secondary": "#1e293b",    # Dark blue-gray
            "tertiary": "#334155",     # Medium dark blue-gray
            "card": "#1e293b",         # Card background
            "overlay": "rgba(255, 255, 255, 0.1)",
        }
    },
    
    # Text colors - theme-aware
    "text": {
        "light": {
            "primary": "#1f2937",      # Dark gray
            "secondary": "#4b5563",    # Medium gray
            "tertiary": "#6b7280",     # Light gray
            "inverse": "#ffffff",      # White text
        },
        "dark": {
            "primary": "#f8fafc",      # Light gray
            "secondary": "#cbd5e1",    # Medium light gray
            "tertiary": "#94a3b8",     # Light gray
            "inverse": "#1f2937",      # Dark text
        }
    },
    
    # Border colors - theme-aware
    "border": {
        "light": {
            "primary": "#e5e7eb",      # Light gray
            "secondary": "#d1d5db",    # Medium light gray
            "focus": "#667eea",        # Primary blue
        },
        "dark": {
            "primary": "#334155",      # Medium dark gray
            "secondary": "#475569",    # Dark gray
            "focus": "#8b5cf6",        # Purple accent
        }
    }
}

# CSS variables for theme switching
def get_theme_css():
    """Generate CSS with CSS variables for theme switching"""
    return """
    :root {
        /* Light theme colors */
        --color-primary: #667eea;
        --color-primary-hover: #5a6fd8;
        --color-secondary: #764ba2;
        --color-secondary-hover: #6b4190;
        
        --color-success: #10b981;
        --color-error: #ef4444;
        --color-warning: #f59e0b;
        --color-info: #3b82f6;
        
        --color-background-primary: #ffffff;
        --color-background-secondary: #f8fafc;
        --color-background-tertiary: #f1f5f9;
        --color-background-card: #ffffff;
        
        --color-text-primary: #1f2937;
        --color-text-secondary: #4b5563;
        --color-text-tertiary: #6b7280;
        --color-text-inverse: #ffffff;
        
        --color-border-primary: #e5e7eb;
        --color-border-secondary: #d1d5db;
        --color-border-focus: #667eea;
        
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    /* Dark theme colors */
    @media (prefers-color-scheme: dark) {
        :root {
            --color-primary: #8b5cf6;
            --color-primary-hover: #7c3aed;
            --color-secondary: #a855f7;
            --color-secondary-hover: #9333ea;
            
            --color-success: #10b981;
            --color-error: #ef4444;
            --color-warning: #f59e0b;
            --color-info: #3b82f6;
            
            --color-background-primary: #0f172a;
            --color-background-secondary: #1e293b;
            --color-background-tertiary: #334155;
            --color-background-card: #1e293b;
            
            --color-text-primary: #f8fafc;
            --color-text-secondary: #cbd5e1;
            --color-text-tertiary: #94a3b8;
            --color-text-inverse: #1f2937;
            
            --color-border-primary: #334155;
            --color-border-secondary: #475569;
            --color-border-focus: #8b5cf6;
            
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.3);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.3);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 10px 10px -5px rgba(0, 0, 0, 0.3);
        }
    }
    
    /* Streamlit dark theme override */
    .stApp[data-theme="dark"] {
        --color-primary: #8b5cf6;
        --color-primary-hover: #7c3aed;
        --color-secondary: #a855f7;
        --color-secondary-hover: #9333ea;
        
        --color-background-primary: #0f172a;
        --color-background-secondary: #1e293b;
        --color-background-tertiary: #334155;
        --color-background-card: #1e293b;
        
        --color-text-primary: #f8fafc;
        --color-text-secondary: #cbd5e1;
        --color-text-tertiary: #94a3b8;
        --color-text-inverse: #1f2937;
        
        --color-border-primary: #334155;
        --color-border-secondary: #475569;
        --color-border-focus: #8b5cf6;
    }
    """

def get_component_css():
    """Generate CSS for UI components using the theme variables"""
    return """
    /* Main header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, var(--color-primary) 0%, var(--color-secondary) 100%);
        color: var(--color-text-inverse);
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-lg);
    }
    
    .main-header h1 {
        font-size: 3rem;
        margin: 0;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .main-header p {
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-weight: 400;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
        color: var(--color-text-inverse);
        border: none;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--shadow-md);
        cursor: pointer;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-xl);
        background: linear-gradient(135deg, var(--color-primary-hover) 0%, var(--color-secondary-hover) 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: var(--shadow-md);
    }
    
    /* Secondary button styling */
    .secondary-button {
        background: var(--color-background-card);
        color: var(--color-text-primary);
        border: 2px solid var(--color-border-primary);
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .secondary-button:hover {
        border-color: var(--color-primary);
        color: var(--color-primary);
        box-shadow: var(--shadow-md);
    }
    
    /* Form elements */
    .stSelectbox > div > div {
        background-color: var(--color-background-card);
        border: 1px solid var(--color-border-primary);
        border-radius: 8px;
        color: var(--color-text-primary);
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: var(--color-border-focus);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stTextInput > div > div > input {
        background-color: var(--color-background-card);
        border: 1px solid var(--color-border-primary);
        border-radius: 8px;
        color: var(--color-text-primary);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--color-border-focus);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Data frames and tables */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--color-border-primary);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
        color: var(--color-text-inverse);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: var(--shadow-md);
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    .metric-card h3 {
        margin: 0 0 0.5rem 0;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .metric-card p {
        margin: 0;
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Status messages */
    .success-message {
        background-color: rgba(16, 185, 129, 0.1);
        color: var(--color-success);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        border: 1px solid rgba(16, 185, 129, 0.2);
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .error-message {
        background-color: rgba(239, 68, 68, 0.1);
        color: var(--color-error);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        border: 1px solid rgba(239, 68, 68, 0.2);
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .warning-message {
        background-color: rgba(245, 158, 11, 0.1);
        color: var(--color-warning);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        border: 1px solid rgba(245, 158, 11, 0.2);
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .info-message {
        background-color: rgba(59, 130, 246, 0.1);
        color: var(--color-info);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        border: 1px solid rgba(59, 130, 246, 0.2);
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* Card components */
    .card {
        background: var(--color-background-card);
        border: 1px solid var(--color-border-primary);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    
    .card-header {
        border-bottom: 1px solid var(--color-border-primary);
        padding-bottom: 1rem;
        margin-bottom: 1rem;
    }
    
    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--color-text-primary);
        margin: 0;
    }
    
    .card-subtitle {
        font-size: 0.875rem;
        color: var(--color-text-secondary);
        margin: 0.25rem 0 0 0;
    }
    
    /* Workflow navigation */
    .workflow-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 2rem 0;
        padding: 1rem;
        background: var(--color-background-secondary);
        border-radius: 12px;
        border: 1px solid var(--color-border-primary);
    }
    
    .workflow-step {
        display: flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .workflow-step.active {
        background: var(--color-primary);
        color: var(--color-text-inverse);
        box-shadow: var(--shadow-md);
    }
    
    .workflow-step.completed {
        background: var(--color-success);
        color: var(--color-text-inverse);
    }
    
    .workflow-step:hover:not(.active):not(.completed) {
        background: var(--color-background-tertiary);
        color: var(--color-text-primary);
    }
    
    /* Form factor selection */
    .form-factor-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .form-factor-card {
        background: var(--color-background-card);
        border: 2px solid var(--color-border-primary);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .form-factor-card:hover {
        border-color: var(--color-primary);
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }
    
    .form-factor-card.selected {
        border-color: var(--color-primary);
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        box-shadow: var(--shadow-md);
    }
    
    .form-factor-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--color-text-primary);
        margin: 0 0 0.5rem 0;
    }
    
    .form-factor-description {
        font-size: 0.875rem;
        color: var(--color-text-secondary);
        margin: 0 0 1rem 0;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header p {
            font-size: 1rem;
        }
        
        .workflow-nav {
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .form-factor-grid {
            grid-template-columns: 1fr;
        }
    }
    """

def get_plotly_theme():
    """Get Plotly theme configuration for both light and dark modes"""
    return {
        "light": {
            "layout": {
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"color": "#1f2937"},
                "xaxis": {
                    "gridcolor": "#e5e7eb",
                    "linecolor": "#d1d5db",
                    "tickcolor": "#6b7280"
                },
                "yaxis": {
                    "gridcolor": "#e5e7eb", 
                    "linecolor": "#d1d5db",
                    "tickcolor": "#6b7280"
                }
            }
        },
        "dark": {
            "layout": {
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"color": "#f8fafc"},
                "xaxis": {
                    "gridcolor": "#334155",
                    "linecolor": "#475569",
                    "tickcolor": "#94a3b8"
                },
                "yaxis": {
                    "gridcolor": "#334155",
                    "linecolor": "#475569", 
                    "tickcolor": "#94a3b8"
                }
            }
        }
    }

def is_dark_mode():
    """Detect if the current theme is dark mode"""
    try:
        import streamlit as st
        # Check if we're in a Streamlit context
        if hasattr(st, 'get_option'):
            return st.get_option('theme.base') == 'dark'
        return False
    except:
        return False

def get_current_theme():
    """Get the current theme name"""
    return 'dark' if is_dark_mode() else 'light'

def get_theme_colors():
    """Get colors for the current theme"""
    # Default to light theme to avoid issues
    theme = 'light'
    return {
        'primary': COLORS['primary']['500'],
        'secondary': COLORS['secondary']['500'],
        'background': COLORS['background'][theme]['primary'],
        'background_secondary': COLORS['background'][theme]['secondary'],
        'text': COLORS['text'][theme]['primary'],
        'text_secondary': COLORS['text'][theme]['secondary'],
        'border': COLORS['border'][theme]['primary'],
        'success': COLORS['accent']['green'],
        'error': COLORS['accent']['red'],
        'warning': COLORS['accent']['yellow'],
        'info': COLORS['accent']['blue']
    }
