# SPDX-FileCopyrightText: 2023-present Fynn Freyer <fynn.freyer@googlemail.com>
#
# SPDX-License-Identifier: MIT

"""
Module Documentation
====================

The :mod:`sphinxcontrib-relativeinclude.relativeinclude` module implements the :class:`RelativeInclude` class, which
provides a new ``relativeinclude`` directive for reST. This directive works just like a normal include, but it will
translate relative paths in the included document, so that they're relative to the document we're including from.

.. warning:: This does not support nested includes yet!
"""

from os.path import relpath
from pathlib import Path
from typing import ClassVar, Collection, List

from docutils.nodes import Element, GenericNodeVisitor, Node
from docutils.nodes import document as Document  # noqa: N812
from docutils.parsers.rst.directives.misc import Include
from sphinx import __display_version__
from sphinx.util import logging

logger = logging.getLogger(__name__)

__app_name__ = "sphinxcontrib-relativeinclude"
__description__ = "Implements a new reST include directive to translate relative paths."

__author_name__ = "Fynn Freyer"
__author_email__ = "fynn.freyer@googlemail.com"

__authors__ = [
    {"name": __author_name__, "email": __author_email__},
]

__version__ = "0.0.4"

__all__ = ["LinkTranslator", "RelativeInclude", "setup", "__app_name__", "__author_name__", "__version__"]


def _identify(obj: object) -> str:
    """Provide a human-readable identifier for arbitrary objects."""
    from hashlib import md5

    # this depends on a CPython implementation detail,
    # and should not be used in arbitrary contexts
    raw_hash = str(hash(obj) if hasattr(obj, "__hash__") else id(obj)).encode()
    # it doesn't matter here, because this is protected and only for logging
    pretty_hash = md5(raw_hash).hexdigest()[:6].upper()  # noqa: S324
    return f"{obj.__class__.__name__}_{pretty_hash}"


class LinkTranslator(GenericNodeVisitor):
    """
    Translates relative links in included documents with respect to the source document.
    """

    resolve_attrs: ClassVar[Collection[str]] = (
        "reftarget",
        "uri",
    )
    """ Attributes, that need changing. """

    ignore_schemes: ClassVar[Collection[str]] = (
        "http",
        "https",
        "data",
    )
    """ If we encounter these prefixes in a link, we leave it alone. """

    def __init__(self, document: Document, absolute_base: Path, relative_base: Path):
        """
        Initialize a ``LinkTranslator``.

        :param document: The document Node we're working on.
        :param absolute_base: The path of the file from which we are including.
        :param relative_base: The path of the file we are including.
        """
        super().__init__(document)

        self.abs_base = absolute_base.resolve().parent
        self.rel_base = relative_base.resolve().parent

    def default_visit(self, node: Node):
        """When visiting a node, we change all attrs with relative paths, defined in :attr:`change_attrs`."""
        # if we're resolved already, or there aren't any attributes to resolve, we move on
        if not isinstance(node, Element) or (hasattr(node, "resolved") and node.resolved):
            return

        attrs_to_resolve = [attr for attr in self.resolve_attrs if attr in node.attributes]

        for attr in attrs_to_resolve:
            old_target = node[attr]

            # if this is a link, or a data URL, we skip it
            if any(old_target.startswith(scheme) for scheme in self.ignore_schemes):
                logger.info(f"{_identify(self)}: skipping data URL: {old_target}")
                continue

            new_absolute_target = (self.rel_base / old_target).resolve()
            new_relative_target = relpath(new_absolute_target, self.abs_base)

            if new_absolute_target.exists():
                node[attr] = new_relative_target
                logger.info(
                    f"{_identify(self)}: changed {attr} in {_identify(node)} "
                    f"from {old_target} to {new_relative_target}."
                )
            else:
                logger.warn(
                    f"{_identify(self)}: couldn't resolve {_identify(node)} "
                    f"target path {new_absolute_target} derived from {old_target}. Skipping!"
                )

            if hasattr(node, "resolved"):
                node.resolved = True  # type: ignore [attr-defined]

    def unknown_visit(self, node: Node):
        """If we don't know a Node, we ignore it."""
        logger.warn(f"{_identify(self)}: visited unknown node {_identify(node)} of type {type(node)}")

    def default_departure(self, node: Node):
        """Override abstract method for completeness."""
        logger.info(f"{_identify(self)}: departing from {_identify(node)}.")


class RelativeInclude(Include):
    """
    This class is supposed to implement a ``relativeinclude`` directive in Sphinx. It should automatically translate
    relative links in included documents and apart from that works just like ``.. include::``.
    """

    resolve_attrs: ClassVar[Collection[str]] = (
        "reftarget",
        "uri",
    )
    """ Attributes, that need changing. """

    @property
    def include_source(self) -> Path:
        """The absolute path of the document we're including from."""
        source = None

        if source is None:
            source = self.state.document.current_source

        return Path(source).resolve()

    @property
    def include_target(self) -> Path:
        """The absolute path of the document we're including."""
        target = Path(self.arguments[0])
        if target.is_absolute():
            return target.resolve()  # force error if not existent
        return Path(self.include_source.parent / target).resolve()

    def run(self) -> List[Node]:
        """
        Include a file as part of the content of this reST file, and translate any relative paths in the included file.
        """

        included_nodes = super().run()

        translator = LinkTranslator(self.state.document, self.include_source, self.include_target)
        for node in included_nodes:
            node.walk(translator)

        return included_nodes

    def translate(self, node: Node, absolute_base: Path, relative_base: Path):
        """
        Recursively translate relative nodes.

        :param node: The node we're currently working on.
        :param absolute_base: The absolute path of the file from which we are including.
        :param relative_base: The absolute path of the file we are including.
        """
        # if we're resolved already, or there aren't any attributes to resolve, we move on
        if not isinstance(node, Element) or (
            hasattr(node, "resolved") and node.resolved  # type: ignore [attr-defined]
        ):
            return

        attrs_to_resolve = [attr for attr in self.resolve_attrs if attr in node.attributes]

        for attr in attrs_to_resolve:
            old_target = node[attr]
            new_absolute_target = (relative_base / old_target).resolve()
            new_relative_target = relpath(new_absolute_target, absolute_base)

            # the previously included path is the one we're including from now
            for child in node.children:
                self.translate(child, relative_base, new_absolute_target)

            node[attr] = new_relative_target

            logger.info(
                f"{_identify(self)}: "
                f"changed {attr} in {_identify(node)} "
                f"from {old_target} to {new_absolute_target}."
            )

            if hasattr(node, "resolved"):
                node.resolved = True  # type: ignore [attr-defined]


def setup(app):
    """Register the directive."""
    app.add_directive("relativeinclude", RelativeInclude)

    return {
        "version": __display_version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
