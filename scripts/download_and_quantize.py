#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path
import argparse

def run_command(cmd, cwd=None):
    """Run a shell command and handle errors."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout

def download_and_quantize():
    """Download jan-mini-14B and quantize to Q4_K_XS."""
    
    # Paths
    llama_cpp_dir = Path("llama.cpp")
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    model_name = "jan-mini-14b"
    fp16_path = models_dir / f"{model_name}-f16.gguf"
    q4_path = models_dir / f"{model_name}-q4_k_xs.gguf"
    
    # Check if already quantized
    if q4_path.exists():
        print(f"Quantized model already exists at {q4_path}")
        return str(q4_path)
    
    # Step 1: Convert HF model to GGUF
    if not fp16_path.exists():
        print("Converting HuggingFace model to GGUF...")
        cmd = [
            sys.executable,
            str(llama_cpp_dir / "convert_hf_to_gguf.py"),
            "--outfile", str(fp16_path),
            "--outtype", "f16",
            "jan-ai/Jan-mini-14B-qwen3"
        ]
        run_command(cmd)
    else:
        print(f"FP16 model already exists at {fp16_path}")
    
    # Step 2: Quantize to Q4_K_XS
    print("Quantizing to Q4_K_XS...")
    quantize_cmd = str(llama_cpp_dir / "build" / "bin" / "llama-quantize")
    if not Path(quantize_cmd).exists():
        print("Error: quantize binary not found. Please run setup.sh first.")
        sys.exit(1)
    
    cmd = [
        quantize_cmd,
        str(fp16_path),
        str(q4_path),
        "Q4_K_XS"
    ]
    run_command(cmd)
    
    # Print size comparison
    fp16_size = fp16_path.stat().st_size / (1024**3)
    q4_size = q4_path.stat().st_size / (1024**3)
    print(f"\nSize comparison:")
    print(f"FP16: {fp16_size:.1f} GB")
    print(f"Q4_K_XS: {q4_size:.1f} GB")
    print(f"Compression ratio: {fp16_size/q4_size:.1f}x")
    
    return str(q4_path)

def main():
    parser = argparse.ArgumentParser(description="Download and quantize jan-mini-14B model")
    parser.add_argument("--keep-fp16", action="store_true", help="Keep FP16 model after quantization")
    args = parser.parse_args()
    
    try:
        q4_path = download_and_quantize()
        print(f"\n✅ Success! Quantized model saved to: {q4_path}")
        
        if not args.keep_fp16:
            fp16_path = Path("models/jan-mini-14b-f16.gguf")
            if fp16_path.exists():
                print("Removing FP16 model to save space...")
                fp16_path.unlink()
                
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()