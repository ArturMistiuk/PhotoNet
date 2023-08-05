import sys
import os

sys.path.append(os.path.abspath('..'))

project = 'PhotoNet'
copyright = '2023, Artur Mistiuk'
author = 'Artur Mistiuk'
release = '1.0.0'

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'nature'
html_static_path = ['_static']
