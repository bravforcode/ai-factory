"""
test_agent.py — Unit tests for AI Agent
=========================================

Run: pytest tests/test_agent.py
Or:  python tests/test_agent.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import Mock, patch

from tools import calculator, read_file, list_tools
from memory import Memory


class TestTools(unittest.TestCase):
    def test_calculator_basic(self):
        result = calculator("2 + 2")
        self.assertEqual(result, "4")

    def test_calculator_complex(self):
        result = calculator("10 * 5 - 3")
        self.assertEqual(result, "47")

    def test_calculator_invalid_chars(self):
        result = calculator("__import__('os').system('rm -rf /')")
        self.assertIn("Error", result)

    def test_calculator_division_by_zero(self):
        result = calculator("1/0")
        # Should return error, not crash
        self.assertIn("Error", result)

    def test_read_file_safety(self):
        # Should refuse to read system files
        result = read_file("/etc/passwd")
        self.assertIn("Error", result)

    def test_list_tools(self):
        tools = list_tools()
        self.assertIn("calculator", tools)
        self.assertIn("read_file", tools)
        self.assertIn("web_search", tools)
        self.assertIn("send_email", tools)


class TestMemory(unittest.TestCase):
    def setUp(self):
        self.mem = Memory(system_prompt="test prompt", persist_path="/tmp/test_memory.json")

    def tearDown(self):
        if os.path.exists("/tmp/test_memory.json"):
            os.remove("/tmp/test_memory.json")

    def test_init_has_system(self):
        self.assertEqual(len(self.mem.messages), 1)
        self.assertEqual(self.mem.messages[0]["role"], "system")

    def test_add_message(self):
        self.mem.add("user", "hello")
        self.mem.add("assistant", "hi")
        self.assertEqual(len(self.mem.messages), 3)

    def test_clear(self):
        self.mem.add("user", "hello")
        self.mem.clear()
        self.assertEqual(len(self.mem.messages), 1)
        self.assertEqual(self.mem.messages[0]["role"], "system")

    def test_token_estimation(self):
        self.mem.add("user", "สวัสดีครับ" * 100)
        tokens = self.mem._estimate_tokens()
        self.assertGreater(tokens, 0)

    def test_save_load(self):
        self.mem.add("user", "test message")
        self.mem.save_user("test_user")

        mem2 = Memory(persist_path="/tmp/test_memory.json")
        mem2.load_user("test_user")
        # Should have system + restored messages
        self.assertGreaterEqual(len(mem2.messages), 1)


class TestAgentStructure(unittest.TestCase):
    def test_agent_module_imports(self):
        """Just test that modules import without error."""
        try:
            import agent_loop
            self.assertTrue(hasattr(agent_loop, "Agent"))
            self.assertTrue(hasattr(agent_loop, "OpenAIProvider"))
            self.assertTrue(hasattr(agent_loop, "AnthropicProvider"))
            self.assertTrue(hasattr(agent_loop, "GoogleProvider"))
        except ImportError as e:
            self.fail(f"agent_loop module import failed: {e}")


if __name__ == "__main__":
    unittest.main()
