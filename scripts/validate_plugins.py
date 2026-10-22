"""Check the shared Claude Code / Codex package layout without third-party packages.

This checks repository invariants, not full upstream JSON/YAML schemas. Use the
native host validators as well; see CONTRIBUTING.md.
"""

import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MANUAL_POLICY = "policy:\n  allow_implicit_invocation: false\n"


class ValidationError(ValueError):
    """A package would be missing, inconsistent, or incomplete on one host."""


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    except (OSError, ValueError) as error:
        raise ValidationError(f"{path}: {error}") from error
    require(isinstance(value, dict), f"{path}: expected a JSON object")
    return value


def entries_by_name(catalog):
    entries = catalog.get("plugins")
    require(isinstance(entries, list) and entries, "marketplace needs plugins")
    result = {}
    for entry in entries:
        require(isinstance(entry, dict), "marketplace entries must be objects")
        name = entry.get("name")
        require(isinstance(name, str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name),
                f"invalid plugin name: {name}")
        require(name not in result, f"duplicate plugin entry: {name}")
        result[name] = entry
    return result


def local_path(root, value):
    require(isinstance(value, str) and value.startswith("./"),
            f"source must be a ./-prefixed local path: {value}")
    path = (root / value).resolve()
    require(path.is_relative_to(root), f"source escapes marketplace root: {value}")
    require(path.is_dir(), f"missing plugin directory: {value}")
    return path


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    require(match is not None, f"missing frontmatter: {path}")
    return match.group(1)


def validate_links(plugin):
    for path in plugin.rglob("*.md"):
        # Only check inline file links, not URLs, anchors, or illustrative code.
        text = re.sub(r"^```[^\n]*\n.*?^```[^\n]*$", "", path.read_text(encoding="utf-8"),
                      flags=re.MULTILINE | re.DOTALL)
        for target in re.findall(r"\[[^\]\n]*\]\(([^)\s]+)\)", text):
            url = urlsplit(target)
            if url.scheme or url.netloc or not url.path:
                continue
            resolved = (path.parent / unquote(url.path)).resolve()
            require(resolved.is_relative_to(plugin), f"link leaves plugin package: {path}: {target}")
            require(resolved.is_file(), f"broken local link: {path}: {target}")


def validate_repository(root):
    root = Path(root).resolve()
    claude = read_json(root / ".claude-plugin/marketplace.json")
    codex = read_json(root / ".agents/plugins/marketplace.json")
    require(claude.get("name") == codex.get("name") and bool(claude.get("name")),
            "marketplace names differ or are missing")
    require(bool(codex.get("interface", {}).get("displayName")), "missing marketplace displayName")
    claude_entries, codex_entries = entries_by_name(claude), entries_by_name(codex)
    directories = {path.name for path in (root / "plugins").iterdir() if path.is_dir()}
    require(set(claude_entries) == set(codex_entries) == directories,
            "plugin inventory differs between catalogs and plugins/")
    skill_count = 0
    for name, entry in claude_entries.items():
        plugin = local_path(root, entry.get("source"))
        codex_entry = codex_entries[name]
        source = codex_entry.get("source")
        require(isinstance(source, dict) and source.get("source") == "local",
                f"{name}: expected a local Codex source")
        require(local_path(root, source.get("path")) == plugin == root / "plugins" / name,
                f"{name}: source paths differ")
        require(codex_entry.get("policy") == {
            "installation": "AVAILABLE", "authentication": "ON_INSTALL"
        }, f"{name}: missing or unexpected marketplace policy")
        require(codex_entry.get("category") == "Productivity", f"{name}: missing category")
        legacy = read_json(plugin / ".claude-plugin/plugin.json")
        portable = read_json(plugin / "plugin.json")
        require(portable.get("$schema") == PLUGIN_SCHEMA, f"{name}: missing Agent Plugins schema")
        require(portable.get("name") == name, f"{name}: manifest name differs")
        for key in ("name", "version", "description", "author"):
            require(key in portable and portable[key] == legacy.get(key),
                    f"{name}: manifests disagree on {key}")
        require(re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", portable["version"]),
                f"{name}: expected a stable semantic version")
        require(not {"skills", "agents", "dependencies", "mcpServers", "interface"} & portable.keys(),
                f"{name}: Claude/compatibility fields in portable manifest")
        listing = portable.get("extensions", {}).get("com.openai", {}).get("interface", {})
        require(0 < len(listing.get("shortDescription", "")) <= 30, f"{name}: invalid shortDescription")
        require(listing.get("category") == codex_entry["category"], f"{name}: categories differ")
        skills = sorted((plugin / "skills").glob("*/SKILL.md"))
        require(bool(skills), f"{name}: no skills found")
        skill_names = set()
        for skill in skills:
            header = frontmatter(skill)
            skill_name = re.search(r"^name: ([a-z0-9-]+)$", header, re.MULTILINE)
            require(skill_name is not None and skill_name.group(1) == skill.parent.name,
                    f"{skill}: skill name must match its directory")
            require(skill_name.group(1) not in skill_names, f"{name}: duplicate skill name")
            skill_names.add(skill_name.group(1))
            require(re.search(r"^description: >-\n  \S", header, re.MULTILINE),
                    f"{skill}: description must be a nonempty folded scalar")
            policy = skill.parent / "agents/openai.yaml"
            manual = bool(re.search(r"^disable-model-invocation: true$", header, re.MULTILINE))
            if manual:
                require(policy.is_file() and policy.read_text(encoding="utf-8") == MANUAL_POLICY,
                        f"{skill}: manual invocation policy missing or changed")
            else:
                require(not policy.exists(), f"{skill}: unexpected manual invocation policy")
            require("Codex" in skill.read_text(encoding="utf-8"), f"{skill}: missing runtime guidance")
        for agent in (plugin / "agents").glob("*.md"):
            frontmatter(agent)
        require(not any(path.is_symlink() for path in plugin.rglob("*")),
                f"{name}: package must not depend on symlinks")
        validate_links(plugin)
        skill_count += len(skills)
    require((root / "CLAUDE.md").read_text(encoding="utf-8").strip() == "@AGENTS.md",
            "CLAUDE.md must import shared AGENTS.md")
    require((root / "AGENTS.md").is_file(), "shared AGENTS.md is missing")
    return len(directories), skill_count


if __name__ == "__main__":
    try:
        plugins, skills = validate_repository(Path(__file__).resolve().parents[1])
    except (ValidationError, OSError, TypeError, KeyError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: {plugins} plugins, {skills} shared skills; catalogs, manifests, policies, and links agree")
