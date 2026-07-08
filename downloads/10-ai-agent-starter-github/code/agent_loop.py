"""
agent_loop.py — Main AI Agent Loop (ReAct pattern)
==================================================

Production-ready AI agent with:
- ReAct (Reasoning + Acting) loop
- Multi-provider support (OpenAI, Anthropic, Google)
- Tool calling with retry
- Memory management
- Graceful error handling

Usage:
    python agent_loop.py
    python agent_loop.py --provider anthropic --model claude-3-5-sonnet-20241022
"""

import os
import sys
import json
import time
import argparse
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from tools import TOOL_REGISTRY
from memory import Memory


# ============================================================
# Configuration
# ============================================================

DEFAULT_CONFIG = {
    "provider": os.getenv("LLM_PROVIDER", "openai"),
    "model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
    "max_iterations": int(os.getenv("AGENT_MAX_ITERATIONS", "10")),
    "temperature": float(os.getenv("AGENT_TEMPERATURE", "0.7")),
    "system_prompt": os.getenv(
        "AGENT_SYSTEM_PROMPT",
        "คุณเป็น AI ผู้ช่วยอัจฉริยะ ตอบคำถามเป็นภาษาไทย ใช้ tools เมื่อจำเป็น"
    ),
    "memory_path": os.getenv("MEMORY_FILE", "./memory.json"),
    "verbose": os.getenv("AGENT_VERBOSE", "true").lower() == "true"
}


# ============================================================
# Provider Wrappers
# ============================================================

class LLMResponse:
    """Unified response from any LLM provider."""
    def __init__(self, text: str = "", tool_calls: List[Dict] = None,
                 input_tokens: int = 0, output_tokens: int = 0):
        self.text = text
        self.tool_calls = tool_calls or []
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens

    @property
    def has_tool_call(self) -> bool:
        return len(self.tool_calls) > 0


class LLMProvider:
    """Base class for LLM providers."""
    def complete(self, messages: List[Dict], tools: List[Dict]) -> LLMResponse:
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    def __init__(self, model: str, temperature: float = 0.7):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package not installed. Run: pip install openai")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in .env")
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def complete(self, messages, tools):
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        if tools:
            params["tools"] = [{"type": "function", "function": t} for t in tools]
            params["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**params)
        msg = response.choices[0].message

        tool_calls = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {}
                tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "args": args
                })

        return LLMResponse(
            text=msg.content or "",
            tool_calls=tool_calls,
            input_tokens=response.usage.prompt_tokens if response.usage else 0,
            output_tokens=response.usage.completion_tokens if response.usage else 0
        )


class AnthropicProvider(LLMProvider):
    def __init__(self, model: str = "claude-3-5-sonnet-20241022", temperature: float = 0.7):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in .env")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def complete(self, messages, tools):
        # Extract system message
        system = ""
        chat_msgs = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                chat_msgs.append(m)

        # Convert tools
        anthropic_tools = []
        if tools:
            for t in tools:
                anthropic_tools.append({
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "input_schema": t.get("parameters", {"type": "object", "properties": {}})
                })

        response = self.client.messages.create(
            model=self.model,
            system=system,
            messages=chat_msgs,
            tools=anthropic_tools if anthropic_tools else None,
            temperature=self.temperature,
            max_tokens=4096
        )

        text = ""
        tool_calls = []
        for block in response.content:
            if block.type == "text":
                text += block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "args": block.input
                })

        return LLMResponse(
            text=text,
            tool_calls=tool_calls,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens
        )


class GoogleProvider(LLMProvider):
    def __init__(self, model: str = "gemini-1.5-flash", temperature: float = 0.7):
        if not GOOGLE_AVAILABLE:
            raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set in .env")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.temperature = temperature

    def complete(self, messages, tools):
        # Convert messages to Gemini format
        history = []
        system = ""
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            elif m["role"] == "user":
                history.append({"role": "user", "parts": [m["content"]]})
            elif m["role"] == "assistant":
                history.append({"role": "model", "parts": [m.get("content", "") or ""]})

        # Configure tools
        gemini_tools = []
        if tools:
            for t in tools:
                gemini_tools.append(t)  # Gemini uses different format

        chat = self.model.start_chat(history=history[:-1] if len(history) > 1 else [])
        last_msg = history[-1]["parts"][0] if history else ""
        response = chat.send_message(last_msg, generation_config={"temperature": self.temperature})

        return LLMResponse(
            text=response.text,
            tool_calls=[],  # Simplified for Gemini
            input_tokens=0,
            output_tokens=0
        )


def get_provider(name: str, model: str, temperature: float) -> LLMProvider:
    if name == "openai":
        return OpenAIProvider(model=model, temperature=temperature)
    elif name == "anthropic":
        return AnthropicProvider(model=model, temperature=temperature)
    elif name == "google":
        return GoogleProvider(model=model, temperature=temperature)
    else:
        raise ValueError(f"Unknown provider: {name}")


# ============================================================
# Agent
# ============================================================

