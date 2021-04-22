"""Parse the abstract syntax tree of a Python project into basic syntax element objects."""
import ast
from typing import List, Optional

from pycograph.schemas.basic_syntax_elements import (
    CallSyntaxElement,
    ClassDefSyntaxElement,
    ConstantSyntaxElement,
    FunctionDefSyntaxElement,
    ImportSyntaxElement,
    SyntaxElement,
    ImportFromSyntaxElement,
)


def parse_module(content: str, full_name: str) -> List[SyntaxElement]:
    """Parse the content of a Python module into a list os basic syntax elements.

    This function returns only a list of basic syntax elements,
    which will be stored in the module.
    In later steps, they will be converted into objects with context and relationships.

    :param content: The module's content as text.
    :type content: str
    :param full_name: The module's full name.
    :type full_name: str
    :return: A list of basic syntax elements.
    :rtype: List[SyntaxElement]
    """
    result = []
    module = ast.parse(content, full_name, type_comments=True)
    for ast_object in module.body:
        result.extend(parse_ast_object(ast_object))
    return result


def parse_ast_object(ast_object: ast.AST) -> List[SyntaxElement]:
    """Parse an abstract syntax tree object depending on its type.

    :param ast_object: An abstract syntax tree object.
    :type ast_object: ast.AST
    :return: A list of basic syntax elements.
    :rtype: List[SyntaxElement]
    """
    if type(ast_object) == ast.ImportFrom:
        return parse_import_from(ast_object)  # type: ignore
    if type(ast_object) == ast.Import:
        return parse_import(ast_object)  # type: ignore
    if type(ast_object) == ast.FunctionDef:
        return [parse_function(ast_object)]  # type: ignore
    if type(ast_object) == ast.ClassDef:
        return [parse_class(ast_object)]  # type: ignore

    if type(ast_object) == ast.Assign:
        return parse_ast_assign(ast_object)  # type: ignore

    if type(ast_object) == ast.Attribute:
        result = parse_ast_attribute(ast_object)  # type: ignore
        if result:
            return [result]
    if type(ast_object) == ast.Name:
        result = parse_ast_name(ast_object)  # type: ignore
        if result:
            return [result]
    return []


def parse_import_from(ast_import_from: ast.ImportFrom) -> List[ImportFromSyntaxElement]:
    """Convert an ImportFrom ast object into a list of ImportFromSyntaxElements.

    :param ast_import_from: An ImportFrom ast object representing one or more imports.
    :type ast_import_from: ast.ImportFrom
    :return: A list where each member represents exactly 1 imports relationship.
    :rtype: List[ImportFromSyntaxElement]
    """
    result = []
    for import_from_name in ast_import_from.names:
        import_relationship = ImportFromSyntaxElement(
            from_text=ast_import_from.module,
            name=import_from_name.name,
            as_name=import_from_name.asname,
            level=ast_import_from.level,
        )
        result.append(import_relationship)
    return result


def parse_import(ast_import: ast.Import) -> List[ImportSyntaxElement]:
    """Convert an Import ast object into a list of ImportSyntaxElements.

    :param ast_import: An Import ast object representing one or more imports.
    :type ast_import: ast.Import
    :return: A list where each member represents exactly 1 imports relationship.
    :rtype: List[ImportSyntaxElement]
    """
    result = []
    for import_from_name in ast_import.names:
        import_relationship = ImportSyntaxElement(
            name=import_from_name.name,
            as_name=import_from_name.asname,
        )
        result.append(import_relationship)
    return result


def parse_function(ast_function_def: ast.FunctionDef) -> FunctionDefSyntaxElement:
    """Parse a function definition and its content into a basic syntax element.

    The body of the function is parsed into a list `SyntaxElement`s
    and stored in the `FunctionDefSyntaxElement`.

    :param ast_function_def: An function including its content.
    :type ast_function_def: ast.FunctionDef
    :return: A basic syntax element for function definition.
    :rtype: FunctionDefSyntaxElement
    """
    function_def = FunctionDefSyntaxElement(name=ast_function_def.name)
    for line in ast.walk(ast_function_def):
        if type(line) != ast.FunctionDef:
            function_def.add_syntax_elements(parse_ast_object(line))
    return function_def


