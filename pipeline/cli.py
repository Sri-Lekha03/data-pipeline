from __future__ import annotations

import typer

from pipeline.handler import run_pipeline

app = typer.Typer(help="Data Pipeline CLI — run the pipeline locally.")


@app.command()
def run(
    source_bucket: str = typer.Option(..., help="S3 source bucket name"),
    dest_bucket: str = typer.Option(..., help="S3 destination bucket name"),
    date: str = typer.Option(
        ..., help="Date to process in YYYY/MM/DD format"
    ),
    namespace: str = typer.Option(
        "DataPipeline", help="CloudWatch namespace for metrics"
    ),
) -> None:
    """Run the pipeline for a specific date prefix."""
    prefix = f"raw/{date}/"

    typer.echo(f"Starting pipeline for prefix: {prefix}")
    typer.echo(f"Source bucket: {source_bucket}")
    typer.echo(f"Destination bucket: {dest_bucket}")

    result = run_pipeline(
        source_bucket=source_bucket,
        dest_bucket=dest_bucket,
        prefix=prefix,
        cloudwatch_namespace=namespace,
    )

    typer.echo("\nPipeline complete!")
    typer.echo(f"Processed: {result['records_processed']}")
    typer.echo(f"Failed:    {result['records_failed']}")
    typer.echo(f"Duration:  {result['duration_ms']}ms")


if __name__ == "__main__":
    app()