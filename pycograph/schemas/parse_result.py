"""The objects, which will become the nodes and edges of the graph.

They contain contextual information and methods with logic.
"""

from abc import ABC
import logging
import os
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from pycograph.ast_to_basic_syntax_elements import parse_module
from pycograph.schemas.basic_syntax_elements import (
    BlockSyntaxElement,
    CallSyntaxElement,
    ClassDefSyntaxElement,
    ConstantSyntaxElement,
    FunctionDefSyntaxElement,
    ImportSyntaxElement,
    ImportFromSyntaxElement,
    SyntaxElement,
)

from pycograph.config import settings
from pycograph.helpers.name_analyzer import determine_full_name_parts

logger = logging.getLogger(__name__)


class Relationship(BaseModel, ABC):
    name: str
    destination_full_name: str

    def properties(self) -> Dict[str, Any]:
        return {}


class ContainsRelationship(Relationship):
    name: str = "contains"


class CallsRelationship(Relationship):
    name: str = "calls"
    syntax_element: CallSyntaxElement

    def properties(self) -> Dict[str, Any]:
        return {
            "reference_name": self.syntax_element.what_reference_name,
            "called_attribute": self.syntax_element.called_attribute or "",
        }


class ResolvedImportRelationship(Relationship):
    name: str = "imports"
    import_element: ImportSyntaxElement

    def properties(self) -> Dict[str, Any]:
        props = {
            "name": self.import_element.name,
            "as_name": self.import_element.as_name or "",
            "reference_type": self.import_element.reference_type(),
        }
        if isinstance(self.import_element, ImportFromSyntaxElement):
            props["from"] = self.import_element.from_text or ""
            props["level"] = self.import_element.level
        return props


class ObjectWithContext(BaseModel, ABC):
    name: str
    full_name: str = ""
    names_in_scope: dict = {}
    is_test_object: bool = False
    test_type: str = ""
    relationships: List[Relationship] = []
    unresolved_imports: List[ImportSyntaxElement] = []
    calls: List[CallSyntaxElement] = []
    contained_objects: List["ObjectWithContext"] = []

    def label(self) -> str:
        return "other"

    def node_properties(self):
        if self.is_test_object and settings.determine_test_types:
            return {"name", "full_name", "is_test_object", "test_type"}
        return {"name", "full_name", "is_test_object"}

    def parse_syntax_elements(self, syntax_elements: List[SyntaxElement]):
        result = {}
        for syntax_element in syntax_elements:
            defined_object: Optional[ObjectWithContext] = None
            if isinstance(syntax_element, ImportSyntaxElement):
                self.unresolved_imports.append(syntax_element)
                continue
            if isinstance(syntax_element, CallSyntaxElement):
                self.calls.append(syntax_element)
                continue
            if isinstance(syntax_element, ConstantSyntaxElement):
                defined_object = ConstantWithContext(
                    name=syntax_element.name,
                )
            if isinstance(syntax_element, ClassDefSyntaxElement):
                defined_object = ClassWithContext(
                    name=syntax_element.name,
                )
            if isinstance(syntax_element, FunctionDefSyntaxElement):
                defined_object = FunctionWithContext(
                    name=syntax_element.name,
                )
            if defined_object:
                self.add_content(defined_object)
                result[defined_object.full_name] = defined_object
                self.names_in_scope[defined_object.name] = defined_object.full_name
                if isinstance(syntax_element, BlockSyntaxElement):
                    result.update(
                        defined_object.parse_syntax_elements(
                            syntax_element.syntax_elements
                        )
                    )
        return result

    def add_content(self, thing: "ObjectWithContext"):
        thing.initialize(self)
        contains_rel = ContainsRelationship(
            destination_full_name=thing.full_name,
        )
        self.relationships.append(contains_rel)
        self.contained_objects.append(thing)

    def initialize(self, owner: "ObjectWithContext"):
        self.full_name = f"{owner.full_name}.{self.name}"
        self.is_test_object = owner.is_test_object
        self.test_type = owner.test_type

    def update_names_in_scope_for_content(self):
        for thing in self.contained_objects:
            thing.names_in_scope.update(self.names_in_scope)
            thing.update_names_in_scope_for_content()

    def resolve_calls(self, imported_names):
        for call in self.calls:
            if call.what_reference_name not in self.names_in_scope.keys():
                continue
            called_full_name = self.names_in_scope[call.what_reference_name]
            if call.called_attribute:
                what_full_name = f"{called_full_name}.{call.called_attribute}"
            else:
                what_full_name = called_full_name
            if what_full_name in imported_names.keys():
                what_full_name = imported_names[what_full_name]
            calls_rel = CallsRelationship(
                destination_full_name=what_full_name, syntax_element=call
            )
            self.relationships.append(calls_rel)
        for thing in self.contained_objects:
            thing.resolve_calls(imported_names)


class FunctionWithContext(ObjectWithContext):
    def label(self) -> str:
        if self.is_test_object:
            if self.name.startswith("test_"):
                return "test_function"
            else:
                return "test_helper_function"
        else:
            return "function"


class ClassWithContext(ObjectWithContext):
    def initialize(self, owner: "ObjectWithContext"):
        super().initialize(owner)
        self.names_in_scope = {
            "self": self.full_name,
            "class": self.full_name,
        }

    def label(self) -> str:
        if self.is_test_object:
            return "test_class"
        else:
            return "class"


class ConstantWithContext(ObjectWithContext):
    def label(self) -> str:
        if self.is_test_object:
            return "test_constant"
        else:
            return "constant"


class ModuleWithContext(ObjectWithContext):
    file_path: str
    content: str = ""

    def label(self) -> str:
        if self.name == "__init__":
            return "init"
        elif self.is_test_object:
            return "test_module"
        else:
            return "module"

    def parse(self):
        self.read_content()
        try:
            syntax_elements = parse_module(self.content, self.full_name)
            result = self.parse_syntax_elements(syntax_elements)
            return result
        except SyntaxError:
            logger.error(f"Skipped module {self.full_name} because of syntax error.")
            return []

    def read_content(self):
        if self.content:
            return
        with open(self.file_path, "r") as f:
            self.content = f.read()


class PackageWithContext(ObjectWithContext):
    dir_path: str

    def label(self) -> str:
        if self.is_test_object:
            return "test_package"
        else:
            return "package"

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        full_name_parts = determine_full_name_parts(self.full_name)
        self.is_test_object = "test" in full_name_parts or "tests" in full_name_parts
        if (
            settings.determine_test_types
            and self.is_test_object
            and len(full_name_parts) > 1
        ):
            self.test_type = full_name_parts[1]

    def add_module(self, name: str) -> ModuleWithContext:
        module_path = os.path.join(self.dir_path, f"{name}.py")
        modu = ModuleWithContext(
            name=name,
            file_path=module_path,
        )
        self.add_content(modu)
        return modu


class ParseResult(BaseModel):
    objects: Dict[str, ObjectWithContext] = {}
