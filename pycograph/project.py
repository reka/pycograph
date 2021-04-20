"""Module for the PythonProject class."""

import os
from typing import Dict, List, Optional

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


class PythonProject:
    """
    The central class of the application.

    It processes the basic syntax elements
    and resolves their references in the context of a project.
    """

    def __init__(self, root_dir_path) -> None:
        self.root_dir_path: str = root_dir_path
        self.modules: List[ModuleWithContext] = []
        self.objects: Dict[str, ObjectWithContext] = {}
        self.imported_names: Dict[str, str] = {}

    def _add_object(self, thing: ObjectWithContext):
        self.objects[thing.full_name] = thing

    def parse(self) -> ParseResult:
        self._parse_file_system()
        self._parse_module_contents()
        self._resolve_relationships()
        return ParseResult(
            objects=self.objects,
        )

    def _parse_file_system(self):
        """Find the packages and modules int project's directory."""
        for current_dir, dirs, files in os.walk(self.root_dir_path):
            current_package = None
            for file_name in files:
                name_content, extension = os.path.splitext(file_name)
                if extension == ".py" and file_name != "setup.py":
                    if not current_package:
                        current_package = self._add_package(current_dir)
                    self._add_module(current_package, name_content)

    def _add_package(self, dir_path: str) -> PackageWithContext:
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

    def _add_module(self, package: PackageWithContext, name: str) -> ModuleWithContext:
        modu = package.add_module(name)
        self._add_object(modu)
        self.modules.append(modu)
        return modu

    def _parse_module_contents(self):
        for modu in self.modules:
            added_objects = modu.parse()
            self.objects.update(added_objects)

    def _resolve_relationships(self) -> None:
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
        if import_element.reference_type() == ABSOLUTE:
            imported_thing = self._find_by_name(import_element.what_full_name())
            if imported_thing:
                return imported_thing
            # check the importer module's directory
            sibling_module_path = self._get_relative_imported_path(
                module_full_name, import_element.what_full_name(), 1
            )
            return self._find_by_name(sibling_module_path)
        if import_element.reference_type() == RELATIVE:
            relative_import_path = self._get_relative_imported_path(
                module_full_name, import_element.what_full_name(), import_element.level  # type: ignore
            )
            return self._find_by_name(relative_import_path)
        return None

    def _process_resolved_import(
        self,
        modu: ModuleWithContext,
        imp_rel: ImportSyntaxElement,
        resolve_result: ObjectWithContext,
    ):
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

    def _find_by_name(self, reference_name: str) -> Optional[ObjectWithContext]:
        basic = self.objects.get(reference_name)
        if basic:
            return basic
        referenced_full_name = self.imported_names.get(reference_name)
        if referenced_full_name:
            return self._find_by_name(referenced_full_name)
        return None

    def _get_relative_imported_path(
        self, module_full_name: str, import_full_name: str, level: int
    ) -> str:
        relative_pkg = ".".join(module_full_name.split(".")[:-(level)])
        return f"{relative_pkg}.{import_full_name}"
