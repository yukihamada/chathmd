#!/usr/bin/env python3
"""
Simple test handler for RunPod - Returns realistic responses without actual model
"""

import runpod
import random
import time

# Predefined responses for testing
RESPONSES = [
    "I'm Wisbee, your AI assistant powered by the jan-nano XS model. This revolutionary model provides GPT-3.5 level performance in just 7.5GB, making it perfect for local deployment while maintaining your privacy.",
    
    "That's a great question! With the jan-nano XS model and Q4_K_XS quantization, I can provide fast, accurate responses while running entirely on your local hardware. No data ever leaves your device.",
    
    "The Text-to-LoRA technology I use allows me to learn from your feedback in real-time. When you rate my responses, I can adapt and improve to better serve your needs, all while keeping your data completely private.",
    
    "I'm designed with privacy as my top priority. Unlike cloud-based AI services, I process everything locally on your device. This means your conversations, personal information, and data never leave your computer.",
    
    "The jan-nano XS model I'm based on represents a breakthrough in AI efficiency. Using advanced quantization techniques, it achieves 3-5x faster inference speeds compared to traditional models while maintaining high quality outputs.",
    
    "I can help you with a wide variety of tasks - from answering questions and explaining complex topics to helping with creative writing and problem-solving. What would you like to explore today?",
    
    "One of my unique features is continuous learning through Text-to-LoRA. This means I can adapt to your communication style and preferences over time, creating a more personalized experience just for you.",
    
    "Running AI locally has many advantages: complete privacy, no internet requirement, zero latency, and full control over your data. Plus, with the efficient jan-nano XS model, you get all this without sacrificing performance.",
]

def handler(job):
    """
    Test handler that returns realistic responses
    """
    try:
        # Get job input
        job_input = job["input"]
        prompt = job_input.get("prompt", "")
        max_tokens = job_input.get("max_tokens", 500)
        temperature = job_input.get("temperature", 0.8)
        
        # Simulate processing time (0.5-2 seconds)
        processing_time = random.uniform(0.5, 2.0)
        time.sleep(processing_time)
        
        # Select a response based on prompt keywords
        response = select_response(prompt)
        
        # Add some variation based on temperature
        if temperature > 0.9 and random.random() < 0.3:
            response += "\n\nIs there anything specific you'd like to know more about?"
        
        # Simulate token count
        tokens = len(response.split())
        
        return {
            "response": response,
            "model": "jan-nano-xs",
            "tokens_generated": tokens,
            "inference_time": round(processing_time, 2),
            "status": "success"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }

def select_response(prompt):
    """Select appropriate response based on prompt"""
    prompt_lower = prompt.lower()
    
    # Check for specific topics
    if any(word in prompt_lower for word in ["privacy", "private", "secure", "data"]):
        return RESPONSES[3]  # Privacy-focused response
    
    elif any(word in prompt_lower for word in ["learn", "feedback", "improve", "adapt"]):
        return RESPONSES[2]  # Learning/LoRA response
    
    elif any(word in prompt_lower for word in ["model", "jan-nano", "xs", "technical"]):
        return RESPONSES[4]  # Technical response
    
    elif any(word in prompt_lower for word in ["hello", "hi", "introduce", "who are you"]):
        return RESPONSES[0]  # Introduction
    
    elif any(word in prompt_lower for word in ["help", "can you", "what can"]):
        return RESPONSES[5]  # Capabilities
    
    elif any(word in prompt_lower for word in ["local", "offline", "device"]):
        return RESPONSES[7]  # Local advantages
    
    else:
        # Return random response for general queries
        return random.choice(RESPONSES)

# Start RunPod serverless handler
print("Starting Wisbee test handler...")
runpod.serverless.start({"handler": handler})