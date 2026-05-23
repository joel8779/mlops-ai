"""GitHub log parser - Parse GitHub Actions logs for failure analysis."""

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class GitHubLogEntry:
    """Parsed GitHub Actions log entry."""

    step_name: str
    status: str
    error_message: Optional[str]
    duration_seconds: Optional[float]
    timestamp: datetime
    raw_log: str


class GitHubLogParser:
    """Parse GitHub Actions logs for failure analysis."""

    def __init__(self) -> None:
        """Initialize GitHub log parser."""
        self.entries: list[GitHubLogEntry] = []

    def parse_log(self, log_content: str) -> list[GitHubLogEntry]:
        """Parse GitHub Actions log content.

        Args:
            log_content: Raw log content from GitHub Actions

        Returns:
            List of GitHubLogEntry objects
        """
        self.entries = []
        
        # Split log into sections (steps)
        sections = self._split_into_sections(log_content)
        
        for section in sections:
            entry = self._parse_section(section)
            if entry:
                self.entries.append(entry)
        
        return self.entries

    def _split_into_sections(self, log_content: str) -> list[str]:
        """Split log content into step sections.

        Args:
            log_content: Raw log content

        Returns:
            List of section strings
        """
        # GitHub Actions logs have step markers
        sections = re.split(r'##\[group\]|##\[endgroup\]', log_content)
        return [s.strip() for s in sections if s.strip()]

    def _parse_section(self, section: str) -> Optional[GitHubLogEntry]:
        """Parse a single log section.

        Args:
            section: Section string

        Returns:
            GitHubLogEntry or None
        """
        # Extract step name
        step_match = re.search(r'##\[(.*?)\]', section)
        if not step_match:
            return None
        
        step_name = step_match.group(1)
        
        # Determine status
        status = "unknown"
        if "Error" in section or "failed" in section.lower():
            status = "failed"
        elif "Success" in section or "passed" in section.lower():
            status = "success"
        
        # Extract error message
        error_match = re.search(r'Error: (.*)$', section, re.MULTILINE)
        error_message = error_match.group(1) if error_match else None
        
        # Extract duration if available
        duration_match = re.search(r'Duration: (\d+)s', section)
        duration = float(duration_match.group(1)) if duration_match else None
        
        return GitHubLogEntry(
            step_name=step_name,
            status=status,
            error_message=error_message,
            duration_seconds=duration,
            timestamp=datetime.now(timezone.utc),
            raw_log=section,
        )

    def get_failed_steps(self) -> list[GitHubLogEntry]:
        """Get all failed steps.

        Returns:
            List of failed GitHubLogEntry objects
        """
        return [e for e in self.entries if e.status == "failed"]

    def get_error_summary(self) -> dict[str, Any]:
        """Get summary of errors.

        Returns:
            Summary dictionary
        """
        failed_steps = self.get_failed_steps()
        
        return {
            "total_steps": len(self.entries),
            "failed_steps": len(failed_steps),
            "failed_step_names": [e.step_name for e in failed_steps],
            "errors": [e.error_message for e in failed_steps if e.error_message],
        }
