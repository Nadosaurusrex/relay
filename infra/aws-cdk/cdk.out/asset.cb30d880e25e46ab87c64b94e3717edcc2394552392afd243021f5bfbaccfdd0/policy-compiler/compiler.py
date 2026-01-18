"""
Policy compiler: YAML → Rego

Transpiles human-readable YAML policies to OPA Rego format.
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any


class PolicyCompiler:
    """
    Compiles YAML policy files to Rego format.
    """

    def __init__(self, template_dir: str = None):
        """
        Initialize the policy compiler.

        Args:
            template_dir: Directory containing Jinja2 templates
        """
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"

        self.template_dir = Path(template_dir)
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def compile(self, yaml_file: Path, output_file: Path = None) -> str:
        """
        Compile a YAML policy file to Rego.

        Args:
            yaml_file: Path to YAML policy file
            output_file: Optional output file path (if None, returns string)

        Returns:
            Compiled Rego policy as string
        """
        # Load YAML
        with open(yaml_file, 'r') as f:
            policy_data = yaml.safe_load(f)

        # Validate YAML structure
        self._validate_policy(policy_data)

        # Prepare template context
        context = {
            "version": policy_data.get("version", "1.0"),
            "timestamp": datetime.utcnow().isoformat(),
            "source_file": yaml_file.name,
            "package_name": policy_data.get("package", "relay.policies.main"),
            "policies": policy_data["policies"],
        }

        # Render Rego template
        template = self.jinja_env.get_template("base.rego.j2")
        rego_code = template.render(**context)

        # Write to file if specified
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(rego_code)
            print(f"✅ Compiled {yaml_file.name} → {output_file}")

        return rego_code

    def _validate_policy(self, policy_data: Dict[str, Any]):
        """
        Validate YAML policy structure.

        Args:
            policy_data: Parsed YAML data

        Raises:
            ValueError: If policy structure is invalid
        """
        if "policies" not in policy_data:
            raise ValueError("Missing 'policies' key in YAML")

        if not isinstance(policy_data["policies"], list):
            raise ValueError("'policies' must be a list")

        for policy in policy_data["policies"]:
            if "name" not in policy:
                raise ValueError("Each policy must have a 'name'")

            if "rules" not in policy:
                raise ValueError(f"Policy '{policy['name']}' missing 'rules'")

            for rule in policy["rules"]:
                if "id" not in rule:
                    raise ValueError(f"Rule in policy '{policy['name']}' missing 'id'")

                if "condition" not in rule:
                    raise ValueError(f"Rule '{rule['id']}' missing 'condition'")

                if "action" not in rule:
                    raise ValueError(f"Rule '{rule['id']}' missing 'action'")

                if rule["action"] not in ["allow", "deny"]:
                    raise ValueError(f"Rule '{rule['id']}' has invalid action: {rule['action']}")

    def compile_all(self, policy_dir: Path, output_dir: Path):
        """
        Compile all YAML policy files in a directory.

        Args:
            policy_dir: Directory containing YAML policy files
            output_dir: Directory for compiled Rego files
        """
        yaml_files = list(policy_dir.glob("*.yaml")) + list(policy_dir.glob("*.yml"))

        if not yaml_files:
            print(f"⚠️  No YAML files found in {policy_dir}")
            return

        for yaml_file in yaml_files:
            output_file = output_dir / f"{yaml_file.stem}.rego"
            try:
                self.compile(yaml_file, output_file)
            except Exception as e:
                print(f"❌ Failed to compile {yaml_file.name}: {e}")


def main():
    """CLI entry point for policy compiler."""
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <yaml_file> [output_file]")
        print("   or: python compiler.py --all <policy_dir> <output_dir>")
        sys.exit(1)

    compiler = PolicyCompiler()

    if sys.argv[1] == "--all":
        # Compile all policies in directory
        if len(sys.argv) < 4:
            print("Usage: python compiler.py --all <policy_dir> <output_dir>")
            sys.exit(1)

        policy_dir = Path(sys.argv[2])
        output_dir = Path(sys.argv[3])

        compiler.compile_all(policy_dir, output_dir)

    else:
        # Compile single policy
        yaml_file = Path(sys.argv[1])
        output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None

        rego_code = compiler.compile(yaml_file, output_file)

        if not output_file:
            print(rego_code)


if __name__ == "__main__":
    main()
