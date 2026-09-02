"""Descarga de modelos IA desde HuggingFace."""
import argparse
import os
import sys
from pathlib import Path

try:
    from huggingface_hub import hf_hub_download, snapshot_download
except ImportError:
    print("Instalando huggingface_hub...")
    os.system(f"{sys.executable} -m pip install huggingface_hub")
    from huggingface_hub import hf_hub_download, snapshot_download

MODELS = {
    "llm": {
        "qwen": {
            "repo": "bartowski/Qwen2.5-7B-Instruct-GGUF",
            "file": "Qwen2.5-7B-Instruct-Q4_K_M.gguf",
            "rename_to": "qwen2.5-7b-instruct-q4_k_m.gguf",
            "size_gb": 4.4,
            "dest": "models/llm",
        },
    },
    "visual": {
        "pony": {
            "repo": "LyliaEngine/Pony_Diffusion_V6_XL",
            "file": "ponyDiffusionV6XL_v6StartWithThisOne.safetensors",
            "rename_to": "pony-diffusion-v6-xl.safetensors",
            "size_gb": 6.5,
            "dest": "comfyui/ComfyUI/models/checkpoints",
        },
        "juggernaut": {
            "repo": "RunDiffusion/Juggernaut-XL-v9",
            "file": "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors",
            "rename_to": "juggernautXL_v9.safetensors",
            "size_gb": 6.6,
            "dest": "comfyui/ComfyUI/models/checkpoints",
        },
        "animagine": {
            "repo": "cagliostrolab/animagine-xl-3.1",
            "file": "animagine-xl-3.1.safetensors",
            "size_gb": 6.5,
            "dest": "comfyui/ComfyUI/models/checkpoints",
        },
    },
    "tts": {
        "f5tts": {
            "repo": "SWivid/F5-TTS",
            "files": None,
            "size_gb": 1.8,
            "dest": "models/tts/F5-TTS",
        },
    },
}

TIERS = {
    "mvp": ["llm.qwen", "visual.pony", "tts.f5tts"],
    "full": ["llm.qwen", "visual.pony", "visual.juggernaut", "visual.animagine", "tts.f5tts"],
    "llm-only": ["llm.qwen"],
    "visual-only": ["visual.pony", "visual.juggernaut", "visual.animagine"],
}


def download_model(key: str, model_info: dict) -> None:
    path_key, model_name = key.split(".")
    dest = model_info.get("dest", f"models/{path_key}")

    # Check if target file already exists
    if model_info.get("file"):
        target_name = model_info.get("rename_to", model_info["file"])
        target_path = Path(dest) / target_name
        if target_path.exists():
            print(f"  {model_name} ya existe en {target_path}, saltando descarga.")
            return

    print(f"\n  Descargando {model_name} desde {model_info['repo']}...")
    print(f"  Tamaño estimado: ~{model_info['size_gb']} GB")
    print(f"  Destino: {dest}/")

    os.makedirs(dest, exist_ok=True)

    if model_info.get("file"):
        downloaded_path = hf_hub_download(
            repo_id=model_info["repo"],
            filename=model_info["file"],
            local_dir=dest,
            local_dir_use_symlinks=False,
        )
        if model_info.get("rename_to"):
            new_path = Path(dest) / model_info["rename_to"]
            if os.path.exists(new_path):
                os.remove(new_path)
            os.rename(downloaded_path, new_path)
            print(f"  Renombrado {model_info['file']} a {model_info['rename_to']}")
    else:
        snapshot_download(
            repo_id=model_info["repo"],
            local_dir=dest,
            local_dir_use_symlinks=False,
        )

    print(f"  {model_name} descargado correctamente.")


def main():
    parser = argparse.ArgumentParser(description="Descarga modelos para AI Story Studio")
    parser.add_argument("--tier", choices=TIERS.keys(), default="mvp", help="Tier de modelos a descargar")
    args = parser.parse_args()

    models_to_download = TIERS[args.tier]
    total_gb = sum(MODELS[k[0]][k[1]]["size_gb"] for k in (m.split(".") for m in models_to_download))

    print(f"=== AI Story Studio — Descarga de Modelos ===")
    print(f"Tier: {args.tier}")
    print(f"Modelos: {len(models_to_download)}")
    print(f"Espacio requerido: ~{total_gb:.1f} GB")

    for model_key in models_to_download:
        parts = model_key.split(".")
        category = MODELS.get(parts[0])
        if not category or parts[1] not in category:
            print(f"  Modelo desconocido: {model_key}, saltando...")
            continue
        download_model(model_key, category[parts[1]])

    print(f"\n=== Descarga completada ===")


if __name__ == "__main__":
    main()