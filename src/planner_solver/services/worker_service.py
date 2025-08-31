import copy
import logging
from enum import IntEnum
from typing import List

from ortools.sat.cp_model_pb2 import CpSolverStatus
from ortools.sat.python.cp_model import CpModel, CpSolver

from planner_solver.exceptions.worker_exceptions import WorkerStatusException
from planner_solver.models.base_models import Scenario, Solver, Resource, Task, Target, WrappedModel, Constraint, \
    ScenarioStatus, TaskStatus, WrappedSolver
from planner_solver.services.mongodb_service import MongodbService
from planner_solver.services.rabbitmq_service import RabbitmqService

logger = logging.getLogger(__name__)

class WorkerTaskInput:
    """
    this class wraps everything needed to execute one worker task
    it is booted directly by the worker service and then sent to be worked
    based on the worker settings
    """

    wrapped_model: WrappedModel
    scenario: Scenario
    solver: CpSolver

    def __init__(
            self,
            wrapped_model: WrappedModel,
            scenario: Scenario,
            solver: CpSolver
    ):
        self.wrapped_model = wrapped_model
        self.scenario = scenario
        self.solver = solver

class WorkerTaskOutputStatus(IntEnum):
    """
    simpler enum to wrap the solver result. The descriptions are copied from cp_model_pb2.pyi
    """
    UNKNOWN = 0
    """
    The status of the model is still unknown. A search limit has been reached
    before any of the statuses below could be determined.
    """
    MODEL_INVALID = 1
    """
    The given CpModelProto didn't pass the validation step. You can get a
    detailed error by calling ValidateCpModel(model_proto).
    """
    FEASIBLE = 2
    """
    A feasible solution has been found. But the search was stopped before we
    could prove optimality or before we enumerated all solutions of a
    feasibility problem (if asked).
    """
    INFEASIBLE = 3
    """
    The problem has been proven infeasible.
    """
    OPTIMAL = 4
    """
    An optimal feasible solution has been found.

    More generally, this status represent a success. So we also return OPTIMAL
    if we find a solution for a pure feasibility problem or if a gap limit has
    been specified and we return a solution within this limit. In the case
    where we need to return all the feasible solution, this status will only be
    returned if we enumerated all of them; If we stopped before, we will return
    FEASIBLE.
    """

    @staticmethod
    def from_cp_status(cp_status: CpSolverStatus) -> "WorkerTaskOutputStatus":
        return WorkerTaskOutputStatus(cp_status)


class WorkerTaskOutput:
    """
    this wraps everything that returns from a worker execution
    on the main thread. Side effects are handled outside
    """
    status: WorkerTaskOutputStatus
    wrapped_solver: WrappedSolver
    scenario: Scenario

    def __init__(
            self,
            status: WorkerTaskOutputStatus,
            wrapped_solver: WrappedSolver,
            scenario: Scenario
    ):
        self.status = status
        self.wrapped_solver = wrapped_solver
        self.scenario = scenario

