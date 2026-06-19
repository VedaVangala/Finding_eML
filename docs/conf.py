import os
import sys

# -- Path setup --------------------------------------------------------------
sys.path.insert(0, os.path.abspath('..'))  # Adjust path to locate classify.py

# -- Project information -----------------------------------------------------
project = 'Finding eML'
copyright = '2025, Foltz lab'
author = 'Foltz lab'
release = '1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',        # Extracts docstrings from code
    'sphinx.ext.autosummary',    # Creates summaries automatically
    'sphinx.ext.napoleon',       # Supports Google and NumPy style docstrings
    'sphinx.ext.viewcode',       # Adds links to source code
    'sphinx_copybutton',         # Adds the copy button to code blocks
]

autosummary_generate = True
autodoc_member_order = 'bysource'
napoleon_google_docstring = True
napoleon_numpy_docstring = True

autodoc_mock_imports = [
    "anndata",
    "scanpy",
    "sklearn",
    "pandas",
    "numpy",
    "pyarrow",
    "scvi",
    "muon",
    "mudata",
    "scipy",
    "matplotlib",
    "seaborn",
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_title = "Finding eML Documentation"  # Change how the title appears in the header
html_theme = 'furo'  
html_static_path = ['_static']

# -- Theme Customization -----------------------------------------------------
html_theme_options = {
    "navbar_start": ["navbar-logo"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["search-field"],
    "sidebar_start": ["sidebar-nav"],
    "sidebar_end": ["sidebar-onthepage-toc"],  # <- Right sidebar TOC moved left
    "show_nav_level": 2,
    "navigation_depth": 4,
    "show_toc_level": 1,
    "collapse_navigation": False,
}


# -- Options for sphinx-copybutton -------------------------------------------------
copybutton_selector = "div.highlight pre" 

html_static_path = ['_static']
html_css_files = ['custom.css']
