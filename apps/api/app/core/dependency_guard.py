"""Runtime dependency guardrails for core package compatibility."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import metadata

from packaging import version


@dataclass(frozen=True)
class DependencyAssertion:
    """Result for one dependency compatibility assertion."""

    name: str
    installed_version: str | None
    requirement: str
    ok: bool
    message: str


CORE_RUNTIME_REQUIREMENTS = {
    "protobuf": ">=6.31.1,<7.0.0",
    "grpcio": ">=1.76.0,<2.0.0",
    "grpcio-tools": ">=1.76.0,<2.0.0",
    "grpcio-status": ">=1.76.0,<2.0.0",
}

EMBEDDING_RUNTIME_REQUIREMENTS = {
    "sentence-transformers": ">=3.3.1,<3.4.0",
    "transformers": ">=4.53.0,<4.54.0",
    "torch": ">=2.5.1,<2.6.0",
    "tokenizers": ">=0.21.2,<0.22.0",
    "safetensors": ">=0.5.3,<0.6.0",
}

WORKER_RUNTIME_REQUIREMENTS = {
    "celery": ">=5.4.0,<5.5.0",
    "redis": ">=5.2.1,<6.0.0",
    "kombu": ">=5.3.4,<6.0.0",
    "billiard": ">=4.2.0,<5.0.0",
    "vine": ">=5.1.0,<6.0.0",
    "prefect": ">=3.1.12,<3.2.0",
}


def _satisfies(installed: str, requirement: str) -> bool:
    """Evaluate the small requirement subset used by this guard."""
    parsed = version.parse(installed)
    for part in requirement.split(","):
        part = part.strip()
        if part.startswith(">=") and parsed < version.parse(part[2:]):
            return False
        if part.startswith("<") and parsed >= version.parse(part[1:]):
            return False
    return True


def assert_core_dependency_runtime() -> list[DependencyAssertion]:
    """Assert the protobuf/gRPC runtime that the stable backend depends on."""
    results: list[DependencyAssertion] = []
    failures: list[str] = []

    for package_name, requirement in CORE_RUNTIME_REQUIREMENTS.items():
        try:
            installed = metadata.version(package_name)
        except metadata.PackageNotFoundError:
            result = DependencyAssertion(
                name=package_name,
                installed_version=None,
                requirement=requirement,
                ok=False,
                message=f"{package_name} is not installed",
            )
            results.append(result)
            failures.append(result.message)
            continue

        ok = _satisfies(installed, requirement)
        result = DependencyAssertion(
            name=package_name,
            installed_version=installed,
            requirement=requirement,
            ok=ok,
            message=f"{package_name}=={installed} satisfies {requirement}" if ok else f"{package_name}=={installed} violates {requirement}",
        )
        results.append(result)
        if not ok:
            failures.append(result.message)

    if failures:
        raise RuntimeError("Core dependency runtime is incompatible: " + "; ".join(failures))

    return results


def validate_gemini_dependency_layer() -> list[DependencyAssertion]:
    """Validate that optional Gemini packages do not regress protobuf/gRPC."""
    results = assert_core_dependency_runtime()

    legacy_packages = ("google-generativeai", "google-ai-generativelanguage")
    for package_name in legacy_packages:
        try:
            installed = metadata.version(package_name)
        except metadata.PackageNotFoundError:
            results.append(
                DependencyAssertion(
                    name=package_name,
                    installed_version=None,
                    requirement="not installed in Phase 24.1 runtime",
                    ok=True,
                    message=f"{package_name} is absent",
                )
            )
            continue

        results.append(
            DependencyAssertion(
                name=package_name,
                installed_version=installed,
                requirement="absent; use google-genai instead",
                ok=False,
                message=f"{package_name}=={installed} is legacy and may impose protobuf/gRPC constraints",
            )
        )

    try:
        installed = metadata.version("google-genai")
    except metadata.PackageNotFoundError:
        results.append(
            DependencyAssertion(
                name="google-genai",
                installed_version=None,
                requirement="optional AI layer",
                ok=True,
                message="google-genai is not installed; Gemini remains disabled by graceful degradation",
            )
        )
    else:
        results.append(
            DependencyAssertion(
                name="google-genai",
                installed_version=installed,
                requirement=">=2.6.0,<3.0.0",
                ok=_satisfies(installed, ">=2.6.0,<3.0.0"),
                message=f"google-genai=={installed} installed",
            )
        )

    failures = [result.message for result in results if not result.ok]
    if failures:
        raise RuntimeError("Gemini dependency layer is incompatible: " + "; ".join(failures))

    return results


def validate_embedding_dependency_layer() -> list[DependencyAssertion]:
    """Validate optional CPU embedding packages without importing torch."""
    results = assert_core_dependency_runtime()
    failures: list[str] = []

    for package_name, requirement in EMBEDDING_RUNTIME_REQUIREMENTS.items():
        try:
            installed = metadata.version(package_name)
        except metadata.PackageNotFoundError:
            result = DependencyAssertion(
                name=package_name,
                installed_version=None,
                requirement=requirement,
                ok=False,
                message=f"{package_name} is not installed",
            )
            results.append(result)
            failures.append(result.message)
            continue

        ok = _satisfies(installed, requirement)
        cpu_ok = True
        if package_name == "torch":
            cpu_ok = "+cpu" in installed
            ok = ok and cpu_ok
        result = DependencyAssertion(
            name=package_name,
            installed_version=installed,
            requirement=requirement if package_name != "torch" else f"{requirement}, local version +cpu",
            ok=ok,
            message=(
                f"{package_name}=={installed} satisfies {requirement}"
                if ok
                else f"{package_name}=={installed} violates {requirement}"
            ),
        )
        results.append(result)
        if not ok:
            failures.append(result.message)

    if failures:
        raise RuntimeError("Embedding dependency layer is incompatible: " + "; ".join(failures))

    return results


def validate_worker_dependency_layer() -> list[DependencyAssertion]:
    """Validate Celery/Redis/Prefect packages without importing worker modules."""
    results = assert_core_dependency_runtime()
    failures: list[str] = []

    for package_name, requirement in WORKER_RUNTIME_REQUIREMENTS.items():
        try:
            installed = metadata.version(package_name)
        except metadata.PackageNotFoundError:
            ok = package_name == "prefect"
            result = DependencyAssertion(
                name=package_name,
                installed_version=None,
                requirement=requirement if not ok else f"{requirement}; optional local orchestration",
                ok=ok,
                message=(
                    f"{package_name} is optional and not installed"
                    if ok
                    else f"{package_name} is not installed"
                ),
            )
            results.append(result)
            if not ok:
                failures.append(result.message)
            continue

        ok = _satisfies(installed, requirement)
        result = DependencyAssertion(
            name=package_name,
            installed_version=installed,
            requirement=requirement,
            ok=ok,
            message=(
                f"{package_name}=={installed} satisfies {requirement}"
                if ok
                else f"{package_name}=={installed} violates {requirement}"
            ),
        )
        results.append(result)
        if not ok:
            failures.append(result.message)

    if failures:
        raise RuntimeError("Worker dependency layer is incompatible: " + "; ".join(failures))

    return results
