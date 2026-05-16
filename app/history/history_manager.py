from typing import List

class HistoryManager:
    def __init__(self, max_size: int = 50):
        self._undo_stack: List[list] = []
        self._redo_stack: List[list] = []
        self._max_size = max_size
    
    def push(self, state:list) -> None:
        self._undo_stack.append(state)
        self._redo_stack.clear()
        if len(self._undo_stack) > self._max_size:
            self._undo_stack.pop(0) 
    
    def undo(self, current_state: list):
        if not self._undo_stack:
            return None
        self._redo_stack.append(current_state)
        return self._undo_stack.pop() 
    
    def redo(self, current_state: list):
        if not self._redo_stack:
            return None 
        self._undo_stack.append(current_state)
        return self._redo_stack.pop() 
    
    def redo(self, current_state:list):
        if not self._redo_stack:
            return None
        self._undo_stack.append(current_state)
        return self._redo_stack.pop()
    
    @property
    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0 
    
    @property
    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0