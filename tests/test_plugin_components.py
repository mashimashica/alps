"""Keep the harness's Plugin components aligned across Hosts: its MCP server, command, and install."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOST_ADAPTERS = {".claude-plugin", ".codex-plugin"}
CLI = "harness/src/cli.ts"
# Each registration of the harness's MCP server and the variable its Host puts the Plugin root in.
REGISTRATIONS = {".mcp.json": "${CLAUDE_PLUGIN_ROOT}", "mcp.json": "${PLUGIN_ROOT}"}
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def tool_names() -> set[str]:
    """The MCP tools that harness/src/mcp.ts describes."""
    source = (ROOT / "harness/src/mcp.ts").read_text(encoding="utf-8")
    block = source.split("const DESCRIPTIONS = {", 1)[1].split("} as const;", 1)[0]
    return set(re.findall(r"^  (\w+): `", block, re.MULTILINE))


class PluginComponentTests(unittest.TestCase):
    def test_host_adapters(self) -> None:
        adapters = {
            entry.name
            for entry in ROOT.iterdir()
            if entry.is_dir() and entry.name.startswith(".") and entry.name.endswith("-plugin")
        }
        self.assertEqual(adapters, HOST_ADAPTERS)

    def test_mcp_server_registrations(self) -> None:
        self.assertTrue((ROOT / CLI).is_file())
        for path, root in REGISTRATIONS.items():
            with self.subTest(registration=path):
                servers = load(path)["mcpServers"]
                self.assertEqual(set(servers), {"harness"})
                server = servers["harness"]
                self.assertEqual(server["type"], "stdio")
                self.assertEqual(server["command"], "bun")
                self.assertEqual(server["args"], [f"{root}/{CLI}", "mcp"])
                # No cwd: the harness finds the workspace from ALPS_WORKSPACE or its working directory.
                self.assertNotIn("cwd", server)
        with self.subTest(registration=".mcp.json", key="env"):
            self.assertEqual(
                load(".mcp.json")["mcpServers"]["harness"].get("env"),
                {"ALPS_WORKSPACE": "${CLAUDE_PROJECT_DIR}"},
            )
        with self.subTest(registration="mcp.json", key="$schema"):
            plugin_schema = load("plugin.json")["$schema"]
            self.assertEqual(
                load("mcp.json")["$schema"],
                plugin_schema.replace("plugin.schema.json", "mcp.schema.json"),
            )
        with self.subTest(manifest=".codex-plugin/plugin.json", key="mcpServers"):
            self.assertEqual(load(".codex-plugin/plugin.json")["mcpServers"], "./mcp.json")

    def test_commands_use_the_harness_tools(self) -> None:
        commands = sorted((ROOT / "commands").glob("*.md"))
        self.assertEqual([command.name for command in commands], ["harness.md"])
        prefix = f"mcp__plugin_{load('plugin.json')['name']}_"
        servers = set(load(".mcp.json")["mcpServers"])
        tools = tool_names()
        self.assertIn("open_ui", tools)
        for command in commands:
            match = FRONTMATTER.match(command.read_text(encoding="utf-8"))
            self.assertIsNotNone(match, f"{command.name} has no frontmatter")
            fields = dict(
                line.split(":", 1) for line in match.group(1).splitlines() if ":" in line
            )
            for tool in fields.get("allowed-tools", "").replace(",", " ").split():
                with self.subTest(command=command.name, tool=tool):
                    self.assertTrue(tool.startswith(prefix), "not a tool of this Plugin")
                    server, _, name = tool[len(prefix) :].partition("__")
                    self.assertIn(server, servers)
                    self.assertIn(name, tools)

    def test_fetch_time_install_has_only_runtime_dependencies(self) -> None:
        # Claude Code runs `bun install --frozen-lockfile --ignore-scripts` at the Plugin root.
        root = load("package.json")
        self.assertTrue(root.get("dependencies"))
        self.assertNotIn("devDependencies", root)
        self.assertNotIn("workspaces", root)
        self.assertTrue((ROOT / "bun.lock").is_file())
        # Claude Code skips that install when a bunfig.toml is beside the Bun lockfile.
        self.assertFalse((ROOT / "bunfig.toml").exists())
        # What the harness needs at run time is installed only from the root.
        harness = load("harness/package.json")
        self.assertFalse(harness.get("dependencies"))
        self.assertTrue(harness.get("devDependencies"))


if __name__ == "__main__":
    unittest.main()
