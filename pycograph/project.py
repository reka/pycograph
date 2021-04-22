"""Module for the PythonProject class."""

import logging
import os
from typing import Dict, List, Optional

from pycograph.exceptions import ModuleWithInvalidContentException
from pycograph.schemas.basic_syntax_elements import (
    ABSOLUTE,
    ImportSyntaxElement,
    RELATIVE,
)
from pycograph.schemas.parse_result import (
    ModuleWithContext,
    PackageWithContext,
    ObjectWithContext,
    ParseResult,
    ResolvedImportRelationship,
)

logger = logging.getLogger(__name__)


class PythonProject:
    """
    The central class of the application.

    It processes the basic syntax elements
    and resolves their references in the context of a project.
    """

    def __init__(self, root_dir_path: str) -> None:
        """Initialize a project with a root dir path.

        :param root_dir_path: The path of the project's root dir.
        :type root_dir_path: str
        """
        self.root_dir_path: str = root_dir_path
        self.modules: List[ModuleWithContext] = []
        self.objects: Dict[str, ObjectWithContext] = {}
        self.imported_names: Dict[str, str] = {}

    def parse(self) -> ParseResult:
        """Parse the .py files in the project's directory.

        :return: The parse result prepared for the graph model.
        :rtype: ParseResult
        """

        # Go through the project's directory
        # and find the packages and modules.
        self._parse_file_system()

        # Parse the modules's contents.
        # In this step, we find:
        # * all the objects that will become the nodes
        # * some basic data about the relationships.
        self._parse_module_contents()

        # Resolve all the relationships in the context of this project.
        self._resolve_relationships()
        return ParseResult(
            objects=self.objects,
        )

    def _parse_file_system(self) -> None:
        """Find the packages and modules int project's directory."""
        for current_dir, dirs, files in os.walk(self.root_dir_path):
            current_package = None
            for file_name in files:
                name_content, extension = os.path.splitext(file_name)
                if extension == ".py" and file_name != "setup.py":
                    if not current_package:
                        current_package = self._add_package(current_dir)
                    self._add_module_to_package(current_package, name_content)

    def _add_object(self, obj: ObjectWithContext) -> None:
        """Add an object to the internal object collection.

        :param obj: The object to add.
        :type obj: ObjectWithContext
        """
        self.objects[obj.full_name] = obj

    def _add_package(self, dir_path: str) -> PackageWithContext:
        """Create a package object and add it the project.

        :param dir_path: The directory path of the package.
        :type dir_path: str
        :return: The created package object.
        :rtype: PackageWithContext
        """
        package_path = os.path.relpath(dir_path, start=self.root_dir_path)
        package_name = package_path.replace(os.path.sep, ".")

        # Workaround for the src dir structure.
        if package_name.startswith("src."):
            package_name = package_name.replace("src.", "")
        pkg = PackageWithContext(
            name=package_name,
            full_name=package_name,
            dir_path=dir_path,
        )
        self._add_object(pkg)
        return pkg

    def _add_module_to_package(
        self, package: PackageWithContext, name: str
    ) -> ModuleWithContext:
        """Create a module object in a package and add it to the project.

        :param package: The package where the module is located.
        :type package: PackageWithContext
        :param name: The module's name without the package prefix.
        :type name: str
        :return: The created module object.
        :rtype: ModuleWithContext
        """
        modu = package.add_module(name)
        self._add_module(modu)
        return modu

    def _add_module(self, modu: ModuleWithContext) -> None:
        """Add a module both to the modules and objects collections.

        :param modu: The module to add.
        :type modu: ModuleWithContext
        """
        self._add_object(modu)
        self.modules.append(modu)

    def _parse_module_contents(self) -> None:
        """Go through all the modules and parse their contents.

        In this step, we find:
        * all the objects that will become the nodes
        * some basic data about the relationships, that needs to be resolved later.
        """
        for modu in self.modules:
            try:
                added_objects = modu.parse()
            except ModuleWithInvalidContentException:
                logger.error(
                    f"Skipped module {modu.full_name} because of syntax error."
                )
                continue
            self.objects.update(added_objects)

    def _resolve_relationships(self) -> None:
        """Go through all the modules and resolved the relationships in the context of the project.

        The resolution steps have a strict order:
        1. Resolve the imports.
        2. Update the names in the modules's scopes based on the imports.
        3. With the knowledge of the new names, resolve the calls relationships.
        """

        # We have multiple rounds of import resolution
        # In case an import is referencing an imported name.
        # Currently, we have 3 rounds hard-coded.
        # An alternative would be to loop until we find new imports to resolve.
        for _ in range(0, 3):
            for modu in self.modules:
                self._resolve_imports(modu)

        # With resolving the imports,
        # we defined several new names in the modules.
        # We need to pass those to the content of the modules.
        for modu in self.modules:
            modu.update_names_in_scope_for_content()

        # After defining the new names, we can resolve the function calls.
        for modu in self.modules:
            modu.resolve_calls(self.imported_names)

    def _resolve_imports(self, modu: ModuleWithContext):
        """Go through the unresolved imports in a module and try to resolve them in the project's context.

        :param modu: The module whose imports are resolved.
        :type modu: ModuleWithContext
        """
        import_defs = modu.unresolved_imports.copy()
        modu.unresolved_imports = []

        for imp_rel in import_defs:
            resolve_result = self._resolve_import(imp_rel, modu.full_name)
            if resolve_result:
                self._process_resolved_import(modu, imp_rel, resolve_result)
            else:
                modu.unresolved_imports.append(imp_rel)

    def _resolve_import(
        self, import_element: ImportSyntaxElement, module_full_name: str
    ) -> Optional[ObjectWithContext]:
        """Resolve which object an import syntax element is referring to.

        :param import_element: An import syntax element.
        :type import_element: ImportSyntaxElement
        :param module_full_name: The full name of the module where the import is.
        :type module_full_name: str
        :return: The object the import syntax element is referring to.
        :rtype: Optional[ObjectWithContext]
        """
        if import_element.reference_type() == ABSOLUTE:
            imported_thing = self._find_by_full_name(import_element.what_full_name())
            if imported_thing:
                return imported_thing
            # check the importer module's directory
            sibling_module_path = self._get_relative_imported_path(
                module_full_name, import_element.what_full_name(), 1
            )
            return self._find_by_full_name(sibling_module_path)
        if import_element.reference_type() == RELATIVE:
            relative_import_path = self._get_relative_imported_path(
                module_full_name, import_element.what_full_name(), import_element.level  # type: ignore
            )
            return self._find_by_full_name(relative_import_path)
        return None

    def _process_resolved_import(
        self,
        modu: ModuleWithContext,
        imp_rel: ImportSyntaxElement,
        resolve_result: ObjectWithContext,
    ):
        """Process a resolved import.

        * Add the name to the module's scope, so that it can be used when resolving the function calls.
        * Create a `ResolvedImportRelationship` and add it to its module.
        * Register the imported name in the project, so that it can be used when resolving the function calls.

        :param modu: The module where the import is located.
        :type modu: ModuleWithContext
        :param imp_rel: The import syntax element.
        :type imp_rel: ImportSyntaxElement
        :param resolve_result: The object the import is referring to.
        :type resolve_result: ObjectWithContext
        """
        modu.names_in_scope[imp_rel.name_in_importer()] = resolve_result.full_name
        resolved_imp_rel = ResolvedImportRelationship(
            destination_full_name=resolve_result.full_name,
            import_element=imp_rel,
        )
        modu.relationships.append(resolved_imp_rel)
        if modu.label() == "init":
            owner_name = modu.full_name.replace(".__init__", "")
        else:
            owner_name = modu.full_name
        reference_name = f"{owner_name}.{imp_rel.name}"
        self.imported_names[reference_name] = resolve_result.full_name

    def _find_by_full_name(self, reference_name: str) -> Optional[ObjectWithContext]:
        """Find the object belonging to a full name.

        Search at the following places:
        1. The project's objects.
        2. The project's imported names.

        :param reference_name: The full name we're searching for.
        :type reference_name: str
        :return: The object belonging to this full name.
        :rtype: Optional[ObjectWithContext]
        """
        basic = self.objects.get(reference_name)
        if basic:
            return basic
        referenced_full_name = self.imported_names.get(reference_name)
        if referenced_full_name:
            return self._find_by_full_name(referenced_full_name)
        return None

    def _get_relative_imported_path(
        self, module_full_name: str, import_full_name: str, level: int
    ) -> str:
        """Determine the path a relative import is referring to.

        :param module_full_name: The module's full name, where the import is located.
        :type module_full_name: str
        :param import_full_name: The imported name.
        :type import_full_name: str
        :param level: The relative import's level.
        :type level: int
        :return: The full name this import is referring to.
        :rtype: str
        """
        relative_pkg = ".".join(module_full_name.split(".")[:-(level)])
        return f"{relative_pkg}.{import_full_name}"
