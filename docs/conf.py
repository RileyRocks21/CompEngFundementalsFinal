import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

project = 'Delivery Management System'
copyright = '2025, Riley'
author = 'Riley'

version = '1.0'
release = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
