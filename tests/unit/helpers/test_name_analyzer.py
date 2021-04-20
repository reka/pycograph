from pycograph.helpers import name_analyzer


def test_determine_full_name_parts():
    full_name = "pkg.sample_pkg.dummy.PycoThing"

    result = name_analyzer.determine_full_name_parts(full_name)

    assert result == ["pkg", "sample", "pkg", "dummy", "pyco", "thing"]
