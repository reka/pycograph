"""The objects, which will become the nodes and edges of the graph.

They contain contextual information and methods with logic.
"""

from abc import ABC, abstractmethod
import logging
import os
from pycograph.exceptions import ModuleWithInvalidContentException
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
    """Base class for all relationship classes.

    These classes will be converted into the graph's edges.
    The relationships are contained by the source object.
    The destination object's full name is stored as a property in the relationship.
    """

    name: str
    destination_full_name: str

    def properties(self) -> Dict[str, Any]:
        return {}


class ContainsRelationship(Relationship):
    """Contains relationship between two objects."""

    name: str = "contains"


class CallsRelationship(Relationship):
    """Calls relationship between two objects."""

    name: str = "calls"
    syntax_element: CallSyntaxElement

    def properties(self) -> Dict[str, Any]:
        return {
            "reference_name": self.syntax_element.what_reference_name,
            "called_attribute": self.syntax_element.called_attribute or "",
        }


class ResolvedImportRelationship(Relationship):
    """Import relationship between two objects.

    A ResolvedImportRelationship object gets created during import resolution,
    when we've figured out the full name of the imported object.
    """

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
    """Base class for all objects.

    These will become the graph's nodes.
    """

    name: str
    full_name: str = ""
    names_in_scope: dict = {}
    is_test_object: bool = False
    test_type: str = ""
    relationships: List[Relationship] = []
    unresolved_imports: List[ImportSyntaxElement] = []
    calls: List[CallSyntaxElement] = []
    contained_objects: List["ObjectWithContext"] = []

    @abstractmethod
    def label(self) -> str:
        """The object's label showing its type.

        This will be the node's label in the graph model.
        """
        pass

    def node_properties(self) -> Dict[str, Any]:
        """Properties that will be stored in the RedisGraph node.

        :return: A dictionary containing the properties for the graph node.
        :rtype: Dict[str, Any]
        """
        return self.dict(include=self._node_property_keys())

    def _node_property_keys(self) -> set:
        """The property keys that will be used by the node.

        :return: A set with the relevant property names.
        :rtype: set
        """
        relevant_keys = {"name", "full_name", "is_test_object"}
        if self.is_test_object and settings.determine_test_types:
            relevant_keys.add("test_type")
        return relevant_keys

    def _parse_syntax_elements(
        self, syntax_elements: List[SyntaxElement]
    ) -> Dict[str, "ObjectWithContext"]:
        """Parse the syntax elements in the context of this object.

        If the syntax element defines an object => Store it and add it to the result dictionary.
        If the syntax element represents a relationship => Store it for further processing.

        :return: All the syntax elements that represent an object.
        :rtype: Dict[str, ObjectWithContext]
        """
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
                self._add_to_content(defined_object)
                result[defined_object.full_name] = defined_object
                self.names_in_scope[defined_object.name] = defined_object.full_name

                # BlockSyntaxElements contain further syntax elements.
                # We need to parse these as well.
                if isinstance(syntax_element, BlockSyntaxElement):
                    result.update(
                        defined_object._parse_syntax_elements(
                            syntax_element.syntax_elements
                        )
                    )
        return result

    def _add_to_content(self, obj: "ObjectWithContext") -> None:
        """Add a contained object.

        :param obj: The contained object.
        :type obj: ObjectWithContext
        """
        obj._update_properties_from_owner(self)
        contains_rel = ContainsRelationship(
            destination_full_name=obj.full_name,
        )
        self.relationships.append(contains_rel)
        self.contained_objects.append(obj)

    def _update_properties_from_owner(self, owner: "ObjectWithContext") -> None:
        """Update the properties that the object inherits from its owner.

        Following the aggregate pattern,
        an object doesn't know its owner,
        but the owner knows its contained object.
        We use this method to update the properties that come from the owner.

        :param owner: [description]
        :type owner: ObjectWithContext
        """
        self.full_name = f"{owner.full_name}.{self.name}"
        self.is_test_object = owner.is_test_object
        self.test_type = owner.test_type

    def update_names_in_scope_for_content(self) -> None:
        """Pass the names in scope to all contained objects recursively."""
        for thing in self.contained_objects:
            thing.names_in_scope.update(self.names_in_scope)
            thing.update_names_in_scope_for_content()

    def resolve_calls(self, imported_names: Dict[str, str]) -> None:
        """Resolve all call definitions recursively.

        :param imported_names: A project-level dict showing which object an imported name refers to.
        :type imported_names: Dict[str, str]
        """
        for call in self.calls:
            self._resolve_call(call, imported_names)
        for thing in self.contained_objects:
            thing.resolve_calls(imported_names)

    def _resolve_call(
        self, call: CallSyntaxElement, imported_names: Dict[str, str]
    ) -> None:
        """Resolve a call and determine which object it refers to.

        :param call: A syntax element defining a calls relationship.
        :type call: CallSyntaxElement
        :param imported_names: A project-level dict showing which object an imported name refers to.
        :type imported_names: Dict[str, str]
        """
        if call.what_reference_name not in self.names_in_scope.keys():
            return
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


class FunctionWithContext(ObjectWithContext):
    """An object representing a function."""

    def label(self) -> str:
        if self.is_test_object:
            if self.name.startswith("test_"):
                return "test_function"
            else:
                return "test_helper_function"
        else:
            return "function"


class ClassWithContext(ObjectWithContext):
    """An object representing a class."""

    def _update_properties_from_owner(self, owner: "ObjectWithContext"):
        super()._update_properties_from_owner(owner)
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
    """An object representing a constant."""

    def label(self) -> str:
        if self.is_test_object:
            return "test_constant"
        else:
            return "constant"


class ModuleWithContext(ObjectWithContext):
    """An object representing a module.

    They are created by the PythonProject,
    while it's parsing the file system and detecting .py files.
    """

    file_path: str
    content: str = ""

    def label(self) -> str:
        if self.name == "__init__":
            return "init"
        elif self.is_test_object:
            return "test_module"
        else:
            return "module"

    def parse(self) -> Dict[str, ObjectWithContext]:
        """Parse the content of a module.

        A dictionary of objects and their unique full names is returned
        and stored in the caller (the project).
        All parsed elements are stored in the module itself as well.

        :raises ModuleWithInvalidContentException: If the module contains invalid syntax.
        :return: A dictionary of objects and their unique full names.
        :rtype: Dict[str, ObjectWithContext]
        """
        self._read_content()
        try:
            syntax_elements = parse_module(self.content, self.full_name)
            result = self._parse_syntax_elements(syntax_elements)
            return result
        except SyntaxError as e:
            raise ModuleWithInvalidContentException from e

    def _read_content(self):
        if self.content:
            return
        with open(self.file_path, "r") as f:
            self.content = f.read()


class PackageWithContext(ObjectWithContext):
    """An object representing a package.

    They are created by the PythonProject,
    while it's parsing the file system and detecting directories containing .py files.
    """

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
        """Create a module contained by this package.

        :param name: The name of the module.
        :type name: str
        :return: The module created.
        :rtype: ModuleWithContext
        """
        module_path = os.path.join(self.dir_path, f"{name}.py")
        modu = ModuleWithContext(
            name=name,
            file_path=module_path,
        )
        self._add_to_content(modu)
        return modu


class ParseResult(BaseModel):
    """The result of parsing a Python project.

    This will be used to create the graph model.
    The objects dict contains the nodes.
    The edges are modelled as relationships list of the source object.
    """

    objects: Dict[str, ObjectWithContext] = {}
