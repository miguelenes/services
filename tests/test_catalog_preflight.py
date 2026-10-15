"""Negative catalog fixtures proving preflight errors are actionable."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from tools.catalog_preflight import CatalogValidator


REPOSITORY = Path(__file__).resolve().parents[1]


class CatalogPreflightFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="lerd-catalog-fixture-")
        self.root = Path(self.temp_dir.name)
        shutil.copytree(REPOSITORY / "schema", self.root / "schema")
        services = self.root / "services"
        (services / "bundles").mkdir(parents=True)
        self.preset = {
            "name": "fixture",
            "description": "Fixture service",
            "image": "example.invalid/fixture:1",
            "category": "other",
            "icon": "cube",
        }
        (services / "fixture.yaml").write_text(yaml.safe_dump(self.preset), encoding="utf-8")
        (services / "index.json").write_text(
            json.dumps({"services": [{key: self.preset[key] for key in ("name", "description", "image", "category", "icon")}]}),
            encoding="utf-8",
        )
        self.bundle_index = services / "bundles" / "index.json"
        self.bundle_index.write_text(json.dumps({"schema_version": 1, "bundles": []}), encoding="utf-8")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def check_error(self, needle: str) -> None:
        validator = CatalogValidator(self.root)
        self.assertFalse(validator.run())
        self.assertTrue(any(needle in issue for issue in validator.errors), validator.errors)

    def add_bundle(self, components: list[dict[str, object]], *, environment: dict[str, str] | None = None) -> None:
        bundle = {
            "schema_version": 1,
            "name": "fixture-bundle",
            "version": "1.0.0",
            "description": "Fixture bundle",
            "components": components,
        }
        index = {"schema_version": 1, "bundles": [{"name": "fixture-bundle", "description": "Fixture bundle", "descriptor": "fixture-bundle.yaml"}]}
        (self.root / "services/bundles/fixture-bundle.yaml").write_text(yaml.safe_dump(bundle), encoding="utf-8")
        self.bundle_index.write_text(json.dumps(index), encoding="utf-8")

    @staticmethod
    def component(name: str = "api", **overrides: object) -> dict[str, object]:
        component: dict[str, object] = {
            "name": name,
            "image": "example.invalid/api:1@sha256:" + "a" * 64,
            "supported_hosts": [{"os": "linux", "architecture": "amd64"}],
            "ports": [{"name": "http", "container_port": 8080}],
            "readiness": {"type": "tcp", "port": "http"},
        }
        component.update(overrides)
        return component

    def test_schema_fixture_rejects_invalid_preset_field(self) -> None:
        self.preset["icon"] = "not an icon value"
        (self.root / "services/fixture.yaml").write_text(yaml.safe_dump(self.preset), encoding="utf-8")
        self.check_error("services/fixture.yaml:/icon")

    def test_index_fixture_rejects_parity_break(self) -> None:
        (self.root / "services/index.json").write_text(json.dumps({"services": []}), encoding="utf-8")
        self.check_error("preset 'fixture' is missing from the service index")

    def test_dependency_fixture_rejects_cycle(self) -> None:
        self.add_bundle([self.component("one", depends_on=["two"]), self.component("two", depends_on=["one"])])
        self.check_error("dependency cycle")

    def test_platform_fixture_rejects_unknown_architecture(self) -> None:
        component = self.component()
        component["supported_hosts"] = [{"os": "linux", "architecture": "mips"}]
        self.add_bundle([component])
        self.check_error("/supported_hosts/0/architecture")

    def test_resource_fixture_rejects_non_positive_limit(self) -> None:
        self.add_bundle([self.component(resources={"memory_bytes": 0})])
        self.check_error("/resources/memory_bytes")

    def test_secret_fixture_rejects_literal(self) -> None:
        self.add_bundle([self.component(environment={"API_KEY": "hard-coded-secret"})])
        self.check_error("secret:// reference")

    def test_bundle_schema_fixture_rejects_mutable_image(self) -> None:
        component = self.component()
        component["image"] = "example.invalid/api:latest"
        self.add_bundle([component])
        self.check_error("/components/0/image")

    def test_bundle_schema_fixture_rejects_unsupported_component_setting(self) -> None:
        component = self.component()
        component["privileged"] = True
        self.add_bundle([component])
        self.check_error("Additional properties are not allowed")

    def test_bundle_schema_fixture_rejects_non_loopback_host_binding(self) -> None:
        component = self.component(
            ports=[
                {
                    "name": "http",
                    "container_port": 8080,
                    "host_port": 8080,
                    "publish_host": True,
                    "host_bind": "0.0.0.0",
                }
            ]
        )
        self.add_bundle([component])
        self.check_error("/ports/0/host_bind")


if __name__ == "__main__":
    unittest.main()
