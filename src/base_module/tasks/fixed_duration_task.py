from planner_solver.models.decorators.task_type import TaskType, TaskParameter


@TaskType(type_name="fixed_duration_task")
class FixedDurationTask:
    duration = TaskParameter()