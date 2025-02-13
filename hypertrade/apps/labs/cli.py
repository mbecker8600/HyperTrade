from datetime import datetime

import click


# trunk-ignore-all(mypy,bandit,pyright)
@click.group()
def cli() -> None:
    pass


@cli.command(help="Run a backtest")
@click.option("--start-date", type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option("--end-date", type=click.DateTime(formats=["%Y-%m-%d"]))
def backtest(start_date: datetime, end_date: datetime) -> None:
    print("Running backtest")


if __name__ == "__main__":
    cli()
