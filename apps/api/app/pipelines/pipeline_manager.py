"""Pipeline Manager - Manage AI processing pipelines."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession


class PipelineStatus(str, Enum):
    """Pipeline execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PipelineExecution:
    """Pipeline execution record."""

    execution_id: UUID
    pipeline_name: str
    status: PipelineStatus
    input_data: dict[str, Any]
    output_data: Optional[dict[str, Any]]
    started_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    metadata: dict[str, Any]


class PipelineManager:
    """Manage AI processing pipelines."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize pipeline manager.

        Args:
            db: Database session
        """
        self.db = db
        self.pipelines: dict[str, Callable] = {}
        self.executions: dict[UUID, PipelineExecution] = {}

    def register_pipeline(
        self,
        name: str,
        pipeline_fn: Callable,
    ) -> None:
        """Register a pipeline.

        Args:
            name: Pipeline name
            pipeline_fn: Pipeline function
        """
        self.pipelines[name] = pipeline_fn

    async def execute_pipeline(
        self,
        pipeline_name: str,
        input_data: dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
    ) -> PipelineExecution:
        """Execute a pipeline.

        Args:
            pipeline_name: Name of pipeline to execute
            input_data: Input data for pipeline
            metadata: Optional metadata

        Returns:
            PipelineExecution object
        """
        execution_id = uuid4()
        execution = PipelineExecution(
            execution_id=execution_id,
            pipeline_name=pipeline_name,
            status=PipelineStatus.RUNNING,
            input_data=input_data,
            output_data=None,
            started_at=datetime.now(timezone.utc),
            completed_at=None,
            error_message=None,
            metadata=metadata or {},
        )

        self.executions[execution_id] = execution

        try:
            pipeline_fn = self.pipelines.get(pipeline_name)
            if not pipeline_fn:
                raise ValueError(f"Pipeline {pipeline_name} not found")

            # Execute pipeline
            output_data = await pipeline_fn(input_data)

            execution.status = PipelineStatus.COMPLETED
            execution.output_data = output_data
            execution.completed_at = datetime.now(timezone.utc)

        except Exception as e:
            execution.status = PipelineStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.now(timezone.utc)

        return execution

    async def get_execution(self, execution_id: UUID) -> Optional[PipelineExecution]:
        """Get a pipeline execution.

        Args:
            execution_id: Execution ID

        Returns:
            PipelineExecution or None
        """
        return self.executions.get(execution_id)

    async def cancel_execution(self, execution_id: UUID) -> bool:
        """Cancel a pipeline execution.

        Args:
            execution_id: Execution ID

        Returns:
            True if cancelled
        """
        execution = self.executions.get(execution_id)
        if execution and execution.status == PipelineStatus.RUNNING:
            execution.status = PipelineStatus.CANCELLED
            execution.completed_at = datetime.now(timezone.utc)
            return True
        return False

    async def list_executions(
        self,
        pipeline_name: Optional[str] = None,
        status: Optional[PipelineStatus] = None,
        limit: int = 100,
    ) -> list[PipelineExecution]:
        """List pipeline executions.

        Args:
            pipeline_name: Optional pipeline name filter
            status: Optional status filter
            limit: Maximum number of results

        Returns:
            List of PipelineExecution objects
        """
        executions = list(self.executions.values())

        if pipeline_name:
            executions = [e for e in executions if e.pipeline_name == pipeline_name]

        if status:
            executions = [e for e in executions if e.status == status]

        # Sort by started time descending
        executions.sort(key=lambda x: x.started_at, reverse=True)

        return executions[:limit]
