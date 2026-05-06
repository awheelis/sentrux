"""MCP server implementation for Sentrux."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from sentrux.core.analyzer import ProjectAnalyzer
from sentrux.core.rules import RulesEngine
from sentrux.mcp.tools import MCPTools
from sentrux.utils.config import ConfigLoader


class MCPServer:
    """MCP (Model Context Protocol) server for Sentrux."""

    def __init__(self):
        self.tools = MCPTools()
        self.current_workspace: Optional[Path] = None
        self.last_analysis = None

    def handle_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP request."""
        method = message.get("method", "")
        params = message.get("params", {})

        try:
            if method == "tools/list":
                return self._list_tools()
            elif method == "tools/call":
                return self._call_tool(params)
            elif method == "initialize":
                return self._initialize(params)
            else:
                return self._error(f"Unknown method: {method}")
        except Exception as e:
            return self._error(str(e))

    def _list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return {
            "tools": [
                {
                    "name": "scan",
                    "description": "Analyze workspace and get quality metrics",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to analyze",
                            }
                        },
                    },
                },
                {
                    "name": "health",
                    "description": "Get current project quality metrics",
                    "inputSchema": {"type": "object", "properties": {}},
                },
                {
                    "name": "check_rules",
                    "description": "Check architectural rules compliance",
                    "inputSchema": {"type": "object", "properties": {}},
                },
                {
                    "name": "session_start",
                    "description": "Initialize analysis session",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "workspace_path": {
                                "type": "string",
                                "description": "Workspace root path",
                            }
                        },
                    },
                },
                {
                    "name": "session_end",
                    "description": "End current session",
                    "inputSchema": {"type": "object", "properties": {}},
                },
            ]
        }

    def _call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool."""
        name = params.get("name", "")
        args = params.get("arguments", {})

        if name == "scan":
            return self.tools.scan(args.get("path"))
        elif name == "health":
            return self.tools.health(self.last_analysis)
        elif name == "check_rules":
            return self.tools.check_rules(self.current_workspace, self.last_analysis)
        elif name == "session_start":
            workspace = args.get("workspace_path")
            self.current_workspace = Path(workspace) if workspace else Path.cwd()
            return {"status": "ok", "workspace": str(self.current_workspace)}
        elif name == "session_end":
            self.current_workspace = None
            self.last_analysis = None
            return {"status": "ok"}
        else:
            return self._error(f"Unknown tool: {name}")

    def _initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization."""
        workspace = params.get("workspace", ".")
        self.current_workspace = Path(workspace)
        return {
            "serverInfo": {
                "name": "sentrux",
                "version": "0.1.0",
            },
            "capabilities": {
                "tools": {},
            },
        }

    def _error(self, message: str) -> Dict[str, Any]:
        """Return error response."""
        return {
            "error": {
                "code": -32603,
                "message": message,
            }
        }

    def run(self) -> None:
        """Run the MCP server (read from stdin, write to stdout)."""
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                response = self.handle_request(request)
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
            except json.JSONDecodeError:
                error_response = self._error("Invalid JSON")
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()
            except Exception as e:
                error_response = self._error(str(e))
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()


def run_mcp_server() -> None:
    """Entry point for MCP server."""
    server = MCPServer()
    server.run()
