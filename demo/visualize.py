#!/usr/bin/env python3
"""
Relay Audit Trail Visualizer

Displays the audit trail in a formatted table.
"""

import sys
import requests
from pathlib import Path
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
except ImportError:
    print("⚠️  Rich library not installed. Install it with: pip install rich")
    sys.exit(1)


def fetch_audit_trail(gateway_url: str = "http://localhost:8000"):
    """
    Fetch audit trail from Gateway API.

    Args:
        gateway_url: Base URL of Relay Gateway

    Returns:
        List of audit records
    """
    try:
        response = requests.get(
            f"{gateway_url}/v1/audit/query",
            params={"limit": 50},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])

    except Exception as e:
        print(f"❌ Failed to fetch audit trail: {e}")
        print("   Make sure Relay Gateway is running at", gateway_url)
        sys.exit(1)


def fetch_stats(gateway_url: str = "http://localhost:8000"):
    """
    Fetch audit statistics.

    Args:
        gateway_url: Base URL of Relay Gateway

    Returns:
        Statistics dictionary
    """
    try:
        response = requests.get(
            f"{gateway_url}/v1/audit/stats",
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    except Exception:
        return None


def format_timestamp(iso_timestamp: str) -> str:
    """Format ISO timestamp to readable format."""
    dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_amount(parameters: dict) -> str:
    """Extract and format amount from parameters."""
    if "amount" in parameters:
        amount = parameters["amount"]
        return f"${amount / 100:.2f}"
    return "N/A"


def visualize_audit_trail():
    """Display the audit trail in a formatted table."""
    console = Console()

    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]🔍 Relay Audit Trail[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

    # Fetch data
    records = fetch_audit_trail()
    stats = fetch_stats()

    if not records:
        console.print("[yellow]⚠️  No audit records found[/yellow]")
        console.print("   Run the demo first: python demo/agent.py\n")
        return

    # Create table
    table = Table(
        title=f"[bold]Audit Records[/bold] (showing {len(records)} most recent)",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )

    table.add_column("Timestamp", style="dim", width=19)
    table.add_column("Agent", style="cyan", width=18)
    table.add_column("Action", style="white", width=25)
    table.add_column("Amount", justify="right", width=10)
    table.add_column("Status", justify="center", width=10)
    table.add_column("Policy", style="dim", width=10)

    # Add rows
    for record in records:
        timestamp = format_timestamp(record["created_at"])
        agent_id = record["agent_id"]
        action = f"{record['provider']}.{record['method']}"
        amount = format_amount(record["parameters"])

        # Status with emoji
        if record["approved"]:
            status = "[green]✅ PASS[/green]"
        else:
            status = "[red]❌ DENY[/red]"

        policy_version = record.get("policy_version", "N/A")

        table.add_row(
            timestamp,
            agent_id,
            action,
            amount,
            status,
            policy_version,
        )

    console.print(table)
    console.print()

    # Display statistics
    if stats:
        stats_table = Table(
            title="[bold]Statistics[/bold]",
            box=box.SIMPLE,
            show_header=False,
        )
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", justify="right", style="bold")

        stats_table.add_row("Total Manifests", str(stats["total_manifests"]))
        stats_table.add_row("Approved", f"[green]{stats['approved']}[/green]")
        stats_table.add_row("Denied", f"[red]{stats['denied']}[/red]")
        stats_table.add_row("Executed", str(stats["executed"]))
        stats_table.add_row("Approval Rate", f"{stats['approval_rate']:.1f}%")

        console.print(stats_table)
        console.print()

    # Display denied actions
    denied_records = [r for r in records if not r["approved"]]
    if denied_records:
        console.print("[bold red]❌ Denied Actions:[/bold red]")
        for record in denied_records[:5]:  # Show first 5
            console.print(f"   • {record['method']}: {record['denial_reason']}")
        console.print()

    # Footer
    console.print("[dim]💡 Query the API directly:[/dim]")
    console.print("[dim]   curl http://localhost:8000/v1/audit/query[/dim]")
    console.print()


if __name__ == "__main__":
    try:
        visualize_audit_trail()
    except KeyboardInterrupt:
        print("\n👋 Visualization interrupted")
        sys.exit(0)
