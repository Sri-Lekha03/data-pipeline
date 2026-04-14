from __future__ import annotations

from unittest.mock import patch

from typer.testing import CliRunner

from pipeline.cli import app

runner = CliRunner()


def test_cli_run_calls_pipeline() -> None:
    """CLI run command should call run_pipeline with correct args."""
    with patch("pipeline.cli.run_pipeline") as mock_pipeline:
        mock_pipeline.return_value = {
            "records_processed": 3,
            "records_failed": 0,
            "duration_ms": 123.45,
        }
        result = runner.invoke(app, [
            "--source-bucket=my-source",
            "--dest-bucket=my-dest",
            "--date=2026/04/11",
        ])

    assert result.exit_code == 0, result.output
    assert "Pipeline complete" in result.output
    assert "Processed: 3" in result.output
    mock_pipeline.assert_called_once_with(
        source_bucket="my-source",
        dest_bucket="my-dest",
        prefix="raw/2026/04/11/",
        cloudwatch_namespace="DataPipeline",
    )


def test_cli_shows_failed_count() -> None:
    """CLI should display failed record count."""
    with patch("pipeline.cli.run_pipeline") as mock_pipeline:
        mock_pipeline.return_value = {
            "records_processed": 1,
            "records_failed": 2,
            "duration_ms": 50.0,
        }
        result = runner.invoke(app, [
            "--source-bucket=src",
            "--dest-bucket=dst",
            "--date=2026/04/11",
        ])

    assert result.exit_code == 0, result.output
    assert "Failed:    2" in result.output