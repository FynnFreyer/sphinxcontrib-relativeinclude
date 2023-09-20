# sphinxcontrib-relativeinclude

[![Build](https://img.shields.io/github/actions/workflow/status/FynnFreyer/sphinxcontrib-relativeinclude/publish.yml)](https://github.com/FynnFreyer/sphinxcontrib-relativeinclude/actions/workflows/publish.yml)
[![Docs](https://img.shields.io/github/actions/workflow/status/FynnFreyer/sphinxcontrib-relativeinclude/docs.yml?label=docs)](https://github.com/FynnFreyer/sphinxcontrib-relativeinclude/actions/workflows/docs.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/sphinxcontrib-relativeinclude.svg)](https://pypi.org/project/sphinxcontrib-relativeinclude)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sphinxcontrib-relativeinclude.svg)](https://pypi.org/project/sphinxcontrib-relativeinclude)
[![License: MIT](https://img.shields.io/badge/license-MIT-purple)](https://github.com/FynnFreyer/sphinxcontrib-relativeinclude/blob/main/LICENSE.txt)

## About

This package implements a new reST directive to include files and translate paths included in those files.

## Installation

The project is hosted on [PyPI](https://pypi.org/project/sphinxcontrib-relativeinclude), and can be installed via `pip`.

```console
pip install sphinxcontrib-relativeinclude
```

You can find the contents of the README and the module documentation for the latest release [online](https://fynnfreyer.github.io/sphinxcontrib-relativeinclude).

## Motivation

Let's assume you want to transclude the `README.rst` sitting in your repository root, in your `docs/index.rst`, so it automatically shows up in your generated documentation.
You can just use reST's standard [`include`](https://docutils.sourceforge.io/docs/ref/rst/directives.html#include) directive.

```rst
.. include: ../README.rst
```

**Sidenote:** If you're using a parser, like [MyST](https://myst-parser.readthedocs.io/en/stable/), you could also easily include markdown files, of course.

This will insert the contents of your README in the appropriate place, and even take care of heading levels for you.

The problem arises when you have images or other files included in there. Sphinx won't resolve those links properly, i.e., relative to the README, but instead relative to your Sphinx index document.
That means those pictures won't show up, which, needless to say, is not optimal.
If you use your valuable time to create visual resources for your documentation these should also be included in the documentation output.

|                           ![A honey badger](docs/assets/honey_badger-wikimedia_commons_CCBYSA4_Sumeetmoghe.jpg)                          |
|:----------------------------------------------------------------------------------------------------------------------------------------:|
| Picture of a honey badger by [Sumeetmoghe on Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Honey_Badger.jpg) (CC-BY-SA-4.0) |

This picture uses a relative path to a file in the [`docs/assets`](docs/assets) directory, and would happily show up in your Git repo, but not in your documentation.

This is what this extension is supposed to solve.
It defines a new `relativeinclude` directive, that takes relative paths in included files, and resolves them into absolute ones.
This way your images show up in your documentation output, but you don't have to hardcode absolute paths in your documentation.
(Cf. this awesome honey badger [here](https://fynnfreyer.github.io/sphinxcontrib-relativeinclude/#motivation))

**Caveat emptor:** At this point in time, nested includes are unfortunately not supported.
(See [TODOs](#todos))

## Usage

You have to register the directive in the `setup` function in your `conf.py` file.
(This is a bug, see [TODOs](#todos))

```python
def setup(app):
    """Register the directive."""
    from sphinxcontrib_relativeinclude import RelativeInclude
    app.add_directive("relativeinclude", RelativeInclude)
```

Then you can use it in your documentation index under the registered name.

```rst
.. relativeinclude: ../README.md
    :parser: myst_parser.docutils_
```

It supports the same options as the standard [`include`](https://docutils.sourceforge.io/docs/ref/rst/directives.html#include) directive.
If not, you've found a bug, and I'd be happy if you reported it on the [issue tracker](https://github.com/FynnFreyer/sphinxcontrib-relativeinclude/issues).
Please provide thorough description, and a minimal reproducible example, i.e., (abbreviated) reST files you used, potentially your `conf.py` contents and maybe other relevant info.

If you want to see some real code, check out this repositories [`docs/index.rst`](https://github.com/FynnFreyer/sphinxcontrib-relativeinclude/blob/main/docs/index.rst).

## TODOs

- support multiple levels of indirection
- properly register directive on install

## License

`sphinxcontrib-relativeinclude` is distributed under the terms of the [MIT](https://github.com/FynnFreyer/sphinxcontrib-relativeinclude/blob/main/LICENSE.txt) license.
