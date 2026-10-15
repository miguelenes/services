#!/usr/bin/env python3
"""Validate the service catalog and bundle registry without network access."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


SCHEMAS = {
    "preset": "schema/service-preset-v1.schema.json",
    "service_index": "schema/service-index-v1.schema.json",
    "bundle_index": "schema/bundle-index-v1.schema.json",
    "bundle": "schema/service-bundle-v1.schema.json",
}
SENSITIVE_KEY = re.compile(r"(?:pass(?:word)?|secret|token|api[_-]?key|credential)", re.I)
SECRET_REFERENCE = re.compile(r"^secret://[a-z0-9]+(?:-[a-z0-9]+)*$")
LOCAL_DEVELOPMENT_VALUES = {"", "lerd", "lerdpassword", "null", "changeme"}
SERVICE_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
IMAGE_DIGEST = re.compile(r"^.+@sha256:[0-9a-f]{64}$")
BUILTIN_DEPENDENCIES = {
    "mysql",
    "mariadb",
    "postgres",
    "redis",
    "valkey",
}


class DuplicateKeyError(ValueError):
    pass


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise DuplicateKeyError(f"duplicate YAML key {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


class CatalogValidator:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.services_dir = self.root / "services"
        self.bundles_dir = self.services_dir / "bundles"
        self.errors: list[str] = []
        self.schemas: dict[str, dict[str, Any]] = {}
        self.presets: dict[str, dict[str, Any]] = {}
        self.index_entries: dict[str, dict[str, Any]] = {}
        self.bundle_descriptors: dict[str, dict[str, Any]] = {}

    def error(self, file: Path | str, field: str, message: str) -> None:
        try:
            display = Path(file).resolve().relative_to(self.root).as_posix()
        except (ValueError, OSError):
            display = str(file)
        self.errors.append(f"{display}:{field}: {message}")

    def read_json(self, path: Path) -> Any | None:
        try:
            def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
                result: dict[str, Any] = {}
                for key, value in pairs:
                    if key in result:
                        raise DuplicateKeyError(f"duplicate JSON key {key!r}")
                    result[key] = value
                return result

            return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)
        except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKeyError) as exc:
            self.error(path, "/", f"cannot read JSON: {exc}")
            return None

    def read_yaml(self, path: Path) -> Any | None:
        try:
            return yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
        except (OSError, UnicodeError, yaml.YAMLError, DuplicateKeyError) as exc:
            self.error(path, "/", f"cannot read YAML: {exc}")
            return None

    def load_schemas(self) -> None:
        for key, relative in SCHEMAS.items():
            path = self.root / relative
            schema = self.read_json(path)
            if not isinstance(schema, dict):
                continue
            try:
                Draft202012Validator.check_schema(schema)
            except Exception as exc:  # jsonschema exposes several schema error classes
                self.error(path, "/", f"invalid Draft 2020-12 schema: {exc.message if hasattr(exc, 'message') else exc}")
                continue
            self.schemas[key] = schema

    def validate(self, schema_key: str, data: Any, path: Path) -> bool:
        schema = self.schemas.get(schema_key)
        if schema is None:
            return False
        validator = Draft202012Validator(schema)
        violations = sorted(validator.iter_errors(data), key=lambda exc: tuple(map(str, exc.absolute_path)))
        for violation in violations:
            field = "/" + "/".join(map(str, violation.absolute_path)) if violation.absolute_path else "/"
            self.error(path, field, violation.message)
        return not violations

    def load_services(self) -> None:
        index_path = self.services_dir / "index.json"
        index = self.read_json(index_path)
        if index is not None:
            self.validate("service_index", index, index_path)
            records = index.get("services") if isinstance(index, dict) else None
            if isinstance(records, list):
                for position, record in enumerate(records):
                    if not isinstance(record, dict) or not isinstance(record.get("name"), str):
                        continue
                    name = record["name"]
                    if name in self.index_entries:
                        self.error(index_path, f"/services/{position}/name", f"duplicate service name {name!r}")
                    self.index_entries[name] = record

        for path in sorted(self.services_dir.glob("*.yaml")):
            preset = self.read_yaml(path)
            if preset is None:
                continue
            self.validate("preset", preset, path)
            if not isinstance(preset, dict):
                continue
            name = preset.get("name")
            if not isinstance(name, str):
                continue
            if name in self.presets:
                self.error(path, "/name", f"duplicate service name {name!r}; first declared in services/{name}.yaml")
            else:
                self.presets[name] = preset

        service_index_path = self.services_dir / "index.json"
        for name in sorted(self.presets.keys() - self.index_entries.keys()):
            self.error(service_index_path, "/services", f"preset {name!r} is missing from the service index")
        for name in sorted(self.index_entries.keys() - self.presets.keys()):
            self.error(service_index_path, "/services", f"index entry {name!r} has no services/{name}.yaml preset")

        for name in sorted(self.presets.keys() & self.index_entries.keys()):
            preset = self.presets[name]
            entry = self.index_entries[name]
            for key in ("description", "category", "icon", "family", "image"):
                if key in preset and key in entry and preset[key] != entry[key]:
                    self.error(service_index_path, f"/services/{name}/{key}", f"does not match services/{name}.yaml")
            if "versions" in preset and "versions" in entry:
                preset_tags = [version.get("tag") for version in preset["versions"] if isinstance(version, dict)]
                index_tags = [version.get("tag") for version in entry["versions"] if isinstance(version, dict)]
                # The published index can be a compatibility projection; tags/order
                # must match, while image references can differ across schema views.
                if preset_tags != index_tags:
                    self.error(service_index_path, f"/services/{name}/versions", f"version tags/order do not match services/{name}.yaml")

    def check_secret_values(self, data: Any, file: Path, path: str = "") -> None:
        if not isinstance(data, Mapping):
            if isinstance(data, list):
                for index, value in enumerate(data):
                    self.check_secret_values(value, file, f"{path}/{index}")
            return
        for key, value in data.items():
            field = f"{path}/{key}"
            # Secret declarations name inputs; they are not secret values.
            # The actual values still get checked wherever they are wired into
            # the component environment.
            if key == "secrets":
                continue
            if isinstance(key, str) and SENSITIVE_KEY.search(key):
                values = value if isinstance(value, list) else [value]
                for item in values:
                    if item is None or isinstance(item, bool):
                        continue
                    if not isinstance(item, str):
                        self.error(file, field, "sensitive values must be secret references, not literals")
                        continue
                    normalized = item.strip()
                    if normalized in LOCAL_DEVELOPMENT_VALUES or normalized.startswith("!ChangeThis"):
                        continue
                    if not SECRET_REFERENCE.fullmatch(normalized):
                        self.error(file, field, "sensitive value must use a secret:// reference, not a literal")
            self.check_secret_values(value, file, field)

    def load_bundles(self) -> None:
        index_path = self.bundles_dir / "index.json"
        if not index_path.exists():
            self.error(index_path, "/", "bundle index is missing")
            return
        index = self.read_json(index_path)
        if index is None:
            return
        self.validate("bundle_index", index, index_path)
        entries = index.get("bundles") if isinstance(index, dict) else None
        if not isinstance(entries, list):
            return
        seen_names: set[str] = set()
        expected_descriptors: set[Path] = set()
        for position, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            name, relative = entry.get("name"), entry.get("descriptor")
            if isinstance(name, str):
                if name in seen_names:
                    self.error(index_path, f"/bundles/{position}/name", f"duplicate bundle name {name!r}")
                seen_names.add(name)
            if not isinstance(relative, str):
                continue
            relative_path = Path(relative)
            if relative_path.is_absolute() or ".." in relative_path.parts or len(relative_path.parts) != 1 or not relative_path.name.endswith(".yaml"):
                self.error(index_path, f"/bundles/{position}/descriptor", "descriptor path must be a safe YAML file directly under services/bundles")
                continue
            candidate = self.bundles_dir / relative
            try:
                resolved = candidate.resolve(strict=True)
            except OSError as exc:
                self.error(index_path, f"/bundles/{position}/descriptor", f"descriptor does not exist: {exc}")
                continue
            if resolved.parent != self.bundles_dir.resolve():
                self.error(index_path, f"/bundles/{position}/descriptor", "descriptor path must be a safe file directly under services/bundles")
                continue
            expected_descriptors.add(resolved)
            descriptor = self.read_yaml(resolved)
            if descriptor is None:
                continue
            self.validate("bundle", descriptor, resolved)
            if not isinstance(descriptor, dict):
                continue
            descriptor_name = descriptor.get("name")
            if descriptor_name != name:
                self.error(resolved, "/name", f"must match index name {name!r}")
            if isinstance(descriptor_name, str):
                if descriptor_name in self.bundle_descriptors:
                    self.error(resolved, "/name", f"duplicate bundle name {descriptor_name!r}")
                self.bundle_descriptors[descriptor_name] = descriptor
            self.check_secret_values(descriptor, resolved)
            self.check_bundle_components(descriptor, resolved)

        for path in sorted(self.bundles_dir.glob("*.yaml")):
            if path.resolve() not in expected_descriptors:
                self.error(path, "/", "bundle descriptor is not listed in bundles/index.json")

    def check_bundle_components(self, descriptor: dict[str, Any], file: Path) -> None:
        components = descriptor.get("components")
        if not isinstance(components, list):
            return
        names: set[str] = set()
        for position, component in enumerate(components):
            if not isinstance(component, dict):
                continue
            name = component.get("name")
            if isinstance(name, str):
                if name in names:
                    self.error(file, f"/components/{position}/name", f"duplicate component name {name!r}")
                names.add(name)
            image = component.get("image")
            if isinstance(image, str) and not IMAGE_DIGEST.fullmatch(image):
                self.error(file, f"/components/{position}/image", "image must be immutable and pinned with a sha256 digest")
            hosts = component.get("supported_hosts")
            if isinstance(hosts, list) and not hosts:
                self.error(file, f"/components/{position}/supported_hosts", "at least one verified host profile is required")
            ports = component.get("ports")
            port_names = {port.get("name") for port in ports if isinstance(port, dict) and isinstance(port.get("name"), str)} if isinstance(ports, list) else set()
            readiness = component.get("readiness")
            if isinstance(readiness, dict) and readiness.get("port") not in port_names:
                self.error(file, f"/components/{position}/readiness/port", "must reference a declared component port")

        graph: dict[str, list[str]] = {}
        for position, component in enumerate(components):
            if not isinstance(component, dict) or not isinstance(component.get("name"), str):
                continue
            name = component["name"]
            deps = component.get("depends_on", [])
            graph[name] = [dep for dep in deps if isinstance(dep, str)] if isinstance(deps, list) else []
            for dep in graph[name]:
                if dep not in names:
                    self.error(file, f"/components/{position}/depends_on", f"unknown component dependency {dep!r}")
        self.check_graph(graph, file, "/components")

    def check_graph(self, graph: dict[str, list[str]], file: Path, field: str) -> None:
        active: list[str] = []
        finished: set[str] = set()

        def visit(node: str) -> None:
            if node in active:
                start = active.index(node)
                self.error(file, field, "dependency cycle: " + " -> ".join(active[start:] + [node]))
                return
            if node in finished:
                return
            active.append(node)
            for child in graph.get(node, []):
                if child in graph:
                    visit(child)
            active.pop()
            finished.add(node)

        for name in graph:
            visit(name)

    def check_preset_dependencies(self) -> None:
        families = {preset.get("family") for preset in self.presets.values() if isinstance(preset.get("family"), str)}
        known = set(self.presets) | families | BUILTIN_DEPENDENCIES
        graph: dict[str, list[str]] = {}
        for name, preset in self.presets.items():
            deps = preset.get("depends_on", [])
            graph[name] = []
            if not isinstance(deps, list):
                continue
            for dep in deps:
                if not isinstance(dep, str):
                    continue
                if dep not in known:
                    self.error(self.services_dir / f"{name}.yaml", "/depends_on", f"unknown service or family dependency {dep!r}")
                elif dep in self.presets:
                    graph[name].append(dep)
        self.check_graph(graph, self.services_dir / "index.json", "/services/depends_on")

    def run(self) -> bool:
        if not self.services_dir.is_dir():
            self.error(self.services_dir, "/", "services directory is missing")
            return False
        self.load_schemas()
        self.load_services()
        self.load_bundles()
        self.check_preset_dependencies()
        if self.errors:
            for issue in self.errors:
                print(f"ERROR {issue}", file=sys.stderr)
            print(f"Catalog preflight failed with {len(self.errors)} error(s).", file=sys.stderr)
            return False
        print(f"Catalog preflight passed: {len(self.presets)} presets and {len(self.bundle_descriptors)} bundles; no network or container operations performed.")
        return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="repository root (defaults to this script's parent repository)")
    args = parser.parse_args()
    return 0 if CatalogValidator(args.root).run() else 1


if __name__ == "__main__":
    raise SystemExit(main())
