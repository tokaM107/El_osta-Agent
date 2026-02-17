import streamlit as st
import os
import base64
from typing import Optional

def _bg_base64():
    # Use the image from the app root directory if it exists there, or define a fallback
    # Current structure suggests it might be in app/elostabackground.png based on previous context
    # or app/ui/assets/ based on the snippet provided.
    
    # Let's try to locate it relative to this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Potential paths
    paths = [
        os.path.join(current_dir, "..", "elostabackground.png"), # app/elostabackground.png
        os.path.join(current_dir, "assets", "elostabackground.png") # app/ui/assets/elostabackground.png
    ]

    for path in paths:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    
    return None


def inject_theme(dark: bool = False):
    """
    Injects the CSS variables and styles for the application.
    """
    
    bg_image = _bg_base64()

    # --- Color Palettes (Tailwind-inspired) ---
    if dark:
        # DARK MODE
        css_vars = """
            --bg-color: #0F172A;
            --bg-gradient-start: #0F172A;
            --bg-gradient-end: #1E293B;
            --card-bg: rgba(30, 41, 59, 0.75);
            --card-border: rgba(255, 255, 255, 0.1);
            --text-primary: #F8FAFC;
            --text-secondary: #94A3B8;
            --accent-primary: #FBBF24;  /* Amber-400 */
            --accent-secondary: #34D399; /* Emerald-400 */
            --input-bg: rgba(15, 23, 42, 0.6);
            --input-border: rgba(255, 255, 255, 0.15);
            --button-bg: #FBBF24;
            --button-text: #0F172A;
            --shadow-color: rgba(0, 0, 0, 0.4);
        """
        bg_overlay_opacity = 0.85 # Dark overlay to make text readable
    else:
        # LIGHT MODE
        css_vars = """
            --bg-color: #F8FAFC;
            --bg-gradient-start: #F1F5F9;
            --bg-gradient-end: #E2E8F0;
            --card-bg: rgba(255, 255, 255, 0.85);
            --card-border: rgba(226, 232, 240, 0.8);
            --text-primary: #1E293B;  /* Slate-800 */
            --text-secondary: #64748B; /* Slate-500 */
            --accent-primary: #D97706;  /* Amber-600 (Darker for contrast on light) */
            --accent-secondary: #059669; /* Emerald-600 */
            --input-bg: #FFFFFF;
            --input-border: #CBD5E1;
            --button-bg: #D97706;
            --button-text: #FFFFFF;
            --shadow-color: rgba(100, 116, 139, 0.15);
        """
        bg_overlay_opacity = 0.6 # Light overlay

    # Background CSS
    if bg_image:
        bg_css = f"""
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url("{bg_image}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            filter: blur(3px); /* Reduced blur as requested */
            opacity: 0.15; /* Low opacity to blend with background color */
            z-index: -1;
            pointer-events: none;
        }}
        """
    else:
        bg_css = ""

    # Global CSS injection
    st.markdown(f"""
        <style>
            :root {{
                {css_vars}
            }}

            /* --- Base Layout --- */
            .stApp {{
                background: linear-gradient(to bottom right, var(--bg-gradient-start), var(--bg-gradient-end));
                color: var(--text-primary);
                font-family: 'Inter', 'Segoe UI', 'Cairo', sans-serif;
            }}

            {bg_css}

            /* --- Typography --- */
            h1, h2, h3, h4, h5, h6 {{
                color: var(--text-primary) !important;
                font-weight: 700;
            }}
            
            p, label, span, div {{
                color: var(--text-primary);
            }}

            .eo-muted {{
                color: var(--text-secondary) !important;
                font-size: 0.9rem;
            }}

            /* --- Cards & Containers --- */
            .eo-card {{
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 20px;
                box-shadow: 0 4px 20px var(--shadow-color);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }}
            
            .eo-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 30px var(--shadow-color);
            }}

            /* Specialized Cards */
            .eo-card-green {{ border-left: 4px solid var(--accent-secondary); }}
            .eo-card-orange {{ border-left: 4px solid var(--accent-primary); }}
            .eo-card-purple {{ border-left: 4px solid #818CF8; }}

            /* --- Streamlit Native Overrides --- */
            
            /* Sidebar */
            section[data-testid="stSidebar"] {{
                background-color: var(--card-bg);
                border-right: 1px solid var(--card-border);
            }}
            
            /* Inputs (Text, Number, Area) */
            .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectboxdiv, .stMultiSelect div {{
                background-color: var(--input-bg) !important;
                color: var(--text-primary) !important;
                border: 1px solid var(--input-border) !important;
                border-radius: 8px !important;
            }}
            
            .stTextInput input:focus, .stTextArea textarea:focus {{
                border-color: var(--accent-primary) !important;
                box-shadow: 0 0 0 2px rgba(251, 191, 36, 0.2) !important;
            }}

            /* Buttons */
            .stButton > button {{
                background-color: var(--button-bg) !important;
                color: var(--button-text) !important;
                border-radius: 8px !important;
                border: none !important;
                padding: 0.6rem 1.2rem !important;
                font-weight: 600 !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: all 0.2s ease;
            }}
            
            .stButton > button:hover {{
                opacity: 0.9;
                transform: translateY(-1px);
                box-shadow: 0 6px 8px rgba(0,0,0,0.15);
            }}

            /* Expander */
            .streamlit-expanderHeader {{
                background-color: var(--input-bg) !important;
                color: var(--text-primary) !important;
                border-radius: 8px !important;
            }}

            /* Pills / Badges */
            .eo-pill {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 6px 16px;
                background: var(--input-bg);
                border: 1px solid var(--card-border);
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: 500;
                color: var(--text-primary);
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }}
            
            /* App Header Specifics */
            .eo-header h1 {{
                 background: linear-gradient(135deg, var(--accent-primary), var(--accent-primary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.2rem;
            }}

        </style>
    """, unsafe_allow_html=True)


def render_header() -> None:
    st.markdown("""
        <div style="text-align: center; padding: 1.5rem 0 2.5rem 0;" class="eo-header">
            <h1 style="font-size: 3rem; margin:0;">🧭 El Osta</h1>
            <div class="eo-muted" style="font-size: 1.2rem;">
                <span style="display:block;">Your Smart Transit Companion</span>
                <span style="font-family: 'Cairo', sans-serif;">رفيقك الذكي في المواصلات</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
