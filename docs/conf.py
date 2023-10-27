# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from sphinxcontrib_relativeinclude import RelativeInclude
from sphinxcontrib_relativeinclude.__about__ import __name__, __author_name__, __version__

project = __name__
author = __author_name__
copyright = f"2023-present, {__author_name__}"  # noqa: A001
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_rtd_theme",
    "sphinxcontrib.cairosvgconverter",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for output ------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-latex-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["assets"]
templates_path = ["_templates"]

latex_elements = {
    "extraclassoptions": "openany,oneside",
    "papersize": "a4paper",
    "pointsize": "12pt",
    "figure_align": "H",
}

# -- Autodoc configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

add_module_names = False

autodoc_mock_imports = ["docutils", "sphinx"]
autodoc_member_order = "bysource"


def setup(app):
    """Register the directive."""
    app.add_directive("relativeinclude", RelativeInclude)