def parse_class(ast_class: ast.ClassDef) -> ClassDefSyntaxElement:
    """Parse a class definition and its content into a basic syntax element.

    :param ast_class: A class including its content.
    :type ast_class: ast.ClassDef
    :return: A basic syntax element for class definition.
    :rtype: ClassDefSyntaxElement
    """
    class_def = ClassDefSyntaxElement(name=ast_class.name)

    # Here, we don't use walk,
    # because we want to add only the direct children.
    # We assume that we won't encounter ifs or other similar blocks
    # directly in the class's code, but rather in functions...
    for ast_object in ast_class.body:
        class_def.add_syntax_elements(parse_ast_object(ast_object))

    return class_def


def parse_ast_assign(ast_assign: ast.Assign) -> List[SyntaxElement]:
    """Parse an assignment.

    :param ast_assign: An assign statement.
    :type ast_assign: ast.Assign
    :return: A list of syntax basic elements: one element per assignment target.
    :rtype: List[SyntaxElement]
    """
    result = []
    for target in ast_assign.targets:
        if type(target) == ast.Name:
            parsed_name = parse_ast_name(target)  # type: ignore
            if parsed_name:
                result.append(parsed_name)
    return result


def parse_ast_attribute(ast_attribute: ast.Attribute) -> Optional[SyntaxElement]:
    """Parse an attribute into a basic syntax element.

    :param ast_attribute: An attribute ast object.
    :type ast_attribute: ast.Attribute
    :return: A basic syntax element.
    :rtype: Optional[SyntaxElement]
    """
    if type(ast_attribute.value) == ast.Name:
        return parse_ast_name(ast_attribute.value, ast_attribute.attr)  # type: ignore
    if (
        type(ast_attribute.value) == ast.Call
        and type(ast_attribute.value.func) == ast.Name  # type: ignore
    ):
        return parse_ast_name(ast_attribute.value.func, ast_attribute.attr)  # type: ignore
    return None


def parse_ast_name(
    ast_name: ast.Name, called_attribute: Optional[str] = None
) -> Optional[SyntaxElement]:
    """Convert a `Name` ast object into a basic syntax element.

    Depending on the context of the `ast.Name`,
    the result can be a definition or a call.

    :param ast_name: A syntax element representing a name.
    :type ast_name: ast.Name
    :param called_attribute: [description], defaults to None
    :type called_attribute: Optional[str]
    :return: [description]
    :rtype: Optional[SyntaxElement]
    """
    if type(ast_name.ctx) == ast.Load:
        return parse_loaded_ast_name(ast_name, called_attribute)
    if type(ast_name.ctx) == ast.Store:
        return parse_stored_ast_name(ast_name)
    return None


def parse_loaded_ast_name(
    ast_name: ast.Name, called_attribute: Optional[str] = None
) -> CallSyntaxElement:
    """Parse an `ast.Name`, whose context is `ast.Load` into a `CallSyntaxElement`.

    :param ast_name: An `ast.Name`, whose context is `ast.Load`.
    :type ast_name: ast.Name
    :param called_attribute: The attribute defined in `ast.Attribute`, defaults to None
    :type called_attribute: Optional[str]
    :return: [description]
    :rtype: CallSyntaxElement
    """
    return CallSyntaxElement(
        what_reference_name=ast_name.id,
        called_attribute=called_attribute,
    )


def parse_stored_ast_name(ast_name: ast.Name) -> Optional[ConstantSyntaxElement]:
    """Parse an `ast.Name`, whose context is `ast.Store` into a `DefinitionSyntaxElement`.

    The current version of this function supports only constant definitions.

    :param ast_name: An `ast.Name`, whose context is `ast.Store`.
    :type ast_name: ast.Name
    :return: A constant definition if applicable.
    :rtype: Optional[ConstantSyntaxElement]
    """
    if ast_name.id == ast_name.id.upper():
        return ConstantSyntaxElement(name=ast_name.id)
    return None
