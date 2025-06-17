#!/usr/bin/env python3
"""Create a stub hypernet for testing Text-to-LoRA pipeline."""

import json
from pathlib import Path
import torch
from safetensors.torch import save_file

def create_hypernet_stub():
    """Create a minimal hypernet stub for jan-mini-14B."""
    
    hypernet_dir = Path("trained_t2l/jan_qwen_t2l")
    hypernet_dir.mkdir(parents=True, exist_ok=True)
    
    # Configuration for jan-mini-14B
    config = {
        "model_type": "qwen2",
        "base_model": "jan-ai/Jan-mini-14B-qwen3",
        "num_layers": 40,
        "hidden_size": 5120,
        "intermediate_size": 13824,
        "num_attention_heads": 40,
        "num_key_value_heads": 8,
        "vocab_size": 151936,
        "lora_rank": 8,
        "lora_alpha": 16,
        "lora_dropout": 0.05,
        "target_modules": [
            "q_proj", "v_proj", "k_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ],
        "hypernet_hidden_size": 768,
        "hypernet_num_layers": 6
    }
    
    # Save config
    with open(hypernet_dir / "config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    # Create stub hypernet weights
    hypernet_weights = {
        "encoder.embedding.weight": torch.randn(config["vocab_size"], config["hypernet_hidden_size"]) * 0.02,
        "encoder.position_embedding.weight": torch.randn(512, config["hypernet_hidden_size"]) * 0.02,
    }
    
    # Add transformer layers
    for i in range(config["hypernet_num_layers"]):
        prefix = f"encoder.layers.{i}"
        hypernet_weights.update({
            f"{prefix}.self_attn.q_proj.weight": torch.randn(config["hypernet_hidden_size"], config["hypernet_hidden_size"]) * 0.02,
            f"{prefix}.self_attn.k_proj.weight": torch.randn(config["hypernet_hidden_size"], config["hypernet_hidden_size"]) * 0.02,
            f"{prefix}.self_attn.v_proj.weight": torch.randn(config["hypernet_hidden_size"], config["hypernet_hidden_size"]) * 0.02,
            f"{prefix}.self_attn.o_proj.weight": torch.randn(config["hypernet_hidden_size"], config["hypernet_hidden_size"]) * 0.02,
            f"{prefix}.mlp.fc1.weight": torch.randn(config["hypernet_hidden_size"] * 4, config["hypernet_hidden_size"]) * 0.02,
            f"{prefix}.mlp.fc2.weight": torch.randn(config["hypernet_hidden_size"], config["hypernet_hidden_size"] * 4) * 0.02,
            f"{prefix}.norm1.weight": torch.ones(config["hypernet_hidden_size"]),
            f"{prefix}.norm2.weight": torch.ones(config["hypernet_hidden_size"]),
        })
    
    # Add output projections for LoRA generation
    for module in config["target_modules"]:
        hypernet_weights[f"lora_generators.{module}.weight"] = torch.randn(
            config["lora_rank"] * 2, config["hypernet_hidden_size"]
        ) * 0.02
    
    # Save weights
    save_file(hypernet_weights, hypernet_dir / "model.safetensors")
    
    print(f"Hypernet stub created at: {hypernet_dir}")
    print("This is a placeholder for testing. Replace with a trained hypernet for real use.")

if __name__ == "__main__":
    create_hypernet_stub()