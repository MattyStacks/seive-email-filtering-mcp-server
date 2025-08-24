#!/usr/bin/env python3
"""
Command-line interface for the Sieve Email Filtering MCP Server.
"""

import click
import json
from pathlib import Path
from typing import List, Optional

from seive_email_filtering_mcp_server.models import SieveScript
from seive_email_filtering_mcp_server.generator import SieveGenerator, SieveValidator
from seive_email_filtering_mcp_server.utils import SieveFilterBuilder, SieveTemplates


@click.group()
@click.version_option()
def cli():
    """Sieve Email Filtering CLI - Generate and manage Sieve email filters."""
    pass


@cli.command()
@click.option('--mailbox', default='Spam', help='Mailbox to move spam to')
@click.option('--priority', default=10, help='Rule priority')
@click.option('--output', type=click.Path(), help='Output file (default: stdout)')
def spam_filter(mailbox: str, priority: int, output: Optional[str]):
    """Create a spam filter rule."""
    rule = SieveFilterBuilder.create_spam_filter(mailbox, priority)
    script = SieveScript(
        name="Spam Filter",
        rules=[rule],
        requires=["fileinto"]
    )
    
    generator = SieveGenerator()
    script_text = generator.generate_script(script)
    
    if output:
        Path(output).write_text(script_text)
        click.echo(f"Spam filter saved to {output}")
    else:
        click.echo(script_text)


@cli.command()
@click.option('--sender', required=True, help='Sender email address')
@click.option('--mailbox', required=True, help='Mailbox to move messages to')
@click.option('--priority', default=30, help='Rule priority')
@click.option('--output', type=click.Path(), help='Output file (default: stdout)')
def sender_filter(sender: str, mailbox: str, priority: int, output: Optional[str]):
    """Create a sender filter rule."""
    rule = SieveFilterBuilder.create_sender_filter(sender, mailbox, priority)
    script = SieveScript(
        name=f"Sender Filter: {sender}",
        rules=[rule],
        requires=["fileinto"]
    )
    
    generator = SieveGenerator()
    script_text = generator.generate_script(script)
    
    if output:
        Path(output).write_text(script_text)
        click.echo(f"Sender filter saved to {output}")
    else:
        click.echo(script_text)


@cli.command()
@click.option('--list-id', required=True, help='Mailing list identifier')
@click.option('--mailbox', required=True, help='Mailbox to move messages to')
@click.option('--priority', default=20, help='Rule priority')
@click.option('--output', type=click.Path(), help='Output file (default: stdout)')
def mailing_list_filter(list_id: str, mailbox: str, priority: int, output: Optional[str]):
    """Create a mailing list filter rule."""
    rule = SieveFilterBuilder.create_mailing_list_filter(list_id, mailbox, priority)
    script = SieveScript(
        name=f"Mailing List Filter: {list_id}",
        rules=[rule],
        requires=["fileinto"]
    )
    
    generator = SieveGenerator()
    script_text = generator.generate_script(script)
    
    if output:
        Path(output).write_text(script_text)
        click.echo(f"Mailing list filter saved to {output}")
    else:
        click.echo(script_text)


@cli.command()
@click.option('--message', required=True, help='Vacation message')
@click.option('--subject', help='Vacation subject line')
@click.option('--days', default=7, help='Days between responses')
@click.option('--output', type=click.Path(), help='Output file (default: stdout)')
def vacation(message: str, subject: Optional[str], days: int, output: Optional[str]):
    """Create a vacation auto-reply."""
    rule = SieveFilterBuilder.create_vacation_response(message, subject, days)
    script = SieveScript(
        name="Vacation Response",
        rules=[rule],
        requires=["vacation"]
    )
    
    generator = SieveGenerator()
    script_text = generator.generate_script(script)
    
    if output:
        Path(output).write_text(script_text)
        click.echo(f"Vacation response saved to {output}")
    else:
        click.echo(script_text)


@cli.command()
@click.argument('template_name', type=click.Choice(['basic_email_organization', 'comprehensive_filtering', 'vacation_with_filtering']))
@click.option('--output', type=click.Path(), help='Output file (default: stdout)')
def template(template_name: str, output: Optional[str]):
    """Generate a script from a pre-built template."""
    if template_name == 'basic_email_organization':
        script = SieveTemplates.basic_email_organization()
    elif template_name == 'comprehensive_filtering':
        script = SieveTemplates.comprehensive_filtering()
    elif template_name == 'vacation_with_filtering':
        script = SieveTemplates.vacation_with_filtering()
    else:
        click.echo(f"Unknown template: {template_name}")
        return
    
    generator = SieveGenerator()
    script_text = generator.generate_script(script)
    
    if output:
        Path(output).write_text(script_text)
        click.echo(f"Template '{template_name}' saved to {output}")
    else:
        click.echo(script_text)


@cli.command()
@click.argument('script_file', type=click.Path(exists=True))
def validate(script_file: str):
    """Validate a Sieve script JSON file."""
    try:
        script_data = json.loads(Path(script_file).read_text())
        script = SieveScript.model_validate(script_data)
        
        errors = SieveValidator.validate_script(script)
        
        if errors:
            click.echo("Validation failed:")
            for error in errors:
                click.echo(f"  - {error}")
            exit(1)
        else:
            click.echo("Script validation passed!")
            
    except Exception as e:
        click.echo(f"Error validating script: {e}")
        exit(1)


@cli.command()
@click.argument('script_file', type=click.Path(exists=True))
@click.option('--output', type=click.Path(), help='Output file (default: stdout)')
def generate(script_file: str, output: Optional[str]):
    """Generate Sieve script from JSON file."""
    try:
        script_data = json.loads(Path(script_file).read_text())
        script = SieveScript.model_validate(script_data)
        
        # Validate first
        errors = SieveValidator.validate_script(script)
        if errors:
            click.echo("Script validation failed:")
            for error in errors:
                click.echo(f"  - {error}")
            exit(1)
        
        generator = SieveGenerator()
        script_text = generator.generate_script(script)
        
        if output:
            Path(output).write_text(script_text)
            click.echo(f"Sieve script saved to {output}")
        else:
            click.echo(script_text)
            
    except Exception as e:
        click.echo(f"Error generating script: {e}")
        exit(1)


@cli.command()
def list_templates():
    """List available script templates."""
    templates = [
        ("basic_email_organization", "Basic spam filtering and size management"),
        ("comprehensive_filtering", "Complete filtering with whitelist, blacklist, and organization"),
        ("vacation_with_filtering", "Vacation auto-reply with smart filtering")
    ]
    
    click.echo("Available templates:")
    for name, description in templates:
        click.echo(f"  {name:<30} {description}")


@cli.command()
def server():
    """Run the MCP server."""
    from seive_email_filtering_mcp_server.server import main
    main()


if __name__ == '__main__':
    cli()
