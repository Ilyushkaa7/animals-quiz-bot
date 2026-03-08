import json
import os
from typing import Dict, Any

class UserDB:
    def __init__(self, file_path="users.json"):
        self.file_path = file_path
        self.data = self._load()
    
    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get_user(self, user_id: int) -> dict:
        user_id = str(user_id)
        if user_id not in self.data:
            self.data[user_id] = {
                "score": 0,
                "lives": 3,
                "in_game": False,
                "current_animal": None,
                "attempts": 0,
                "rifle_available": True,  # Винтовка доступна в каждом раунде
                "rifle_used": False        # Использована ли в текущем раунде
            }
            self._save()
        return self.data[user_id]
    
    def update_user(self, user_id: int, **kwargs):
        user_id = str(user_id)
        if user_id not in self.data:
            self.get_user(user_id)
        self.data[user_id].update(kwargs)
        self._save()
    
    def reset_game(self, user_id: int):
        user_id = str(user_id)
        if user_id in self.data:
            self.data[user_id].update({
                "in_game": False,
                "current_animal": None,
                "attempts": 0,
                "rifle_used": False
            })
            self._save()
    
    def new_round(self, user_id: int):
        """Сбрасывает использование винтовки для нового раунда"""
        user_id = str(user_id)
        if user_id in self.data:
            self.data[user_id]["rifle_used"] = False
            self._save()