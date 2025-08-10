from planner_solver.models.decorators.task import Task, TaskParameter


@Task(type_name="fixed_duration_task")
class FixedDurationTask:
    duration = TaskParameter()