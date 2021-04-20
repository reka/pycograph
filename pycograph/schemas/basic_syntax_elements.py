"""Basic syntax elements the output of the parsing by ast.

These objects should contain only properties and simple methods.
"""

from typing import List, Optional

from pydantic import BaseModel


ABSOLUTE = "absolute"
RELATIVE = "relative"


class SyntaxElement(BaseModel):
    pass


class DefinitionSyntaxElement(SyntaxElement):
    name: str


class BlockSyntaxElement(SyntaxElement):
    syntax_elements: List[SyntaxElement] = []

    def add_syntax_elements(self, syntax_elements: List[SyntaxElement]):
        self.syntax_elements.extend(syntax_elements)


class ClassDefSyntaxElement(DefinitionSyntaxElement, BlockSyntaxElement):
    pass


class FunctionDefSyntaxElement(DefinitionSyntaxElement, BlockSyntaxElement):
    pass


class ConstantSyntaxElement(DefinitionSyntaxElement):
    pass


class CallSyntaxElement(SyntaxElement):
    what_reference_name: str
    called_attribute: Optional[str]


class ImportSyntaxElement(SyntaxElement):
    name: str
    as_name: Optional[str]

    def name_in_importer(self):
        return self.as_name or self.name

    def what_full_name(self):
        return self.name

    def reference_type(self):
        return ABSOLUTE


class ImportFromSyntaxElement(ImportSyntaxElement):
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
