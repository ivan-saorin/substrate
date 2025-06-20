#!/usr/bin/env python3
"""
Model Configuration Management Tool
Manages model configurations across substrate-based projects
"""
import os
import sys
import click
from pathlib import Path
from tabulate import tabulate
from dotenv import load_dotenv, set_key, dotenv_values
from typing import List, Optional, Dict


# Model size definitions
MODEL_SIZES = ["XS", "S", "M", "L", "XL", "XXL"]
PROVIDERS = ["ANTHROPIC", "OPENAI", "GOOGLE", "GROQ"]

# Default model mappings
DEFAULT_MODELS = {
    "ANTHROPIC": {
        "XS": "claude-3-5-haiku-20241022",
        "S": "claude-3-5-haiku-20241022",
        "M": "claude-3-5-sonnet-20241022",
        "L": "claude-3-5-sonnet-20241022",
        "XL": "claude-3-opus-20240229",
        "XXL": "claude-3-opus-20240229"
    },
    "OPENAI": {
        "XS": "gpt-4o-mini",
        "S": "gpt-4o-mini",
        "M": "gpt-4o",
        "L": "gpt-4o",
        "XL": "o1-preview",
        "XXL": "o1"
    },
    "GOOGLE": {
        "XS": "gemini-1.5-flash",
        "S": "gemini-1.5-flash",
        "M": "gemini-1.5-pro",
        "L": "gemini-1.5-pro",
        "XL": "gemini-1.5-pro",
        "XXL": "gemini-1.5-pro"
    },
    "GROQ": {
        "XS": "llama-3.2-3b-preview",
        "S": "llama-3.2-7b-preview",
        "M": "llama-3.2-70b-preview",
        "L": "llama-3.2-70b-preview",
        "XL": "llama-3.2-70b-preview",
        "XXL": "llama-3.2-70b-preview"
    }
}


def find_env_file(path: Optional[str] = None) -> Path:
    """Find .env file in current or specified directory"""
    if path:
        env_path = Path(path)
        if env_path.is_file():
            return env_path
        elif env_path.is_dir():
            return env_path / ".env"
    
    # Look in current directory
    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        return cwd_env
    
    # Look in parent directories
    current = Path.cwd()
    for parent in current.parents:
        env_file = parent / ".env"
        if env_file.exists():
            return env_file
    
    raise click.ClickException("No .env file found. Use --env-file to specify location.")


@click.group()
@click.option('--env-file', help='Path to .env file', type=click.Path())
@click.pass_context
def cli(ctx, env_file):
    """Model Configuration Management Tool"""
    ctx.ensure_object(dict)
    ctx.obj['env_file'] = find_env_file(env_file)
    

@cli.command()
@click.pass_context
def list(ctx):
    """List all configured models"""
    env_file = ctx.obj['env_file']
    env_vars = dotenv_values(env_file)
    
    click.echo(f"Model configurations from: {env_file}")
    click.echo()
    
    data = []
    for provider in PROVIDERS:
        for size in MODEL_SIZES:
            env_key = f"{provider}_{size}_MODEL"
            model = env_vars.get(env_key, "Not configured")
            
            # Highlight missing configurations
            if model == "Not configured":
                model = click.style(model, fg='red')
            
            data.append([provider, size, model])
    
    print(tabulate(data, headers=["Provider", "Size", "Model"], tablefmt="grid"))


@cli.command()
@click.argument('provider', type=click.Choice(PROVIDERS, case_sensitive=False))
@click.argument('size', type=click.Choice(MODEL_SIZES, case_sensitive=False))
@click.argument('model')
@click.pass_context
def set(ctx, provider, size, model):
    """Set a model configuration"""
    env_file = ctx.obj['env_file']
    env_key = f"{provider.upper()}_{size.upper()}_MODEL"
    
    # Set the value
    set_key(str(env_file), env_key, model)
    click.echo(f"✓ Set {env_key} = {model}")
    
    # Show updated configuration
    env_vars = dotenv_values(env_file)
    click.echo(f"\nCurrent {provider.upper()} models:")
    for s in MODEL_SIZES:
        key = f"{provider.upper()}_{s}_MODEL"
        value = env_vars.get(key, "Not configured")
        if value == "Not configured":
            value = click.style(value, fg='red')
        click.echo(f"  {s}: {value}")


@cli.command()
@click.argument('provider', type=click.Choice(PROVIDERS, case_sensitive=False))
@click.argument('size', type=click.Choice(MODEL_SIZES, case_sensitive=False))
@click.pass_context
def get(ctx, provider, size):
    """Get a specific model configuration"""
    env_file = ctx.obj['env_file']
    env_vars = dotenv_values(env_file)
    
    env_key = f"{provider.upper()}_{size.upper()}_MODEL"
    model = env_vars.get(env_key)
    
    if model:
        click.echo(f"{env_key} = {model}")
    else:
        click.echo(f"{env_key} is not configured", err=True)
        click.echo(f"Default would be: {DEFAULT_MODELS[provider.upper()][size.upper()]}")


