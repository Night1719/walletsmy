"""
Dynamic instruction management system.
Allows adding new instructions without code changes.
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class InstructionManager:
    """Manages instruction files and metadata dynamically"""
    
    def __init__(self, instructions_dir: str = "instructions", config_file: str = "instructions_config.json"):
        self.instructions_dir = Path(instructions_dir)
        self.config_file = Path(config_file)
        self.instructions_dir.mkdir(exist_ok=True)
        
        # Load or create configuration
        self.config = self._load_config()
        
        # Ensure required structure
        self._ensure_structure()
    
    def _load_config(self) -> Dict:
        """Load instructions configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return self._default_config()
        else:
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Create default configuration"""
        return {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "categories": {
                "1c": {
                    "name": "1С",
                    "icon": "🔧",
                    "description": "Инструкции по работе с 1С",
                    "instructions": {
                        "ar2": {
                            "name": "AR2",
                            "description": "Инструкция по AR2",
                            "files": {
                                "pdf": "1c/ar2.pdf",
                                "docx": "1c/ar2.docx"
                            }
                        },
                        "dm": {
                            "name": "DM", 
                            "description": "Инструкция по DM",
                            "files": {
                                "pdf": "1c/dm.pdf",
                                "docx": "1c/dm.docx"
                            }
                        }
                    }
                },
                "email": {
                    "name": "Почта",
                    "icon": "📧",
                    "description": "Настройка почты на различных устройствах",
                    "instructions": {
                        "iphone": {
                            "name": "iPhone",
                            "description": "Настройка почты на iPhone",
                            "files": {
                                "pdf": "email/iphone.pdf",
                                "docx": "email/iphone.docx"
                            }
                        },
                        "android": {
                            "name": "Android",
                            "description": "Настройка почты на Android",
                            "files": {
                                "pdf": "email/android.pdf",
                                "docx": "email/android.docx"
                            }
                        },
                        "outlook": {
                            "name": "Outlook",
                            "description": "Настройка Outlook",
                            "files": {
                                "pdf": "email/outlook.pdf",
                                "docx": "email/outlook.docx"
                            }
                        }
                    }
                }
            }
        }
    
    def _ensure_structure(self):
        """Ensure required directory structure exists"""
        for category_id, category in self.config["categories"].items():
            category_dir = self.instructions_dir / category_id
            category_dir.mkdir(exist_ok=True)
            
            for instruction_id, instruction in category["instructions"].items():
                instruction_dir = category_dir / instruction_id
                instruction_dir.mkdir(exist_ok=True)
    
    def _save_config(self):
        """Save configuration to file"""
        self.config["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get_categories(self) -> Dict:
        """Get all categories"""
        return self.config["categories"]
    
    def get_all_categories(self) -> List[Dict]:
        """Get all categories as list"""
        categories = self.config.get("categories", {})
        result = []
        for cat_id, cat_data in categories.items():
            result.append({
                "id": cat_id,
                "name": cat_data.get("name", ""),
                "icon": cat_data.get("icon", "📁"),
                "description": cat_data.get("description", "")
            })
        return result
    
    def get_category(self, category_id: str) -> Optional[Dict]:
        """Get specific category"""
        return self.config["categories"].get(category_id)
    
    def get_instructions(self, category_id: str) -> Dict:
        """Get all instructions in category"""
        category = self.get_category(category_id)
        return category["instructions"] if category else {}
    
    def get_instructions_by_category(self, category_id: str) -> List[Dict]:
        """Get all instructions in category as list"""
        instructions = self.get_instructions(category_id)
        result = []
        for inst_id, inst_data in instructions.items():
            # Add formats list from files dict
            files = inst_data.get("files", {})
            formats = list(files.keys())
            
            result.append({
                "id": inst_id,
                "name": inst_data.get("name", ""),
                "description": inst_data.get("description", ""),
                "formats": formats
            })
        return result
    
    def get_instruction(self, category_id: str, instruction_id: str) -> Optional[Dict]:
        """Get specific instruction"""
        instructions = self.get_instructions(category_id)
        instruction = instructions.get(instruction_id)
        if instruction:
            # Add formats list from files dict
            files = instruction.get("files", {})
            instruction["formats"] = list(files.keys())
        return instruction
    
    def add_category(self, category_id: str, name: str, icon: str, description: str = "") -> bool:
        """Add new category"""
        try:
            if category_id in self.config["categories"]:
                logger.warning(f"Category {category_id} already exists")
                return False
            
            self.config["categories"][category_id] = {
                "name": name,
                "icon": icon,
                "description": description,
                "instructions": {}
            }
            
            # Create directory
            (self.instructions_dir / category_id).mkdir(exist_ok=True)
            
            self._save_config()
            logger.info(f"Category {category_id} added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error adding category {category_id}: {e}")
            return False
    
    def add_instruction(self, category_id: str, instruction_id: str, name: str, 
                       description: str = "", files: Dict[str, str] = None) -> bool:
        """Add new instruction to category"""
        try:
            if category_id not in self.config["categories"]:
                logger.error(f"Category {category_id} does not exist")
                return False
            
            if instruction_id in self.config["categories"][category_id]["instructions"]:
                logger.warning(f"Instruction {instruction_id} already exists in category {category_id}")
                return False
            
            self.config["categories"][category_id]["instructions"][instruction_id] = {
                "name": name,
                "description": description,
                "files": files or {}
            }
            
            # Create directory
            (self.instructions_dir / category_id / instruction_id).mkdir(exist_ok=True)
            
            self._save_config()
            logger.info(f"Instruction {instruction_id} added to category {category_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding instruction {instruction_id}: {e}")
            return False
    
    def update_instruction(self, category_id: str, instruction_id: str, 
                          name: str = None, description: str = None, 
                          files: Dict[str, str] = None) -> bool:
        """Update existing instruction"""
        try:
            instruction = self.get_instruction(category_id, instruction_id)
            if not instruction:
                logger.error(f"Instruction {instruction_id} not found in category {category_id}")
                return False
            
            if name is not None:
                instruction["name"] = name
            if description is not None:
                instruction["description"] = description
            if files is not None:
                instruction["files"].update(files)
            
            self._save_config()
            logger.info(f"Instruction {instruction_id} updated in category {category_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating instruction {instruction_id}: {e}")
            return False
    
    def remove_instruction(self, category_id: str, instruction_id: str) -> bool:
        """Remove instruction from category"""
        try:
            if category_id not in self.config["categories"]:
                logger.error(f"Category {category_id} does not exist")
                return False
            
            if instruction_id not in self.config["categories"][category_id]["instructions"]:
                logger.error(f"Instruction {instruction_id} not found in category {category_id}")
                return False
            
            del self.config["categories"][category_id]["instructions"][instruction_id]
            self._save_config()
            logger.info(f"Instruction {instruction_id} removed from category {category_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing instruction {instruction_id}: {e}")
            return False
    
    def add_file(self, category_id: str, instruction_id: str, 
                file_format: str, file_path: str) -> bool:
        """Add file to instruction"""
        try:
            instruction = self.get_instruction(category_id, instruction_id)
            if not instruction:
                logger.error(f"Instruction {instruction_id} not found in category {category_id}")
                return False
            
            # Validate file exists
            full_path = self.instructions_dir / file_path
            if not full_path.exists():
                logger.error(f"File {file_path} does not exist")
                return False
            
            # Add file to instruction
            instruction["files"][file_format] = file_path
            self._save_config()
            logger.info(f"File {file_format} added to instruction {instruction_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding file {file_format} to instruction {instruction_id}: {e}")
            return False
    
    def remove_file(self, category_id: str, instruction_id: str, file_format: str) -> bool:
        """Remove file from instruction"""
        try:
            instruction = self.get_instruction(category_id, instruction_id)
            if not instruction:
                logger.error(f"Instruction {instruction_id} not found in category {category_id}")
                return False
            
            if file_format not in instruction["files"]:
                logger.error(f"File format {file_format} not found in instruction {instruction_id}")
                return False
            
            del instruction["files"][file_format]
            self._save_config()
            logger.info(f"File {file_format} removed from instruction {instruction_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing file {file_format} from instruction {instruction_id}: {e}")
            return False
    
    def get_available_files(self, category_id: str, instruction_id: str) -> List[Dict]:
        """Get available files for instruction with existence check"""
        instruction = self.get_instruction(category_id, instruction_id)
        if not instruction:
            return []
        
        available_files = []
        for file_format, file_path in instruction["files"].items():
            full_path = self.instructions_dir / file_path
            if full_path.exists():
                file_size = full_path.stat().st_size
                available_files.append({
                    "format": file_format,
                    "path": file_path,
                    "size": file_size,
                    "exists": True
                })
            else:
                available_files.append({
                    "format": file_format,
                    "path": file_path,
                    "size": 0,
                    "exists": False
                })
        
        return available_files
    
    def get_file_path(self, category_id: str, instruction_id: str, file_format: str) -> Optional[Path]:
        """Get full path to instruction file"""
        instruction = self.get_instruction(category_id, instruction_id)
        if not instruction or file_format not in instruction["files"]:
            return None
        
        file_path = self.instructions_dir / instruction["files"][file_format]
        return file_path if file_path.exists() else None
    
    def validate_structure(self) -> List[str]:
        """Validate instruction structure and return issues"""
        issues = []
        
        for category_id, category in self.config["categories"].items():
            category_dir = self.instructions_dir / category_id
            if not category_dir.exists():
                issues.append(f"Category directory {category_id} does not exist")
                continue
            
            for instruction_id, instruction in category["instructions"].items():
                instruction_dir = category_dir / instruction_id
                if not instruction_dir.exists():
                    issues.append(f"Instruction directory {category_id}/{instruction_id} does not exist")
                
                for file_format, file_path in instruction["files"].items():
                    full_path = self.instructions_dir / file_path
                    if not full_path.exists():
                        issues.append(f"File {file_path} does not exist")
        
        return issues
    
    def export_config(self) -> Dict:
        """Export current configuration"""
        return self.config.copy()
    
    def import_config(self, config: Dict) -> bool:
        """Import configuration from dict"""
        try:
            self.config = config
            self._ensure_structure()
            self._save_config()
            logger.info("Configuration imported successfully")
            return True
        except Exception as e:
            logger.error(f"Error importing configuration: {e}")
            return False

# Global instance
instruction_manager = None

def init_instruction_manager(instructions_dir: str = "instructions", config_file: str = "instructions_config.json"):
    """Initialize the global instruction manager"""
    global instruction_manager
    instruction_manager = InstructionManager(instructions_dir, config_file)
    logger.info(f"Instruction manager initialized with directory: {instructions_dir}")

def get_instruction_manager() -> InstructionManager:
    """Get the global instruction manager instance"""
    if instruction_manager is None:
        raise RuntimeError("Instruction manager not initialized")
    return instruction_manager