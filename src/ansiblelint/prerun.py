"""Utilities for configuring ansible runtime environment."""
import logging
import os
import pathlib
import re
import sys
from typing import Any, Dict, Optional

from ansiblelint.config import options
from ansiblelint.constants import ANSIBLE_MOCKED_MODULE, INVALID_CONFIG_RC
from ansiblelint.loaders import yaml_from_file

_logger = logging.getLogger(__name__)


def _get_galaxy_role_ns(galaxy_infos: Dict[str, Any]) -> str:
    """Compute role namespace from meta/main.yml, including trailing dot."""
    role_namespace = galaxy_infos.get('namespace', "")
    if len(role_namespace) == 0:
        role_namespace = galaxy_infos.get('author', "")
    # if there's a space in the name space, it's likely author name
    # and not the galaxy login, so act as if there was no namespace
    if re.match(r"^\w+ \w+", role_namespace):
        role_namespace = ""
    else:
        role_namespace = f"{role_namespace}."
    if not isinstance(role_namespace, str):
        raise RuntimeError("Role namespace must be string, not %s" % role_namespace)
    return role_namespace


def _get_galaxy_role_name(galaxy_infos: Dict[str, Any]) -> str:
    """Compute role name from meta/main.yml."""
    return galaxy_infos.get('role_name', "")


def _get_role_fqrn(galaxy_infos: Dict[str, Any]) -> str:
    """Compute role fqrn."""
    role_namespace = _get_galaxy_role_ns(galaxy_infos)
    role_name = _get_galaxy_role_name(galaxy_infos)
    if len(role_name) == 0:
        role_name = pathlib.Path(".").absolute().name
        role_name = re.sub(r'(ansible-|ansible-role-)', '', role_name)

    return f"{role_namespace}{role_name}"


def _make_module_stub(module_name: str) -> None:
    # a.b.c is treated a collection
    if re.match(r"^(\w+|\w+\.\w+\.[\.\w]+)$", module_name):
        parts = module_name.split(".")
        if len(parts) < 3:
            path = f"{options.cache_dir}/modules"
            module_file = f"{options.cache_dir}/modules/{module_name}.py"
            namespace = None
            collection = None
        else:
            namespace = parts[0]
            collection = parts[1]
            path = f"{ options.cache_dir }/collections/ansible_collections/{ namespace }/{ collection }/plugins/modules/{ '/'.join(parts[2:-1]) }"
            module_file = f"{path}/{parts[-1]}.py"
        os.makedirs(path, exist_ok=True)
        _write_module_stub(
            filename=module_file,
            name=module_file,
            namespace=namespace,
            collection=collection,
        )
    else:
        _logger.error("Config error: %s is not a valid module name.", module_name)
        sys.exit(INVALID_CONFIG_RC)


def _write_module_stub(
    filename: str,
    name: str,
    namespace: Optional[str] = None,
    collection: Optional[str] = None,
) -> None:
    """Write module stub to disk."""
    body = ANSIBLE_MOCKED_MODULE.format(
        name=name, collection=collection, namespace=namespace
    )
    with open(filename, "w") as f:
        f.write(body)


def _perform_mockings() -> None:
    """Mock modules and roles."""
    for role_name in options.mock_roles:
        if re.match(r"\w+\.\w+\.\w+$", role_name):
            namespace, collection, role_dir = role_name.split(".")
            path = f"{options.cache_dir}/collections/ansible_collections/{ namespace }/{ collection }/roles/{ role_dir }/"
        else:
            path = f"{options.cache_dir}/roles/{role_name}"
        os.makedirs(path, exist_ok=True)

    if options.mock_modules:
        for module_name in options.mock_modules:
            _make_module_stub(module_name)

    # if inside a collection repo, symlink it to simulate its installed state
    if not os.path.exists("galaxy.yml"):
        return
    yaml = yaml_from_file("galaxy.yml")
    if not yaml:
        # ignore empty galaxy.yml file
        return
    namespace = yaml.get('namespace', None)
    collection = yaml.get('name', None)
    if not namespace or not collection:
        return
    p = pathlib.Path(
        f"{options.cache_dir}/collections/ansible_collections/{ namespace }"
    )
    p.mkdir(parents=True, exist_ok=True)
    link_path = p / collection
    target = pathlib.Path(options.project_dir).absolute()
    if not link_path.exists() or os.readlink(link_path) != target:
        if link_path.exists():
            link_path.unlink()
        link_path.symlink_to(target, target_is_directory=True)
