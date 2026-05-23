"""Report Generator - Generate evaluation reports."""

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.benchmarking.evaluation_suite import EvaluationResult


@dataclass
class Report:
    """Evaluation report."""

    report_id: str
    title: str
    evaluations: list[EvaluationResult]
    summary: dict[str, Any]
    generated_at: datetime


class ReportGenerator:
    """Generate comprehensive evaluation reports."""

    def generate_report(
        self,
        evaluations: list[EvaluationResult],
        title: str = "AI Evaluation Report",
    ) -> Report:
        """Generate an evaluation report.

        Args:
            evaluations: List of evaluation results
            title: Report title

        Returns:
            Report object
        """
        summary = self._generate_summary(evaluations)

        report = Report(
            report_id=f"report_{int(datetime.now(timezone.utc).timestamp())}",
            title=title,
            evaluations=evaluations,
            summary=summary,
            generated_at=datetime.now(timezone.utc),
        )

        return report

    def _generate_summary(self, evaluations: list[EvaluationResult]) -> dict[str, Any]:
        """Generate summary from evaluations.

        Args:
            evaluations: List of evaluation results

        Returns:
            Summary dictionary
        """
        total_evaluations = len(evaluations)
        successful_evaluations = sum(1 for e in evaluations if all(m >= 0 for m in e.metrics.values()))

        return {
            "total_evaluations": total_evaluations,
            "successful_evaluations": successful_evaluations,
            "success_rate": successful_evaluations / total_evaluations if total_evaluations > 0 else 0,
            "evaluation_names": [e.name for e in evaluations],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def to_json(self, report: Report) -> str:
        """Convert report to JSON.

        Args:
            report: Report object

        Returns:
            JSON string
        """
        return json.dumps(
            {
                "report_id": report.report_id,
                "title": report.title,
                "evaluations": [
                    {
                        "evaluation_id": str(e.evaluation_id),
                        "name": e.name,
                        "metrics": e.metrics,
                        "timestamp": e.timestamp.isoformat(),
                        "metadata": e.metadata,
                    }
                    for e in report.evaluations
                ],
                "summary": report.summary,
                "generated_at": report.generated_at.isoformat(),
            },
            indent=2,
        )

    def to_markdown(self, report: Report) -> str:
        """Convert report to Markdown.

        Args:
            report: Report object

        Returns:
            Markdown string
        """
        lines = [
            f"# {report.title}",
            f"\nGenerated at: {report.generated_at.isoformat()}",
            f"\n## Summary",
            f"- Total Evaluations: {report.summary['total_evaluations']}",
            f"- Successful Evaluations: {report.summary['successful_evaluations']}",
            f"- Success Rate: {report.summary['success_rate']:.2%}",
            f"\n## Evaluations",
        ]

        for eval in report.evaluations:
            lines.append(f"\n### {eval.name}")
            lines.append(f"**Timestamp:** {eval.timestamp.isoformat()}")
            lines.append("\n**Metrics:**")
            for key, value in eval.metrics.items():
                lines.append(f"- {key}: {value}")

        return "\n".join(lines)
