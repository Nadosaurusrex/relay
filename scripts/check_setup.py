#!/usr/bin/env python3
"""
Visual status checker for Relay infrastructure.

Checks health of all services and displays results in a nice table.
"""

import sys
import subprocess
import requests
from typing import Tuple, Optional

# Try to use rich for pretty output, fall back to basic output
try:
    from rich.console import Console
    from rich.table import Table
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def check_docker_running() -> Tuple[bool, str]:
    """Check if Docker daemon is running."""
    try:
        subprocess.run(
            ["docker", "info"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            timeout=5
        )
        return True, "Running"
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False, "Not running"


def check_container_running(container_name: str) -> Tuple[bool, str]:
    """Check if a specific Docker container is running."""
    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Status}}", container_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            status = result.stdout.strip()
            return status == "running", status.capitalize()
        return False, "Not found"
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False, "Error"


def check_http_service(url: str, timeout: int = 3) -> Tuple[bool, str]:
    """Check if an HTTP service is responding."""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return True, f"HTTP {response.status_code}"
        return False, f"HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused"
    except Exception as e:
        return False, f"Error: {str(e)[:20]}"


def check_postgres_container() -> Tuple[bool, str]:
    """Check PostgreSQL via Docker."""
    try:
        result = subprocess.run(
            ["docker", "exec", "relay-postgres", "pg_isready", "-U", "relay", "-d", "relay"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        if result.returncode == 0:
            return True, "Ready"
        return False, "Not ready"
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False, "Not available"


def check_env_file() -> Tuple[bool, str]:
    """Check if .env file exists with RELAY_PRIVATE_KEY."""
    try:
        with open('.env', 'r') as f:
            content = f.read()
            if 'RELAY_PRIVATE_KEY' in content:
                return True, "Configured"
            return False, "Missing key"
    except FileNotFoundError:
        return False, "Not found"


def print_rich_status():
    """Print status using rich library."""
    console = Console()

    # Header
    console.print("\n[bold cyan]═══════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]         Relay Agent Governance - System Status            [/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════[/bold cyan]\n")

    # Create table
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan", width=25)
    table.add_column("Status", width=15)
    table.add_column("Details", style="dim", width=30)

    # Check all components
    checks = [
        ("Docker Daemon", check_docker_running(), "docker.com"),
        ("Environment Config", check_env_file(), ".env file"),
        ("Container: PostgreSQL", check_container_running("relay-postgres"), "Port 5432"),
        ("Container: OPA", check_container_running("relay-opa"), "Port 8181"),
        ("Container: Gateway", check_container_running("relay-gateway"), "Port 8000"),
        ("PostgreSQL Health", check_postgres_container(), "Database ready"),
        ("OPA API", check_http_service("http://localhost:8181/health"), "http://localhost:8181"),
        ("Relay Gateway", check_http_service("http://localhost:8000/health"), "http://localhost:8000"),
    ]

    all_passing = True
    for name, (is_healthy, status), detail in checks:
        if is_healthy:
            status_text = f"[bold green]✓[/bold green] {status}"
        else:
            status_text = f"[bold red]✗[/bold red] {status}"
            all_passing = False

        table.add_row(name, status_text, detail)

    console.print(table)

    # Summary
    if all_passing:
        console.print("\n[bold green]✓ All systems operational[/bold green]")
        console.print("\n[cyan]Ready to protect your agents![/cyan]")
        console.print("\n[dim]Next steps:[/dim]")
        console.print("  • [yellow]python examples/simple_demo.py[/yellow]")
        console.print("  • [yellow]cd examples && jupyter notebook[/yellow]")
        console.print("  • [yellow]curl http://localhost:8000/v1/audit/query[/yellow]\n")
    else:
        console.print("\n[bold yellow]⚠ Some components are not running[/bold yellow]")
        console.print("\n[dim]To start services:[/dim]")
        console.print("  [yellow]cd infra && docker-compose up -d[/yellow]")
        console.print("\n[dim]To check logs:[/dim]")
        console.print("  [yellow]docker-compose -f infra/docker-compose.yml logs -f[/yellow]\n")


def print_basic_status():
    """Print status using basic ASCII output."""
    print("\n" + "=" * 63)
    print("         Relay Agent Governance - System Status            ")
    print("=" * 63 + "\n")

    checks = [
        ("Docker Daemon", check_docker_running(), "docker.com"),
        ("Environment Config", check_env_file(), ".env file"),
        ("Container: PostgreSQL", check_container_running("relay-postgres"), "Port 5432"),
        ("Container: OPA", check_container_running("relay-opa"), "Port 8181"),
        ("Container: Gateway", check_container_running("relay-gateway"), "Port 8000"),
        ("PostgreSQL Health", check_postgres_container(), "Database ready"),
        ("OPA API", check_http_service("http://localhost:8181/health"), "http://localhost:8181"),
        ("Relay Gateway", check_http_service("http://localhost:8000/health"), "http://localhost:8000"),
    ]

    all_passing = True
    max_name_length = max(len(name) for name, _, _ in checks)

    for name, (is_healthy, status), detail in checks:
        symbol = "✓" if is_healthy else "✗"
        status_text = f"[{symbol}] {status:15s}"
        print(f"  {name:{max_name_length}s}  {status_text}  {detail}")
        if not is_healthy:
            all_passing = False

    print()
    if all_passing:
        print("✓ All systems operational")
        print("\nReady to protect your agents!")
        print("\nNext steps:")
        print("  • python examples/simple_demo.py")
        print("  • cd examples && jupyter notebook")
        print("  • curl http://localhost:8000/v1/audit/query")
    else:
        print("⚠ Some components are not running")
        print("\nTo start services:")
        print("  cd infra && docker-compose up -d")
        print("\nTo check logs:")
        print("  docker-compose -f infra/docker-compose.yml logs -f")

    print()


def main():
    """Main entry point."""
    if HAS_RICH:
        print_rich_status()
    else:
        print_basic_status()
        print("\nTip: Install 'rich' for better formatting: pip install rich\n")


if __name__ == "__main__":
    main()
