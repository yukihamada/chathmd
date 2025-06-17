#!/usr/bin/env python3
"""Learning Data Manager for Text-to-LoRA training"""

import json
import os
from datetime import datetime
from pathlib import Path
import hashlib

class LearningDataManager:
    """Manages learning data in optimal format for Text-to-LoRA training"""
    
    def __init__(self, data_dir="learning_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different data types
        (self.data_dir / "conversations").mkdir(exist_ok=True)
        (self.data_dir / "feedback").mkdir(exist_ok=True)
        (self.data_dir / "training_pairs").mkdir(exist_ok=True)
        (self.data_dir / "task_descriptions").mkdir(exist_ok=True)
    
    def save_feedback_pair(self, original_response, feedback_data, conversation_context=None):
        """
        Save feedback in the optimal format for Text-to-LoRA training.
        
        Format based on best practices for instruction tuning:
        - Input: Context + Original Response + Feedback Type
        - Output: Improved Response Direction
        """
        
        # Generate unique ID for this feedback pair
        feedback_id = hashlib.md5(
            f"{original_response}{feedback_data['timestamp']}".encode()
        ).hexdigest()[:8]
        
        # Create task description from feedback
        task_description = self._generate_task_description(feedback_data)
        
        # Create training pair
        training_pair = {
            "id": feedback_id,
            "timestamp": feedback_data["timestamp"],
            "task_type": feedback_data["improvement_type"],
            "input": {
                "context": conversation_context or "",
                "original_response": original_response,
                "user_feedback": feedback_data["improvement_text"],
                "rating": feedback_data["rating"],
                "qualities": feedback_data.get("good_qualities", [])
            },
            "target_style": {
                "improvement_direction": feedback_data["improvement_type"],
                "specific_guidance": feedback_data["improvement_text"],
                "ideal_example": feedback_data.get("ideal_example", ""),
                "desired_qualities": feedback_data.get("good_qualities", [])
            },
            "metadata": {
                "is_custom_feedback": feedback_data.get("is_custom", False),
                "conversation_length": len(conversation_context.split()) if conversation_context else 0,
                "response_length": len(original_response.split())
            }
        }
        
        # Save training pair
        pair_file = self.data_dir / "training_pairs" / f"{feedback_id}.json"
        with open(pair_file, 'w', encoding='utf-8') as f:
            json.dump(training_pair, f, ensure_ascii=False, indent=2)
        
        # Save task description for Text-to-LoRA
        task_file = self.data_dir / "task_descriptions" / f"{feedback_id}_task.txt"
        with open(task_file, 'w', encoding='utf-8') as f:
            f.write(task_description)
        
        # Update master index
        self._update_master_index(feedback_id, training_pair)
        
        return feedback_id, task_description
    
    def _generate_task_description(self, feedback_data):
        """Generate natural language task description for Text-to-LoRA"""
        
        improvement_type = feedback_data["improvement_type"]
        improvement_text = feedback_data["improvement_text"]
        rating = feedback_data["rating"]
        
        # Base task templates
        task_templates = {
            "📚 より詳しく・具体的に": [
                "具体例やデータを含めた詳細な説明を提供する",
                "専門的な情報を豊富に含めて回答する", 
                "実例や数字を使って詳しく説明する"
            ],
            "🎯 簡潔で要点を絞って": [
                "重要なポイントだけに絞った簡潔な回答をする",
                "結論を先に述べて要点を整理して答える",
                "短く分かりやすくまとめて回答する"
            ],
            "💡 初心者向けに優しく": [
                "専門用語を避けて誰でも理解できるように説明する",
                "比喩や例え話を使って分かりやすく教える",
                "初心者の目線に立った優しい説明をする"
            ],
            "custom": [
                "ユーザーの具体的な要求に応じた回答スタイルを身につける"
            ]
        }
        
        # Select base template
        if improvement_type in task_templates:
            base_tasks = task_templates[improvement_type]
            base_task = base_tasks[0]  # Use first template as base
        else:
            base_task = "ユーザーの期待に沿った回答スタイルを身につける"
        
        # Enhance with specific feedback
        if improvement_text and improvement_text.strip():
            if feedback_data.get("is_custom", False):
                task_description = f"{improvement_text}という要求に応じた回答をする"
            else:
                task_description = f"{base_task}。特に{improvement_text}を重視して回答する"
        else:
            task_description = base_task
        
        # Add quality indicators
        qualities = feedback_data.get("good_qualities", [])
        if qualities:
            quality_text = "、".join(qualities)
            task_description += f"。{quality_text}な特徴を保ちながら改善する"
        
        return task_description
    
    def _update_master_index(self, feedback_id, training_pair):
        """Update master index for efficient data retrieval"""
        
        index_file = self.data_dir / "master_index.json"
        
        # Load existing index
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
        else:
            index = {
                "total_feedback": 0,
                "by_type": {},
                "by_rating": {},
                "entries": []
            }
        
        # Update statistics
        index["total_feedback"] += 1
        
        improvement_type = training_pair["task_type"]
        if improvement_type not in index["by_type"]:
            index["by_type"][improvement_type] = 0
        index["by_type"][improvement_type] += 1
        
        rating = training_pair["input"]["rating"]
        if str(rating) not in index["by_rating"]:
            index["by_rating"][str(rating)] = 0
        index["by_rating"][str(rating)] += 1
        
        # Add entry
        index["entries"].append({
            "id": feedback_id,
            "timestamp": training_pair["timestamp"],
            "type": improvement_type,
            "rating": rating,
            "is_custom": training_pair["metadata"]["is_custom_feedback"]
        })
        
        # Save updated index
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    
    def get_training_dataset(self, min_rating=3, max_samples=None):
        """Get training dataset in format suitable for Text-to-LoRA"""
        
        training_data = []
        
        # Load all training pairs
        pairs_dir = self.data_dir / "training_pairs"
        if not pairs_dir.exists():
            return training_data
        
        for pair_file in pairs_dir.glob("*.json"):
            with open(pair_file, 'r', encoding='utf-8') as f:
                pair_data = json.load(f)
            
            # Filter by rating
            if pair_data["input"]["rating"] >= min_rating:
                # Format for Text-to-LoRA training
                training_sample = {
                    "task_description": self._load_task_description(pair_data["id"]),
                    "input_text": pair_data["input"]["original_response"],
                    "target_style": pair_data["target_style"]["improvement_direction"],
                    "guidance": pair_data["target_style"]["specific_guidance"],
                    "context": pair_data["input"]["context"],
                    "metadata": pair_data["metadata"]
                }
                training_data.append(training_sample)
        
        # Sort by timestamp (most recent first)
        training_data.sort(key=lambda x: x["metadata"]["timestamp"] if "timestamp" in x["metadata"] else "", reverse=True)
        
        # Limit samples if requested
        if max_samples and len(training_data) > max_samples:
            training_data = training_data[:max_samples]
        
        return training_data
    
    def _load_task_description(self, feedback_id):
        """Load task description for a feedback ID"""
        task_file = self.data_dir / "task_descriptions" / f"{feedback_id}_task.txt"
        if task_file.exists():
            with open(task_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        return ""
    
    def export_for_text_to_lora(self, output_file="text_to_lora_dataset.json"):
        """Export data in Text-to-LoRA training format"""
        
        training_data = self.get_training_dataset()
        
        # Format for Text-to-LoRA
        export_data = {
            "dataset_info": {
                "name": "chatHMD_feedback_dataset",
                "description": "User feedback data for Text-to-LoRA training",
                "total_samples": len(training_data),
                "created_at": datetime.now().isoformat()
            },
            "training_samples": []
        }
        
        for sample in training_data:
            formatted_sample = {
                "task": sample["task_description"],
                "input": sample["input_text"],
                "target_style": sample["target_style"],
                "guidance": sample["guidance"],
                "context": sample["context"]
            }
            export_data["training_samples"].append(formatted_sample)
        
        # Save export file
        output_path = self.data_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def get_statistics(self):
        """Get statistics about collected learning data"""
        
        index_file = self.data_dir / "master_index.json"
        if not index_file.exists():
            return {"total_feedback": 0, "by_type": {}, "by_rating": {}}
        
        with open(index_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def clean_old_data(self, days_old=30):
        """Clean old training data to save space"""
        
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # Clean old training pairs
        pairs_dir = self.data_dir / "training_pairs"
        cleaned_count = 0
        
        for pair_file in pairs_dir.glob("*.json"):
            try:
                with open(pair_file, 'r', encoding='utf-8') as f:
                    pair_data = json.load(f)
                
                timestamp = datetime.fromisoformat(pair_data["timestamp"])
                if timestamp < cutoff_date:
                    pair_file.unlink()
                    # Also remove corresponding task file
                    task_file = self.data_dir / "task_descriptions" / f"{pair_data['id']}_task.txt"
                    if task_file.exists():
                        task_file.unlink()
                    cleaned_count += 1
            except:
                continue
        
        return cleaned_count