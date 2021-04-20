from pycograph.schemas.parse_result import PackageWithContext


def create_module_with_content(content, name="example", package_name="pak"):
    package = PackageWithContext(
        name=package_name,
        full_name=package_name,
        dir_path=package_name,
    )
    module_with_context = package.add_module(name)
    module_with_context.content = content
    return module_with_context