class WorkerService:
    """
    This service handles the solver and uses it in a scenario
    in order to retrieve the actual calculations
    """

    def __init__(
            self,
            mongodb_service: MongodbService,
            rabbitmq_service: RabbitmqService,
    ):
        self.__mongodb_service = mongodb_service
        self.__rabbitmq_service = rabbitmq_service

    def _boot_model(self) -> WrappedModel:
        model = CpModel()
        variables = {}

        return WrappedModel(
            model=model,
            variables=variables
        )

    # region resources

    def _fetch_resources(
            self,
            scenario: Scenario,
    ) -> List[Resource]:
        """
        returns empty resources, with both their type
        and their actual data, but without altering the current
        model nor calling their specific methods
        """

        non_unique_resources: List[Resource] = []

        # First I get scenario-wide resources
        for res in scenario.get_resources():
            non_unique_resources.append(res)

        # then I get task-specific resources
        for task in scenario.get_tasks():
            task_res = task.get_resources()
            if task_res and len(task_res):
                for res in task_res:
                    non_unique_resources.append(res)

        # and finally I only consider one resource per id
        resources: List[Resource] = []
        # todo implement removal of extra resources

        return non_unique_resources

    def _prepare_resources(
            self,
            wrapped_model: WrappedModel,
            resources: List[Resource]
    ) -> List[Resource]:
        # todo if needed define a sort order here
        for res in resources:
            res.prepare_resource(wrapped_model.model)

        return resources

    # endregion resources

    # region tasks

    def _fetch_tasks(
            self,
            scenario: Scenario,
    ) -> List[Task]:
        # at first, I simply read the tasks
        # todo fetch from db
        tasks = scenario.get_tasks()

        return tasks

    def _evaluate_horizon(
            self,
            tasks: List[Task],
    ) -> int:
        return sum(task.get_max_duration() for task in tasks)

    def _create_tasks_vars(
            self,
            wrapped_model: WrappedModel,
            tasks: List[Task],
            horizon: int,
    ) -> List[Task]:
        for task in tasks:
            # first I create the task variables with their name
            task.generate_cp_sat(wrapped_model, horizon)

        return tasks

    def _link_task_constraints(
            self,
            model: CpModel,
            tasks: List[Task],
    ) -> None:
        """
        appends the task-defined constraints to the model
        """
        for task in tasks:
            constraints = task.get_constraints()
            if constraints and len(constraints):
                for constraint in constraints:
                    constraint.attach_task_constraint(model, task)

    def _link_task_resources(
            self,
            model: CpModel,
            tasks: List[Task],
    ):
        """
        appends the resource-defined constraints to the model
        """
        for task in tasks:
            resources = task.get_resources()
            if resources and len(resources):
                for resource in resources:
                    resource.attach_task_resource(model, task)

    # endregion tasks

    # region scenario

    def _link_scenario_constraints(
            self,
            model: CpModel,
            scenario: Scenario,
    ) -> List[Constraint]:
        """
        appends the constraints related to the scenario to the model
        """
        scenario_constraints = scenario.get_constraints()
        if scenario_constraints and len(scenario_constraints):
            for constraint in scenario_constraints:
                constraint.attach_scenario_constraint(model)
            return scenario_constraints
        else:
            return []

    def _link_scenario_resources(
            self,
            model: CpModel,
            scenario: Scenario,
    ) -> List[Resource]:
        """
        appends the constraints that the resources need to apply to the model
        """
        scenario_resources = scenario.get_resources()
        if scenario_resources and len(scenario_resources):
            for resource in scenario_resources:
                resource.attach_scenario_resource(model)
            return scenario_resources
        else:
            return []

    # endregion scenario

    # region target

    def _link_target(
            self,
            model: CpModel,
            target: Target,
            horizon: int,
            tasks: List[Task]
    ) -> None:
        # todo absolutely generalize this! maybe the wrapped target?
        target.attach_target(model, horizon, tasks)

    # endregion target

    # region solver

    def _link_solver(
            self,
            model: CpModel,
            solver: Solver
    ) -> CpSolver:
        return solver.generate_solver(model)

    # endregion solver

    def prepare_worker(
            self,
            scenario: Scenario,
            solver: Solver,
            target: Target,
    ) -> WorkerTaskInput:
        """
        This creates everything for the cp_solver to work on

        use this result to actually start a worker, based on the settings
        """
        wrapped_model = self._boot_model()
        logger.debug("Created model")

        # todo add preprocessor for fixed statuses

        resources = self._fetch_resources(scenario)
        logger.debug(f"Loaded {len(resources)} resources")

        resources = self._prepare_resources(wrapped_model, resources)
        logger.debug(f"Prepared {len(resources)} resources")

        tasks = self._fetch_tasks(scenario)
        logger.debug(f"Loaded {len(tasks)} tasks")

        horizon = self._evaluate_horizon(tasks)
        logger.debug(f"Set horizon as {horizon} time units")

        self._create_tasks_vars(wrapped_model, tasks, horizon)
        logger.debug(f"Task vars initialized with a total of {len(wrapped_model.variables)} variables")

        # from here on, actual constraints are starting to be added

        # first for the tasks

        self._link_task_constraints(wrapped_model.model, tasks)
        logger.debug(f"Task constraints initialized")

        self._link_task_resources(wrapped_model.model, tasks)
        logger.debug(f"Task resources initialized")

        # then for the whole scenario constraints

        self._link_scenario_constraints(wrapped_model.model, scenario)
        logger.debug(f"Scenario constraints initialized")

        self._link_scenario_resources(wrapped_model.model, scenario)
        logger.debug(f"Scenario resources initialized")

        # the target is now set
        self._link_target(wrapped_model.model, target, horizon, tasks)
        logger.debug(f"Target set")

        cp_solver = self._link_solver(wrapped_model.model, solver)
        logger.debug(f"Solver created")

        return WorkerTaskInput(
            wrapped_model=wrapped_model,
            scenario=scenario,
            solver=cp_solver
        )

    def _assign_scenario_results(
            self,
            wrapped_model: WrappedModel,
            wrapped_solver: WrappedSolver,
            scenario: Scenario,
            solver_status: WorkerTaskOutputStatus
    ) -> Scenario:
        """
        Creates a new scenario with the results obtained from the computation
        """
        solved_scenario = copy.deepcopy(scenario)

        if (solver_status == WorkerTaskOutputStatus.UNKNOWN or
            solver_status == WorkerTaskOutputStatus.MODEL_INVALID or
            solver_status == WorkerTaskOutputStatus.INFEASIBLE):
            raise WorkerStatusException(int(solver_status), 'You should not assign scenario results if model fails')

        # set the scenario status
        solved_scenario.update_scenario_status(ScenarioStatus.SOLVED)

        # set the status for each task and block their data
        for task in solved_scenario.get_tasks():
            task.update_task_status(TaskStatus.PLANNED)

            start = wrapped_solver.solver.value(task.cp_sat.start)
            end = wrapped_solver.solver.value(task.cp_sat.end)

            task.generate_result(
                start=start,
                end=end
            )

        return solved_scenario


    def solve_synchronously(
            self,
            task: WorkerTaskInput
    ) -> WorkerTaskOutput:
        """
        solves the task without any callback during execution
        one thread per worker
        """

        model = task.wrapped_model.model
        variables = task.wrapped_model.variables
        scenario = task.scenario
        solver = task.solver

        wrapped_solver = WrappedSolver(
            solver=solver,
            variables=task.wrapped_model.variables
        )

        solve_status = solver.solve(model)
        logger.debug(f"Model solved with status {solve_status}")

        worker_solver_status = WorkerTaskOutputStatus.from_cp_status(solve_status)

        result_scenario = self._assign_scenario_results(
            wrapped_model=task.wrapped_model,
            wrapped_solver=wrapped_solver,
            scenario=scenario,
            solver_status=worker_solver_status
        )

        return WorkerTaskOutput(
            wrapped_solver=wrapped_solver,
            scenario=result_scenario,
            status=worker_solver_status
        )