"""Validate embedding runtime without starting the FastAPI backend."""

from __future__ import annotations

import argparse
import json
import os
from importlib import metadata
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from packaging import version


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_CACHE_DIR = ROOT / "runtime" / "model-cache" / "huggingface"


def load_env_file() -> None:
    if not ENV_FILE.exists():
        return
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def assert_dependency(name: str, requirement: str) -> str:
    installed = metadata.version(name)
    parsed = version.parse(installed)
    for part in requirement.split(","):
        part = part.strip()
        if part.startswith(">=") and parsed < version.parse(part[2:]):
            raise RuntimeError(f"{name}=={installed} violates {requirement}")
        if part.startswith("<") and parsed >= version.parse(part[1:]):
            raise RuntimeError(f"{name}=={installed} violates {requirement}")
    return installed


def validate_dependency_layer() -> dict[str, str]:
    return {
        "protobuf": assert_dependency("protobuf", ">=6.31.1,<7.0.0"),
        "grpcio": assert_dependency("grpcio", ">=1.76.0,<2.0.0"),
        "grpcio-tools": assert_dependency("grpcio-tools", ">=1.76.0,<2.0.0"),
        "grpcio-status": assert_dependency("grpcio-status", ">=1.76.0,<2.0.0"),
        "sentence-transformers": assert_dependency("sentence-transformers", ">=3.3.1,<3.4.0"),
        "transformers": assert_dependency("transformers", ">=4.53.0,<4.54.0"),
        "torch": assert_dependency("torch", ">=2.5.1,<2.6.0"),
        "tokenizers": assert_dependency("tokenizers", ">=0.21.2,<0.22.0"),
        "safetensors": assert_dependency("safetensors", ">=0.5.3,<0.6.0"),
    }


def validate_embeddings(model_name: str, cache_dir: Path, local_files_only: bool) -> dict[str, object]:
    import torch
    from sentence_transformers import SentenceTransformer
    from transformers import AutoTokenizer

    if torch.cuda.is_available():
        raise RuntimeError("CUDA is visible; Phase 24.2 requires CPU-only embedding validation")

    cache_dir.mkdir(parents=True, exist_ok=True)
    started = perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        cache_dir=str(cache_dir),
        local_files_only=local_files_only,
    )
    model = SentenceTransformer(
        model_name,
        device="cpu",
        cache_folder=str(cache_dir),
        local_files_only=local_files_only,
    )
    vectors = model.encode(
        ["semantic retrieval validation", "candidate search validation"],
        batch_size=2,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    tokens = tokenizer("semantic retrieval validation", return_tensors="pt")
    duration_ms = round((perf_counter() - started) * 1000, 2)

    return {
        "model": model_name,
        "device": str(model.device),
        "torch": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "embedding_shape": list(vectors.shape),
        "token_count": int(tokens["input_ids"].shape[-1]),
        "duration_ms": duration_ms,
        "cache_dir": str(cache_dir),
        "local_files_only": local_files_only,
    }


def validate_qdrant_insert(vector: list[float], collection: str) -> dict[str, object]:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance, PointStruct, VectorParams

    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key = os.getenv("QDRANT_API_KEY") or None
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key, timeout=10)
    existing = {item.name for item in client.get_collections().collections}
    if collection not in existing:
        client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=len(vector), distance=Distance.COSINE),
        )

    point_id = str(uuid4())
    client.upsert(
        collection_name=collection,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={"phase": "24.2", "text": "embedding validation"},
            )
        ],
    )
    hits = client.search(collection_name=collection, query_vector=vector, limit=1)
    return {
        "collection": collection,
        "point_id": point_id,
        "hit_count": len(hits),
        "top_score": float(hits[0].score) if hits else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate CPU-only embedding runtime.")
    parser.add_argument("--dependency-only", action="store_true", help="Validate packages without loading a model.")
    parser.add_argument("--with-qdrant", action="store_true", help="Also validate Qdrant vector insertion/search.")
    parser.add_argument("--model", default=os.getenv("EMBEDDING_MODEL_NAME", DEFAULT_MODEL))
    parser.add_argument("--cache-dir", default=os.getenv("EMBEDDING_MODEL_CACHE_DIR", str(DEFAULT_CACHE_DIR)))
    parser.add_argument("--local-files-only", action="store_true", help="Use only cached model files.")
    parser.add_argument("--collection", default="phase24_embedding_validation")
    args = parser.parse_args()

    load_env_file()
    dependency_layer = validate_dependency_layer()
    result: dict[str, object] = {"dependency_layer": dependency_layer}

    if not args.dependency_only:
        embedding_result = validate_embeddings(args.model, Path(args.cache_dir), args.local_files_only)
        result["embedding"] = embedding_result
        if args.with_qdrant:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(
                args.model,
                device="cpu",
                cache_folder=args.cache_dir,
                local_files_only=args.local_files_only,
            )
            vector = model.encode("embedding validation", normalize_embeddings=True, show_progress_bar=False).tolist()
            result["qdrant"] = validate_qdrant_insert(vector, args.collection)

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
