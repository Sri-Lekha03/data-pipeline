from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

import boto3


@dataclass
class PipelineMetrics:
    records_processed: int = 0
    records_failed: int = 0
    start_time: float = field(default_factory=time.time)

    @property
    def duration_ms(self) -> float:
        return (time.time() - self.start_time) * 1000

    def to_dict(self) -> dict[str, float]:
        return {
            "records_processed": self.records_processed,
            "records_failed": self.records_failed,
            "duration_ms": round(self.duration_ms, 2),
        }

    def print_summary(self) -> None:
        """Print structured JSON summary to stdout."""
        print(json.dumps(self.to_dict(), indent=2))

    def emit_to_cloudwatch(self, namespace: str = "DataPipeline") -> None:
        """Emit metrics to CloudWatch."""
        client = boto3.client("cloudwatch")
        metrics = self.to_dict()

        client.put_metric_data(
            Namespace=namespace,
            MetricData=[
                {
                    "MetricName": name,
                    "Value": value,
                    "Unit": "Milliseconds" if name == "duration_ms" else "Count",
                }
                for name, value in metrics.items()
            ],
        )