@cli.command()
@click.option('--apply', is_flag=True, help='Apply default configurations')
@click.pass_context
def init(ctx, apply):
    """Initialize model configurations with defaults"""
    env_file = ctx.obj['env_file']
    
    if not env_file.exists() and apply:
        env_file.touch()
        click.echo(f"Created: {env_file}")
    
    env_vars = dotenv_values(env_file)
    
    missing = []
    for provider in PROVIDERS:
        for size in MODEL_SIZES:
            env_key = f"{provider}_{size}_MODEL"
            if env_key not in env_vars:
                default = DEFAULT_MODELS[provider][size]
                missing.append((env_key, default))
    
    if not missing:
        click.echo("✓ All model configurations already present")
        return
    
    click.echo(f"Missing {len(missing)} model configurations:")
    click.echo()
    
    for env_key, default in missing:
        click.echo(f"  {env_key} = {default}")
    
    if apply:
        click.echo()
        with click.progressbar(missing, label='Applying defaults') as bar:
            for env_key, default in bar:
                set_key(str(env_file), env_key, default)
        
        click.echo()
        click.echo("✓ Applied all default configurations")
    else:
        click.echo()
        click.echo("Run with --apply to set these defaults")


@cli.command()
@click.pass_context
def validate(ctx):
    """Validate model configurations"""
    env_file = ctx.obj['env_file']
    env_vars = dotenv_values(env_file)
    
    # Required configurations for basic operation
    required = [
        ("ANTHROPIC", ["S", "M", "L"]),
        ("OPENAI", ["S", "M"]),
    ]
    
    missing = []
    warnings = []
    
    # Check required
    for provider, sizes in required:
        for size in sizes:
            env_key = f"{provider}_{size}_MODEL"
            if env_key not in env_vars:
                missing.append(env_key)
    
    # Check for consistency
    for provider in PROVIDERS:
        models_by_size = {}
        for size in MODEL_SIZES:
            env_key = f"{provider}_{size}_MODEL"
            if env_key in env_vars:
                models_by_size[size] = env_vars[env_key]
        
        # Warn if XS/S are more expensive than M/L
        if 'S' in models_by_size and 'M' in models_by_size:
            if 'opus' in models_by_size['S'] and 'haiku' in models_by_size['M']:
                warnings.append(f"{provider}: Small model ({models_by_size['S']}) is more expensive than Medium ({models_by_size['M']})")
    
    # Report results
    if missing:
        click.echo("❌ Missing required configurations:", err=True)
        for key in missing:
            click.echo(f"  - {key}", err=True)
    else:
        click.echo("✓ All required models configured")
    
    if warnings:
        click.echo()
        click.echo("⚠️  Warnings:")
        for warning in warnings:
            click.echo(f"  - {warning}")
    
    if not missing and not warnings:
        click.echo()
        click.echo("✓ Configuration validated successfully")
    
    sys.exit(1 if missing else 0)


@cli.command()
@click.argument('source', type=click.Path(exists=True))
@click.argument('target', type=click.Path())
@click.option('--merge', is_flag=True, help='Merge with existing configuration')
@click.pass_context
def copy(ctx, source, target, merge):
    """Copy model configurations between .env files"""
    source_vars = dotenv_values(source)
    
    # Extract model configurations
    model_configs = {}
    for key, value in source_vars.items():
        if any(key.startswith(f"{p}_") and key.endswith("_MODEL") for p in PROVIDERS):
            model_configs[key] = value
    
    if not model_configs:
        click.echo("No model configurations found in source", err=True)
        return
    
    # Handle target
    target_path = Path(target)
    if target_path.is_dir():
        target_path = target_path / ".env"
    
    if not target_path.exists():
        target_path.touch()
        click.echo(f"Created: {target_path}")
    
    # Apply configurations
    count = 0
    for key, value in model_configs.items():
        if merge or key not in dotenv_values(target_path):
            set_key(str(target_path), key, value)
            count += 1
    
    click.echo(f"✓ Copied {count} model configurations")


@cli.command()
@click.option('--markdown', is_flag=True, help='Output in markdown format')
@click.pass_context
def report(ctx, markdown):
    """Generate a report of model configurations"""
    env_file = ctx.obj['env_file']
    env_vars = dotenv_values(env_file)
    
    # Collect data
    config_by_provider = {}
    for provider in PROVIDERS:
        config_by_provider[provider] = {}
        for size in MODEL_SIZES:
            env_key = f"{provider}_{size}_MODEL"
            config_by_provider[provider][size] = env_vars.get(env_key)
    
    if markdown:
        # Markdown output
        click.echo("# Model Configuration Report")
        click.echo()
        click.echo(f"Generated from: `{env_file}`")
        click.echo()
        
        for provider in PROVIDERS:
            click.echo(f"## {provider}")
            click.echo()
            click.echo("| Size | Model |")
            click.echo("|------|-------|")
            
            for size in MODEL_SIZES:
                model = config_by_provider[provider][size] or "*Not configured*"
                click.echo(f"| {size} | {model} |")
            
            click.echo()
    else:
        # Text output
        click.echo(f"Model Configuration Report")
        click.echo(f"Source: {env_file}")
        click.echo("=" * 60)
        
        for provider in PROVIDERS:
            click.echo(f"\n{provider}:")
            for size in MODEL_SIZES:
                model = config_by_provider[provider][size] or "Not configured"
                status = "✓" if model != "Not configured" else "✗"
                click.echo(f"  {status} {size}: {model}")


if __name__ == "__main__":
    cli()
