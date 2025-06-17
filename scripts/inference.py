#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path
import argparse
import json
import time

class LoRAInference:
    """Inference engine with LoRA hot-swapping support."""
    
    def __init__(self, model_path, llama_cpp_path="llama.cpp"):
        self.model_path = Path(model_path)
        self.llama_cpp_path = Path(llama_cpp_path)
        self.main_binary = self.llama_cpp_path / "build" / "bin" / "llama-cli"
        
        if not self.main_binary.exists():
            raise FileNotFoundError(f"llama.cpp main binary not found at {self.main_binary}")
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        
        # Default inference parameters
        self.default_params = {
            "ctx_size": 4096,
            "n_predict": -1,
            "temp": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
            "threads": 8
        }
    
    def run_inference(self, prompt, lora_path=None, **kwargs):
        """Run inference with optional LoRA."""
        params = self.default_params.copy()
        params.update(kwargs)
        
        cmd = [
            str(self.main_binary),
            "-m", str(self.model_path),
            "--ctx-size", str(params["ctx_size"]),
            "-n", str(params["n_predict"]),
            "--temp", str(params["temp"]),
            "--top-p", str(params["top_p"]),
            "--repeat-penalty", str(params["repeat_penalty"]),
            "-t", str(params["threads"]),
            "-p", prompt
        ]
        
        # Add LoRA if specified
        if lora_path and Path(lora_path).exists():
            cmd.extend(["--lora", str(lora_path)])
            print(f"Using LoRA: {lora_path}")
        
        # Run inference
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        inference_time = time.time() - start_time
        
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return None
        
        return {
            "output": result.stdout,
            "time": inference_time,
            "lora": lora_path
        }
    
    def benchmark_lora(self, prompt, lora_paths):
        """Benchmark multiple LoRAs on the same prompt."""
        results = []
        
        # Baseline without LoRA
        print("Running baseline (no LoRA)...")
        baseline = self.run_inference(prompt)
        results.append({"name": "baseline", "result": baseline})
        
        # Test each LoRA
        for lora_path in lora_paths:
            lora_name = Path(lora_path).stem
            print(f"\nTesting LoRA: {lora_name}")
            result = self.run_inference(prompt, lora_path)
            results.append({"name": lora_name, "result": result})
        
        return results

def interactive_mode(inference_engine):
    """Interactive prompt mode with LoRA hot-swapping."""
    print("\n=== Interactive Inference Mode ===")
    print("Commands:")
    print("  /lora <path>  - Load a LoRA adapter")
    print("  /nolora       - Remove current LoRA")
    print("  /params       - Show current parameters")
    print("  /exit         - Exit interactive mode")
    print("\nEnter your prompts below:\n")
    
    current_lora = None
    
    while True:
        try:
            prompt = input("> ").strip()
            
            if not prompt:
                continue
            
            # Handle commands
            if prompt.startswith("/"):
                parts = prompt.split()
                cmd = parts[0].lower()
                
                if cmd == "/exit":
                    break
                elif cmd == "/lora" and len(parts) > 1:
                    lora_path = parts[1]
                    if Path(lora_path).exists():
                        current_lora = lora_path
                        print(f"LoRA loaded: {current_lora}")
                    else:
                        print(f"LoRA not found: {lora_path}")
                elif cmd == "/nolora":
                    current_lora = None
                    print("LoRA removed")
                elif cmd == "/params":
                    print(f"Current LoRA: {current_lora or 'None'}")
                    print(f"Model: {inference_engine.model_path}")
                else:
                    print(f"Unknown command: {cmd}")
                continue
            
            # Run inference
            result = inference_engine.run_inference(prompt, current_lora)
            if result:
                print(f"\n{result['output']}")
                print(f"\n[Inference time: {result['time']:.2f}s]")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Run inference with LoRA hot-swapping")
    parser.add_argument("--model", default="models/jan-mini-14b-q4_k_xs.gguf",
                       help="Path to quantized model")
    parser.add_argument("--lora", help="Path to LoRA adapter (GGUF format)")
    parser.add_argument("--prompt", help="Single prompt to run")
    parser.add_argument("--interactive", action="store_true",
                       help="Interactive mode with LoRA hot-swapping")
    parser.add_argument("--benchmark", nargs="+", metavar="LORA",
                       help="Benchmark multiple LoRAs")
    parser.add_argument("--ctx-size", type=int, default=4096,
                       help="Context size")
    parser.add_argument("--threads", type=int, default=8,
                       help="Number of threads")
    
    args = parser.parse_args()
    
    try:
        # Initialize inference engine
        engine = LoRAInference(args.model)
        
        if args.threads:
            engine.default_params["threads"] = args.threads
        if args.ctx_size:
            engine.default_params["ctx_size"] = args.ctx_size
        
        # Run appropriate mode
        if args.interactive:
            interactive_mode(engine)
        elif args.benchmark:
            if not args.prompt:
                print("Error: --prompt required for benchmark mode")
                sys.exit(1)
            results = engine.benchmark_lora(args.prompt, args.benchmark)
            
            # Print benchmark results
            print("\n=== Benchmark Results ===")
            for entry in results:
                name = entry["name"]
                result = entry["result"]
                if result:
                    print(f"\n{name}: {result['time']:.2f}s")
        else:
            # Single inference
            if not args.prompt:
                print("Error: --prompt or --interactive required")
                sys.exit(1)
            
            result = engine.run_inference(args.prompt, args.lora)
            if result:
                print(result["output"])
                
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()