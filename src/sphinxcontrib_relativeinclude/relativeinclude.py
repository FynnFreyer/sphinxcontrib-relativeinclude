# SPDX-FileCopyrightText: 2023-present Fynn Freyer <fynn.freyer@googlemail.com>
#
# SPDX-License-Identifier: MIT
"""
This module implements the :class:`RelativeInclude` class, which provides a new ``relativeinclude`` directive for reST.
This and functions specifically for generating documentation and working with Sphinx.

.. important:: This does not support nested includes!
"""

import logging
from os.path import relpath
from pathlib import Path
from typing import ClassVar, Collection, List

from docutils.nodes import GenericNodeVisitor, Node
from docutils.nodes import document as Document  # noqa: N812
from docutils.parsers.rst.directives.misc import Include

from sphinxcontrib_relativeinclude.__about__ import __version__


class LinkTranslator(GenericNodeVisitor):
    """
    Translates relative links in included documents with respect to the source document.

    .. important:: This does not support nested includes!
    """

    resolve_attrs: ClassVar[Collection[str]] = (
        "reftarget",
        "uri",
    )
    """ Attributes, that need changing. """

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
        if hasattr(node, "resolved") and node.resolved or not hasattr(node, "attributes"):
            return

        attrs_to_resolve = [attr for attr in self.resolve_attrs if attr in node.attributes]

        for attr in attrs_to_resolve:
            old_target = node[attr]  # type: ignore [index]
            new_absolute_target = (self.rel_base / old_target).resolve()
            new_relative_target = relpath(new_absolute_target, self.abs_base)

            node[attr] = new_relative_target  # type: ignore [index]

            logging.info(f"{self}: changed {attr} in {node} from {old_target} to {new_relative_target}.")

            if hasattr(node, "resolved"):
                node.resolved = 1

    def unknown_visit(self, node: Node):
        """If we don't know a Node, we ignore it."""
        logging.info(f"{self}: visited unknown node {node}")

    def default_departure(self, node: Node):
        """Override abstract method for completeness."""


class RelativeInclude(Include):
    """
    This class is supposed to implement a ``relativeinclude`` directive in Sphinx. It should automatically translate
    relative links in included documents and apart from that works just like ``.. include::``.

    .. important:: This does not support nested includes yet!
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

        # breakpoint()
        included_nodes = super().run()

        translator = LinkTranslator(self.state.document, self.include_source, self.include_target)
        # self.state.document.settings.record_dependencies.list
        for node in included_nodes:
            node.walk(translator)

        return included_nodes

    def translate(self, node, absolute_base: Path, relative_base: Path):
        """
        Recursively translate relative nodes.

        :param node: The node we're currently working on.
        :param absolute_base: The absolute path of the file from which we are including.
        :param relative_base: The absolute path of the file we are including.
        """
        # if we're resolved already, or there aren't any attributes to resolve, we move on
        if hasattr(node, "resolved") and node.resolved or not hasattr(node, "attributes"):
            return

        # breakpoint()

        attrs_to_resolve = [attr for attr in self.resolve_attrs if attr in node.attributes]

        for attr in attrs_to_resolve:
            old_target = node[attr]
            new_absolute_target = (relative_base / old_target).resolve()
            new_relative_target = relpath(new_absolute_target, absolute_base)

            # the previously included path is the one we're including from now
            for child in node.children:
                self.translate(child, relative_base, new_absolute_target)

            node[attr] = new_relative_target

            logging.info(f"{self}: changed {attr} in {node} from {old_target} to {new_absolute_target}.")

            if hasattr(node, "resolved"):
                node.resolved = 1


def setup(app):
    """Register the directive."""
    app.add_directive("relativeinclude", RelativeInclude)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
