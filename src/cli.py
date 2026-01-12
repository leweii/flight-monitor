# src/cli.py
import click
import asyncio
import logging
from pathlib import Path
from src.config import load_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@click.group()
def cli():
    """Flight price monitoring CLI."""
    pass

@cli.command()
@click.option('--config', '-c', default='config.yaml', help='Config file path')
def start(config):
    """Start the monitoring service."""
    from src.main import main
    click.echo(f"Starting flight monitor with config: {config}")
    asyncio.run(main(config))

@cli.command('list-routes')
@click.option('--config', '-c', default='config.yaml', help='Config file path')
def list_routes(config):
    """List all configured routes."""
    cfg = load_config(config)
    routes = cfg.get('routes', [])

    if not routes:
        click.echo("No routes configured.")
        return

    click.echo(f"\nConfigured routes ({len(routes)}):\n")
    for r in routes:
        click.echo(f"  {r['name']}")
        click.echo(f"    Route: {r['origin']} -> {r['destination']}")
        click.echo(f"    Interval: {r['check_interval']}")
        if 'date_range' in r:
            click.echo(f"    Dates: {r['date_range'].get('start')} to {r['date_range'].get('end')}")
        click.echo()

@cli.command()
@click.argument('origin')
@click.argument('destination')
@click.option('--config', '-c', default='config.yaml', help='Config file path')
def check(origin, destination, config):
    """Manually check a specific route."""
    from src.main import check_route_once
    click.echo(f"Checking {origin} -> {destination}...")
    asyncio.run(check_route_once(origin, destination, config))

if __name__ == '__main__':
    cli()