class Agent:
    """ReAct AI Agent with tool calling and memory."""

    def __init__(self, provider: str = None, model: str = None,
                 system_prompt: str = None, tools: Dict = None,
                 memory: Memory = None, config: Dict = None):
        cfg = {**DEFAULT_CONFIG, **(config or {})}
        provider_name = provider or cfg["provider"]
        self.model = model or cfg["model"]

        self.llm = get_provider(provider_name, self.model, cfg["temperature"])
        self.tools = tools or TOOL_REGISTRY
        self.tool_schemas = [t["schema"] for t in self.tools.values()]
        self.memory = memory or Memory(
            system_prompt=system_prompt or cfg["system_prompt"],
            persist_path=cfg["memory_path"]
        )
        self.max_iter = cfg["max_iterations"]
        self.verbose = cfg["verbose"]
        self.total_tokens = {"in": 0, "out": 0}

    def log(self, msg: str):
        if self.verbose:
            print(f"[Agent] {msg}", file=sys.stderr)

    def execute_tool(self, name: str, args: Dict) -> str:
        """Execute a tool with retry on failure."""
        if name not in self.tools:
            return f"Error: Tool '{name}' not found. Available: {list(self.tools.keys())}"

        tool_func = self.tools[name]["function"]
        self.log(f"Tool call: {name}({args})")

        for attempt in range(3):
            try:
                result = tool_func(**args)
                result_str = str(result)
                self.log(f"Tool result: {result_str[:200]}")
                return result_str
            except Exception as e:
                self.log(f"Tool error (attempt {attempt+1}): {e}")
                if attempt == 2:
                    return f"Error executing {name}: {str(e)}"
                time.sleep(0.5 * (attempt + 1))
        return "Tool execution failed"

    def run(self, user_message: str, user_id: str = "default") -> str:
        """Run agent loop until final answer."""
        # Load user history if exists
        self.memory.load_user(user_id)
        self.memory.add("user", user_message)

        for iteration in range(self.max_iter):
            self.log(f"=== Iteration {iteration + 1}/{self.max_iter} ===")

            # 1. Get LLM response
            try:
                response = self.llm.complete(self.memory.messages, self.tool_schemas)
                self.total_tokens["in"] += response.input_tokens
                self.total_tokens["out"] += response.output_tokens
            except Exception as e:
                self.log(f"LLM error: {e}")
                return f"ขออภัย เกิดข้อผิดพลาด: {str(e)}"

            # 2. Check if LLM wants to use tool
            if response.has_tool_call:
                # Add assistant's tool call to memory
                self.memory.add_assistant_with_tools(response.text, response.tool_calls)

                # 3. Execute each tool call
                for tc in response.tool_calls:
                    result = self.execute_tool(tc["name"], tc["args"])
                    self.memory.add_tool_result(tc["id"], result)

                # Continue loop — LLM will see tool results
                continue

            # 4. Final answer
            final = response.text.strip()
            if not final:
                final = "ขออภัย ไม่สามารถตอบได้ในขณะนี้ค่ะ"

            self.memory.add("assistant", final)
            self.memory.save_user(user_id)

            self.log(f"Final: {final[:200]}")
            self.log(f"Tokens: {self.total_tokens}")
            return final

        # Max iterations reached
        self.log("Max iterations reached")
        return "ขออภัย การค้นหาข้อมูลนานเกินไป กรุณาถามใหม่ค่ะ"


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="AI Agent CLI")
    parser.add_argument("--provider", choices=["openai", "anthropic", "google"],
                        help="LLM provider")
    parser.add_argument("--model", help="Model name")
    parser.add_argument("--system", help="Path to system prompt file")
    parser.add_argument("--user", default="default", help="User ID for memory")
    parser.add_argument("--no-verbose", action="store_true", help="Disable verbose logging")
    args = parser.parse_args()

    # Load system prompt
    system_prompt = None
    if args.system and os.path.exists(args.system):
        with open(args.system) as f:
            system_prompt = f.read()
        print(f"Loaded system prompt: {args.system}")

    # Initialize agent
    config = {"verbose": not args.no_verbose}
    if system_prompt:
        config["system_prompt"] = system_prompt

    agent = Agent(
        provider=args.provider,
        model=args.model,
        config=config
    )

    # Interactive loop
    provider_name = args.provider or DEFAULT_CONFIG["provider"]
    model_name = args.model or DEFAULT_CONFIG["model"]
    print(f"\n🤖 AI Agent ({provider_name}/{model_name})")
    print("Commands: 'exit' = quit, 'clear' = clear memory, 'tokens' = show usage")
    print("-" * 50)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Bye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            print("👋 Bye!")
            break
        if user_input.lower() == "clear":
            agent.memory.clear()
            print("🗑️ Memory cleared")
            continue
        if user_input.lower() == "tokens":
            print(f"Tokens used: {agent.total_tokens}")
            continue

        print("\nAgent: ", end="", flush=True)
        response = agent.run(user_input, user_id=args.user)
        print(response)


if __name__ == "__main__":
    main()
