"""
CISCO SAMPLE CODE LICENSE Version 1.1 Copyright (c) 2022 Cisco and/or its affiliates

These terms govern this Cisco Systems, Inc. ("Cisco"), example or demo source code and its associated documentation (together, the "Sample Code"). 
By downloading, copying, modifying, compiling, or redistributing the Sample Code, you accept and agree to be bound by the following terms and 
conditions (the "License"). If you are accepting the License on behalf of an entity, you represent that you have the authority to do so 
(either you or the entity, "you"). Sample Code is not supported by Cisco TAC and is not tested for quality or performance. 
This is your only license to the Sample Code and all rights not expressly granted are reserved.
"""

from ThousandEyes import ThousandEyes
import logging
import sys
import click
from rich.console import Console

@click.group()
@click.pass_context
def cli(ctx):
    """
    Manage Thousand Eyes Agent on Catalyst 9000
    """
    ctx.ensure_object(dict)
    pass

@cli.command()
@click.option("--config", "-c", required=True, type=str, help="Config")
@click.pass_context
def deploy(ctx, config):
    """
    Deploy Thousand Eyes Agent
    """
    print("Deploying Thousand Eyes Agents")
    cfg = ThousandEyes.Configs.load(config=config)
    proccess = ThousandEyes(cfg)

    for host, override in cfg.hosts.items():
        try:
            proccess.deploy(host=host, vlan=cfg.vlan)
        except Exception as error_msg:
            print(f"Can't connect to {host} - {error_msg}")
            pass


if __name__ == "__main__":
    cli()
