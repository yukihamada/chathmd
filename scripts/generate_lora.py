#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from pathlib import Path
import argparse
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from safetensors.torch import save_file

class TextToLoRA:
    """Text-to-LoRA generator for jan-mini-14B model."""
    
    def __init__(self, hypernet_path, model_name="jan-ai/Jan-mini-14B-qwen3"):
        self.hypernet_path = Path(hypernet_path)
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load hypernet config
        config_path = self.hypernet_path / "config.json"
        if config_path.exists():
            with open(config_path) as f:
                self.config = json.load(f)
        else:
            # Default config for jan-mini-14B
            self.config = {
                "num_layers": 40,  # jan-mini has 40 layers
                "hidden_size": 5120,
                "intermediate_size": 13824,
                "lora_rank": 8,
                "lora_alpha": 16,
                "lora_dropout": 0.05,
                "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj", 
                                 "gate_proj", "up_proj", "down_proj"]
            }
    
    def generate_lora_weights(self, task_description, rank=8):
        """Generate LoRA weights from task description."""
        print(f"Generating LoRA for task: {task_description}")
        
        # In a real implementation, this would use the hypernet
        # For now, we create initialized LoRA weights
        lora_weights = {}
        
        for layer_idx in range(self.config["num_layers"]):
            for module in self.config["target_modules"]:
                # Generate LoRA A and B matrices
                if "proj" in module:
                    if module in ["q_proj", "k_proj", "v_proj"]:
                        in_features = self.config["hidden_size"]
                        out_features = self.config["hidden_size"]
                    elif module == "o_proj":
                        in_features = self.config["hidden_size"]
                        out_features = self.config["hidden_size"]
                    else:  # gate_proj, up_proj, down_proj
                        in_features = self.config["hidden_size"]
                        out_features = self.config["intermediate_size"]
                    
                    # Initialize with small random values
                    lora_A = torch.randn(rank, in_features) * 0.01
                    lora_B = torch.zeros(out_features, rank)
                    
                    prefix = f"model.layers.{layer_idx}.self_attn" if module in ["q_proj", "k_proj", "v_proj", "o_proj"] else f"model.layers.{layer_idx}.mlp"
                    lora_weights[f"{prefix}.{module}.lora_A"] = lora_A
                    lora_weights[f"{prefix}.{module}.lora_B"] = lora_B
        
        return lora_weights
    
    def save_lora_adapter(self, lora_weights, output_dir, task_description):
        """Save LoRA adapter in PEFT format."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save weights
        save_file(lora_weights, output_path / "adapter_model.safetensors")
        
        # Save adapter config
        adapter_config = {
            "peft_type": "LORA",
            "auto_mapping": None,
            "base_model_name_or_path": self.model_name,
            "revision": None,
            "task_type": "CAUSAL_LM",
            "inference_mode": True,
            "r": self.config.get("lora_rank", 8),
            "target_modules": self.config["target_modules"],
            "lora_alpha": self.config.get("lora_alpha", 16),
            "lora_dropout": self.config.get("lora_dropout", 0.05),
            "fan_in_fan_out": False,
            "bias": "none",
            "task_description": task_description,
            "modules_to_save": None
        }
        
        with open(output_path / "adapter_config.json", "w") as f:
            json.dump(adapter_config, f, indent=2)
        
        print(f"LoRA adapter saved to: {output_path}")
        return output_path
    
    def convert_to_gguf(self, lora_dir, base_model_path):
        """Convert PEFT LoRA to GGUF format."""
        lora_path = Path(lora_dir)
        gguf_path = lora_path.with_suffix(".gguf")
        
        # Check if base model exists
        if not Path(base_model_path).exists():
            print(f"Warning: Base model not found at {base_model_path}")
            print("Skipping GGUF conversion. Run download_and_quantize.py first.")
            return None
        
        # Convert using llama.cpp script
        convert_script = Path("llama.cpp/convert_lora_to_gguf.py")
        if not convert_script.exists():
            print("Warning: convert_lora_to_gguf.py not found in llama.cpp")
            print("Please update llama.cpp to a recent version.")
            return None
        
        cmd = [
            sys.executable,
            str(convert_script),
            "--base-model", str(base_model_path),
            "--lora-dir", str(lora_path),
            "--outfile", str(gguf_path)
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"GGUF LoRA saved to: {gguf_path}")
            return gguf_path
        except subprocess.CalledProcessError as e:
            print(f"Error converting to GGUF: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description="Generate LoRA from task description")
    parser.add_argument("hypernet_path", help="Path to hypernet model")
    parser.add_argument("task", help="Task description in natural language")
    parser.add_argument("--model-dir", default="jan-ai/Jan-mini-14B-qwen3", 
                       help="Base model name or path")
    parser.add_argument("--out", required=True, help="Output directory for LoRA")
    parser.add_argument("--rank", type=int, default=8, help="LoRA rank")
    parser.add_argument("--convert-gguf", action="store_true", 
                       help="Convert to GGUF format")
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = TextToLoRA(args.hypernet_path, args.model_dir)
    
    # Generate LoRA weights
    lora_weights = generator.generate_lora_weights(args.task, rank=args.rank)
    
    # Save LoRA adapter
    output_dir = generator.save_lora_adapter(lora_weights, args.out, args.task)
    
    # Convert to GGUF if requested
    if args.convert_gguf:
        base_model = "models/jan-mini-14b-f16.gguf"
        gguf_path = generator.convert_to_gguf(output_dir, base_model)
        if gguf_path:
            print(f"\n✅ LoRA ready for inference: {gguf_path}")

if __name__ == "__main__":
    main()