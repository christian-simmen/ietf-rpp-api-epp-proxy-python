"""The common modules of the SQLite backend are named, one by one, as the source modules of the two import contracts that
keep them from importing an extension (`generic-not-extensions`, `sqlite-common-not-extensions`), because a source of
`registry_adapter.sqlite` as a whole would include the part of the extensions. A new module that is in neither list would
escape both, so this test finds it."""
import ast
import tomllib

import pytest

from tests.helper.test_environment import REPOSITORY

SQLITE = REPOSITORY / "src" / "registry_adapter" / "sqlite"

CONTRACTS = {contract["id"]: contract for contract in
             tomllib.loads((REPOSITORY / "pyproject.toml").read_text(encoding="utf-8"))["tool"]["importlinter"]["contracts"]}


def common_modules() -> list[str]:
    """Every module of the common part, a package's `__init__` as the package, without the part of the extensions."""
    names = []
    for path in sorted(SQLITE.rglob("*.py")):
        relative = path.relative_to(SQLITE)
        if relative.parts[0] == "extensions" or "__pycache__" in relative.parts:
            continue
        parts = ["registry_adapter", "sqlite", *relative.with_suffix("").parts]
        if parts[-1] == "__init__":
            parts.pop()
        names.append(".".join(parts))
    return names


def covered(module: str, sources: list[str]) -> bool:
    return any(module == source or module.startswith(f"{source}.") for source in sources)


@pytest.mark.parametrize("contract", ["generic-not-extensions", "sqlite-common-not-extensions"])
def test_every_common_module_is_a_source_module_of_the_contract(contract):
    sources = CONTRACTS[contract]["source_modules"]

    missing = [module for module in common_modules() if module != "registry_adapter.sqlite"
               and not covered(module, sources)]

    assert missing == [], f"{contract} does not name {missing}: add them to its source_modules"


def test_the_package_of_the_common_part_has_no_import_of_its_own():
    """`registry_adapter.sqlite` itself cannot be a source module (it would include the extensions), so its `__init__` is
    held empty of imports."""
    tree = ast.parse((SQLITE / "__init__.py").read_text(encoding="utf-8"))

    assert not [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]


def test_the_contracts_do_not_list_a_module_that_does_not_exist():
    existing = common_modules() + ["registry_adapter.common", "registry_adapter.epp", "registry_adapter.rri"]
    for contract in ("generic-not-extensions", "sqlite-common-not-extensions"):
        for source in CONTRACTS[contract]["source_modules"]:
            if source.startswith("registry_adapter."):
                assert covered(source, existing) or source in existing, f"{contract} names {source}, which is not a module"
