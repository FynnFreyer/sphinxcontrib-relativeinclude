# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from sphinxcontrib_relativeinclude.__about__ import __version__

project = "sphinxcontrib-relativeinclude"
author = "Fynn Freyer"
copyright = "2023, Fynn Freyer"  # noqa: A001
language = "en_US"

version = __version__
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinxcontrib.cairosvgconverter",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for output ------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-latex-output

html_theme = "bizstyle"
html_static_path = ["_static"]

latex_elements = {
    "extraclassoptions": "openany,oneside",
    "papersize": "a4paper",
    "pointsize": "12pt",
    "figure_align": "H",
}

# -- Autodoc configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

add_module_names = False

autodoc_mock_imports = ["docutils"]
autodoc_member_order = "bysource"
