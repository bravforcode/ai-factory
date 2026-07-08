"""
tools.py — Tool registry for AI Agent
======================================

4 sample tools:
1. web_search - Search the web (uses DuckDuckGo - free, no API key)
2. calculator - Math calculations (uses sympy if available)
3. read_file - Read local files (with safety checks)
4. send_email - Send email via SMTP

To add a new tool:
1. Define function with type hints + docstring
2. Add to TOOL_REGISTRY with schema
"""

import os
import re
import json
import smtplib
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List


# ============================================================
# Tool 1: Web Search (DuckDuckGo - free)
# ============================================================

def web_search(query: str, num_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo (free, no API key needed).

    Args:
        query: Search query (any language)
        num_results: Number of results to return (1-10)

    Returns:
        JSON string with search results
    """
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))
            if not results:
                return json.dumps({"results": [], "message": "No results found"}, ensure_ascii=False)
            output = []
            for r in results[:num_results]:
                output.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "url": r.get("href", "")
                })
            return json.dumps({"query": query, "results": output}, ensure_ascii=False, indent=2)
    except ImportError:
        return json.dumps({
            "error": "duckduckgo-search not installed. Run: pip install duckduckgo-search"
        })
    except Exception as e:
        return json.dumps({"error": f"Search failed: {str(e)}"})


# ============================================================
# Tool 2: Calculator
# ============================================================

def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression safely.

    Args:
        expression: Math expression like "2+2", "sqrt(16)", "log(100)"

    Returns:
        Result as string
    """
    try:
        # Try with sympy for advanced math
        try:
            import sympy
            # Whitelist safe functions
            safe_dict = {
                "sqrt": sympy.sqrt, "log": sympy.log, "ln": sympy.ln,
                "sin": sympy.sin, "cos": sympy.cos, "tan": sympy.tan,
                "pi": sympy.pi, "e": sympy.E, "exp": sympy.exp,
                "abs": abs, "pow": pow
            }
            # Sanitize - only allow safe chars
            if not re.match(r'^[0-9+\-*/().,\s\w]+$', expression):
                return f"Error: Invalid characters in expression"
            result = sympy.sympify(expression, locals=safe_dict)
            return f"{result}"
        except ImportError:
            # Fallback to safe eval with whitelisted builtins
            safe_dict = {
                "__builtins__": {},
                "abs": abs, "round": round, "pow": pow,
                "max": max, "min": min, "sum": sum,
                "sqrt": lambda x: x ** 0.5,
                "pi": 3.14159265358979, "e": 2.71828182845905
            }
            if not re.match(r'^[0-9+\-*/().,\s\w]+$', expression):
                return f"Error: Invalid characters"
            result = eval(expression, safe_dict)
            return f"{result}"
    except Exception as e:
        return f"Error: Cannot evaluate '{expression}': {str(e)}"


# ============================================================
# Tool 3: Read File (with safety)
# ============================================================

def read_file(path: str, max_size: int = 100000) -> str:
    """
    Read contents of a local file.

    Args:
        path: Absolute or relative file path
        max_size: Max file size in bytes (default 100KB)

    Returns:
        File contents or error message
    """
    try:
        # Safety: resolve to absolute path
        abs_path = os.path.abspath(path)

        # Safety: only allow reading from current directory or subdirs
        cwd = os.getcwd()
        if not abs_path.startswith(cwd):
            return f"Error: Access denied. Only files in {cwd} are allowed."

        # Check file exists
        if not os.path.exists(abs_path):
            return f"Error: File not found: {path}"

        # Check file size
        size = os.path.getsize(abs_path)
        if size > max_size:
            return f"Error: File too large ({size} bytes). Max allowed: {max_size}"

        # Read file
        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_size)

        return f"File: {path}\nSize: {size} bytes\n---\n{content}"
    except PermissionError:
        return f"Error: Permission denied to read {path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


# ============================================================
# Tool 4: Send Email (SMTP)
# ============================================================

def send_email(to: str, subject: str, body: str, from_email: str = None) -> str:
    """
    Send an email via SMTP.

    Requires SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD env vars.
    For Gmail: use App Password (https://myaccount.google.com/apppasswords)

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body (plain text)
        from_email: Sender email (defaults to SMTP_USER)

    Returns:
        Success or error message
    """
    try:
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        from_email = from_email or smtp_user

        if not all([smtp_user, smtp_password]):
            return "Error: SMTP_USER and SMTP_PASSWORD must be set in .env"

        # Basic email validation
        if "@" not in to or "." not in to.split("@")[-1]:
            return f"Error: Invalid email address: {to}"

        # Build message
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        # Send
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        return f"✅ Email sent successfully to {to}"
    except smtplib.SMTPAuthenticationError:
        return "Error: SMTP authentication failed. Check username/password (use App Password for Gmail)."
    except smtplib.SMTPException as e:
        return f"Error: SMTP failed: {str(e)}"
    except Exception as e:
        return f"Error sending email: {str(e)}"


# ============================================================
# Tool Registry
# ============================================================

TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "web_search": {
        "function": web_search,
        "schema": {
            "name": "web_search",
            "description": "Search the internet for information. Use when you need current data, news, facts, or anything not in your training data. Supports Thai and English queries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results (1-10)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    "calculator": {
        "function": calculator,
        "schema": {
            "name": "calculator",
            "description": "Evaluate a mathematical expression. Supports basic arithmetic (+,-,*,/,**,()), sqrt, log, sin, cos, tan, pi, e. Example: '2*pi*5' or 'sqrt(144)'",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    "read_file": {
        "function": read_file,
        "schema": {
            "name": "read_file",
            "description": "Read the contents of a local text file. Useful for accessing local data, config, or notes. Max 100KB. Only files in current directory are accessible.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to file (relative or absolute)"
                    },
                    "max_size": {
                        "type": "integer",
                        "description": "Max file size in bytes",
                        "default": 100000
                    }
                },
                "required": ["path"]
            }
        }
    },
    "send_email": {
        "function": send_email,
        "schema": {
            "name": "send_email",
            "description": "Send an email via SMTP. Requires SMTP_USER and SMTP_PASSWORD in env. For Gmail, use App Password. Use carefully - emails are sent immediately.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject line"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body (plain text)"
                    },
                    "from_email": {
                        "type": "string",
                        "description": "Sender email (optional, defaults to SMTP_USER)"
                    }
                },
                "required": ["to", "subject", "body"]
            }
        }
    }
}


def list_tools() -> List[str]:
    """Return list of available tool names."""
    return list(TOOL_REGISTRY.keys())


if __name__ == "__main__":
    # Quick test
    print("Available tools:", list_tools())
    print("\nTest calculator:", calculator("2 + 2 * 3"))
    print("Test calculator (sqrt):", calculator("sqrt(144)"))
