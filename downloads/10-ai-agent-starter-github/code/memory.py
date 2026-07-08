"""
memory.py — Memory management for AI Agent
==========================================

Two-tier memory:
1. Short-term: in-RAM message list (with token limit)
2. Long-term: JSON file persistence (per-user history)
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional


class Memory:
    """
    Conversation memory with short-term (context) and long-term (persistence).
    """

    def __init__(self, system_prompt: str = "", persist_path: str = "./memory.json",
                 max_tokens: int = 8000, max_messages: int = 50):
        self.system_prompt = system_prompt
        self.persist_path = persist_path
        self.max_tokens = max_tokens
        self.max_messages = max_messages
        self.messages: List[Dict] = []
        self.current_user: Optional[str] = None
        self._init_system()

    def _init_system(self):
        """Initialize with system message."""
        self.messages = [{
            "role": "system",
            "content": self.system_prompt or "คุณเป็น AI ผู้ช่วยอัจฉริยะ"
        }]

    def add(self, role: str, content: str, **kwargs):
        """Add a message to history."""
        if not content:
            return
        msg = {"role": role, "content": content}
        msg.update(kwargs)
        self.messages.append(msg)
        self._trim()

    def add_assistant_with_tools(self, text: str, tool_calls: List[Dict]):
        """Add an assistant message that contains tool calls."""
        msg = {"role": "assistant", "content": text or ""}
        # Format tool calls based on provider conventions
        msg["tool_calls"] = [
            {
                "id": tc["id"],
                "type": "function",
                "function": {
                    "name": tc["name"],
                    "arguments": json.dumps(tc.get("args", {}), ensure_ascii=False)
                }
            }
            for tc in tool_calls
        ]
        self.messages.append(msg)
        self._trim()

    def add_tool_result(self, tool_call_id: str, content: str):
        """Add a tool result message."""
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": content
        })
        self._trim()

    def _estimate_tokens(self) -> int:
        """Rough token estimation (works for both Thai and English)."""
        total = 0
        for m in self.messages:
            content = m.get("content", "") or ""
            # Thai: 1 token ≈ 1.5 chars; English: 1 token ≈ 4 chars
            thai_chars = sum(1 for c in content if 'ก' <= c <= '๛')
            other_chars = len(content) - thai_chars
            total += int(thai_chars / 1.5 + other_chars / 4)
            # Tool call overhead
            if "tool_calls" in m:
                total += 50
        return total

    def _trim(self):
        """Trim old messages if over limit."""
        # Limit by message count
        while len(self.messages) > self.max_messages:
            if len(self.messages) <= 2:
                break
            # Remove oldest non-system message
            for i, m in enumerate(self.messages):
                if m["role"] != "system":
                    self.messages.pop(i)
                    break

        # Limit by tokens
        while self._estimate_tokens() > self.max_tokens and len(self.messages) > 2:
            for i, m in enumerate(self.messages):
                if m["role"] != "system":
                    self.messages.pop(i)
                    break
            else:
                break

    def clear(self):
        """Clear all messages (keep system)."""
        self._init_system()

    def get_summary(self) -> str:
        """Get a text summary of the conversation."""
        lines = [f"[{m['role']}] {m.get('content', '')[:100]}" for m in self.messages[:10]]
        return "\n".join(lines)

    def save_user(self, user_id: str):
        """Persist current conversation for a user."""
        if not user_id:
            return
        try:
            data = {}
            if os.path.exists(self.persist_path):
                with open(self.persist_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

            users = data.get("users", {})
            user_data = users.get(user_id, {
                "first_seen": datetime.now().isoformat(),
                "preferences": {},
                "history": []
            })

            # Save recent messages (excluding system)
            recent = [m for m in self.messages if m["role"] != "system"][-20:]
            user_data["history"].append({
                "timestamp": datetime.now().isoformat(),
                "messages": recent
            })
            user_data["last_seen"] = datetime.now().isoformat()

            # Keep only last 50 conversations per user
            user_data["history"] = user_data["history"][-50:]

            users[user_id] = user_data
            data["users"] = users
            data["last_updated"] = datetime.now().isoformat()

            os.makedirs(os.path.dirname(self.persist_path) or ".", exist_ok=True)
            with open(self.persist_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Memory] Save error: {e}")

    def load_user(self, user_id: str):
        """Load a user's conversation history."""
        if not user_id or not os.path.exists(self.persist_path):
            return
        try:
            with open(self.persist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            users = data.get("users", {})
            if user_id not in users:
                return
            history = users[user_id].get("history", [])
            if not history:
                return
            # Restore the most recent conversation
            last_conv = history[-1]
            self._init_system()  # reset but keep system
            for m in last_conv.get("messages", []):
                if m["role"] != "system":
                    self.messages.append(m)
            self.current_user = user_id
        except Exception as e:
            print(f"[Memory] Load error: {e}")


if __name__ == "__main__":
    # Quick test
    mem = Memory(system_prompt="คุณเป็น AI")
    mem.add("user", "สวัสดี")
    mem.add("assistant", "สวัสดีครับ")
    mem.add_tool_result("call_1", "Result text")
    print(f"Messages: {len(mem.messages)}")
    print(f"Estimated tokens: {mem._estimate_tokens()}")
    print("Summary:", mem.get_summary())
