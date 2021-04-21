"""Basic syntax elements the output of the parsing by ast.

These objects should contain only properties and simple methods.
"""

from abc import ABC
from typing import List, Optional

from pydantic import BaseModel


ABSOLUTE = "absolute"
RELATIVE = "relative"


class SyntaxElement(BaseModel, ABC):
    """The base class for all syntax element classes."""

    pass


class DefinitionSyntaxElement(SyntaxElement, ABC):
    """Base class for syntax elements containing a definition of an object with a name.

    Examples: class, function, constant.
    """

    name: str


class BlockSyntaxElement(SyntaxElement, ABC):
    """Base class for syntax elements representing blocks.

    They can contain multiple further syntax elements.
    """

    syntax_elements: List[SyntaxElement] = []

    def add_syntax_elements(self, syntax_elements: List[SyntaxElement]):
        self.syntax_elements.extend(syntax_elements)


class ClassDefSyntaxElement(DefinitionSyntaxElement, BlockSyntaxElement):
    """Class definition.

    It can contain multiple syntax elements, e.g. function definitions.
    """

    pass


class FunctionDefSyntaxElement(DefinitionSyntaxElement, BlockSyntaxElement):
    """Function definition.

    It can contain multiple syntax elements, mainly calls.
    """

    pass


class ConstantSyntaxElement(DefinitionSyntaxElement):
    """Constant definition."""

    pass


class CallSyntaxElement(SyntaxElement):
    """A call from one named object to another."""

    what_reference_name: str
    called_attribute: Optional[str]


class ImportSyntaxElement(SyntaxElement):
    """The representation of an import statement."""

    name: str
    as_name: Optional[str]

    def name_in_importer(self):
        return self.as_name or self.name

    def what_full_name(self):
        return self.name

    def reference_type(self):
        return ABSOLUTE


class ImportFromSyntaxElement(ImportSyntaxElement):
    """The representation of an import from statement."""

    from_text: Optional[str]
    level: int

    def what_full_name(self):
        if self.from_text:
            return f"{self.from_text}.{self.name}"
        else:
            return self.name

    def reference_type(self):
        if self.level == 0:
            return ABSOLUTE
        else:
            return RELATIVE
