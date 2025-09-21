from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Set, Tuple
from enum import Enum, IntEnum

from ortools.sat.python.cp_model import CpModel, CpSolver, IntVar, IntervalVar
from pydantic import BaseModel

from planner_solver.exceptions.type_exceptions import TypeException
from planner_solver.models.forms import BasePlannerSolverForm
from planner_solver.models.stored_documents import BasePlannerSolverDocument


# this file contains all the really basic classes
# that will be handled and used, and extended alongside their
# type definitions by the runner and stored to and from the
# planning tasks

class WrappedModel(BaseModel):
    """
    Wraps the model and its variables for easy retrieval
    """
    model: CpModel
    variables: Dict[str, Any]

    class Config:
        arbitrary_types_allowed = True

class WrappedSolver(BaseModel):
    """
    Wraps the solver and its variables for easy retrieval
    """
    solver: CpSolver
    variables: Dict[str, Any]

    class Config:
        arbitrary_types_allowed = True

class CpSatTask(BaseModel):
    """
    the cp-sat variables that I need to link to a task
    """
    start: Optional[IntVar]
    end: Optional[IntVar]
    interval: Optional[IntervalVar]

    class Config:
        arbitrary_types_allowed = True

class ResultTask(BaseModel):
    start: Optional[int]
    end: Optional[int]

    class Config:
        arbitrary_types_allowed = True

class PlannerSolverBaseModel(BaseModel):
    """
    wraps a planner solver entity for easy retrieval and type checking
    """
    __is_planner_solver_model = True

    label: str | None = None
    """this one is stored in every entity"""
    uuid: str | None = None
    """This is specified only when retrieved from the database"""

    def __exclude_hydration(self) -> Tuple[Set[str], Set[str], Set[str]]:
        from beanie.odm.fields import PydanticObjectId
        excluded = set()
        beanie_models = set()
        base_models = set()

        # Iterate through all attributes of this instance
        for attr_name in dir(self):
            if not attr_name.startswith('_'):  # Skip private attributes
                try:
                    attr_value = getattr(self, attr_name)

                    # Check if the attribute has a beanie id (PydanticObjectId)
                    if hasattr(attr_value, 'id') and isinstance(getattr(attr_value, 'id'), PydanticObjectId):
                        excluded.add(attr_name)
                        beanie_models.add(attr_name)
                    # Check if the attribute has __ps_type_name (indicating it's a hydrated model)
                    elif hasattr(attr_value, '__ps_type_name'):
                        excluded.add(attr_name)
                        base_models.add(attr_name)
                    # Check for lists/collections of hydrated models or beanie objects
                    elif hasattr(attr_value, '__iter__') and not isinstance(attr_value, (str, bytes)):
                        try:
                            for item in attr_value:
                                has_beanie_id = hasattr(item, 'id') and isinstance(getattr(item, 'id'), PydanticObjectId)
                                if has_beanie_id or hasattr(item, '__ps_type_name'):
                                    excluded.add(attr_name)
                                    beanie_models.add(attr_name)
                                    break
                        except (TypeError, AttributeError):
                            # Skip if not iterable or other issues
                            pass
                except (AttributeError, TypeError):
                    # Skip if we can't access the attribute
                    pass

        return excluded, beanie_models, base_models

    def to_form(
            self,
            hydrate: bool = True,
            max_depth: int = 3,
    ) -> BasePlannerSolverForm:
        if not hasattr(self, '__ps_type_name'):
            raise TypeException("Make sure to cast to a type decorated with the module type")

        if hydrate:
            excluded, beanie_models, base_models = self.__exclude_hydration()
        else:
            excluded = set()
            beanie_models = set()
            base_models = set()

        dumped = self.model_dump(
            exclude=excluded
        )

        # and now I hydrate the ones that I excluded, following the same behavior used to hydrate myself
        dumped = self.__hydrate(
            data=dumped,
            beanie_models_fields=beanie_models,
            base_models_field=base_models,
            max_depth=max_depth,
        )

        return BasePlannerSolverForm(
            type=getattr(self, '__ps_type_name'),
            data=dumped,
        )

    def __hydrate(
            self,
            data: Dict[str, Any],
            beanie_models_fields: Set[str],
            base_models_field: Set[str],
            max_depth: int = 3,
    ) -> Dict[str, Any]:
        """
        hydrates the link beanie_models_fields
        """
        if max_depth == 0:
            return data

        for f in beanie_models_fields:
            if hasattr(self, f):
                attr: BasePlannerSolverDocument = getattr(self, f)
                hydrated_form = attr.to_base_model().to_form(max_depth=max_depth - 1)
                data[f] = hydrated_form.model_dump()
            else:
                raise Exception(f"Trying to serialize missing beanie attribute {f}")

        for f in base_models_field:
            if hasattr(self, f):
                attr: PlannerSolverBaseModel = getattr(self, f)
                hydrated_form = attr.to_form(max_depth=max_depth - 1)
                data[f] = hydrated_form.model_dump()
            else:
                raise Exception(f"Trying to serialize missing base attribute {f}")

        return data

    model_config = {
        "arbitrary_types_allowed": True,
        "extra": "allow"
    }

class Constraint(ABC, PlannerSolverBaseModel):
    """
    The constraint, as defined in the generic constraint satisfaction
    problem, is here a set that links two or more tasks (or in general, whatever element
    in this file)
    """

    @abstractmethod
    def attach_task_constraint(self, model: CpModel, task: "Task") -> None:
        pass

    @abstractmethod
    def attach_scenario_constraint(self, model: CpModel) -> None:
        pass

class Resource(ABC, PlannerSolverBaseModel):
    """
    the resource identifies all the stuffs that are linked
    to the full planning event, and that have a finite quantity
    thus has to create constraints to check their availability

    e.g. a resource is the machine, the number of operators
    or the max current drain of the shop floor
    """

    @abstractmethod
    def prepare_resource(self, model: CpModel) -> None:
        pass

    @abstractmethod
    def attach_task_resource(self, model: CpModel, task: "Task"):
        pass

    @abstractmethod
    def attach_scenario_resource(self, model: CpModel) -> None:
        pass

class TaskStatus(Enum):
    """
    The status of a task
    """
    CREATED = 0
    """task data are here, but the solver variables are not yet ready
    """
    READY = 1
    """ready to be planned, still not determined
    """
    PLANNED = 2
    """the content within the status is determined by the solver
    """
    FIXED = 3
    """external factors (e.g. current realization status) set the start and end of the task
    """

class Task(ABC, PlannerSolverBaseModel):
    """
    The task is the single atomic value that can be planned
    by itself is not usable, as per every other type you need to
    provide a decorated type that can be manipulated
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__status = TaskStatus.CREATED
        self.cp_sat: None | CpSatTask = None
        self.result: None | ResultTask = None

    def get_task_status(self) -> TaskStatus:
        return self.__status

    def update_task_status(self, task_status: TaskStatus):
        """
        Only the solver should set this to PLANNED
        """
        self.__status = task_status

    def generate_result(
            self,
            start: int,
            end: int
    ) -> ResultTask:
        res = ResultTask(
            start=start,
            end=end
        )
        self.result = res
        return res

    @abstractmethod
    def generate_cp_sat(
            self,
            wrapped_model: WrappedModel,
            horizon: int
    ) -> CpSatTask:
        """
        generates and stores in the task the cpSatTask
        filling the wrapped model
        """

    @abstractmethod
    def get_unique_id(self) -> str:
        pass

    @abstractmethod
    def get_duration(self) -> int:
        """
        the duration is evaluated right before the task is turned into
        a set of solver variables
        this means that, for tasks where this duration can depend on different
        variables, you have to take into account the existence of these dependencies
        """
        pass

    @abstractmethod
    def get_max_duration(self) -> int:
        """
        if the duration is not fixed, this has to return the max duration that the task
        can use, so that it becomes possible to evaluate the horizon for the model
        """
        pass

    @abstractmethod
    def get_constraints(self) -> List[Constraint]:
        """
        returns the task-level constraints
        this is evaluated right before the model is run, in order to create the constraints
        based on the task implementation these can either be stored or evaluated
        """
        pass

    @abstractmethod
    def add_constraint(self, constraint: Constraint) -> None:
        """
        adds a task-level constraint
        """
        pass

    @abstractmethod
    def get_resources(self) -> List[Resource]:
        """
        returns the list of task-level resources

        this is mainly used for specific non-fungible resources
        like the machine or department
        when the resource is instead used across many (e.g. the availability of operators regardless
        of their specification) will be a scenario-level resource
        """
        pass

    @abstractmethod
    def add_resource(self, resource: Resource) -> None:
        """
        adds a new task-level resource
        """
        pass

class Target(ABC, PlannerSolverBaseModel):
    """
    the target function definition, that instructs the model
    on the min/maxes that it needs to set as target
    """

    @abstractmethod
    def attach_target(
            self,
            model: CpModel,
            horizon: int,
            tasks: List[Task]
    ) -> None:
        pass

class ScenarioStatus(IntEnum):
    """
    the current status of a scenario
    """
    CREATED = 0 # scenario variables loaded, not yet ready for the solver
    READY = 1 # ready to be solved
    SOLVED = 2 # already solved
    UNSOLVABLE = 99 # the solver couldn't find a solution

class Scenario(ABC, PlannerSolverBaseModel):
    """
    A scenario is a finite set (solvable or unsolvable) of tasks, constraints and resources
    that can be solved by the solver.

    It models a real world scenario for the planning. e.g. a week of work on the shop floor
    or the completion of a task
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__status = ScenarioStatus.CREATED

    def get_scenario_status(self) -> ScenarioStatus:
        return self.__status

    def update_scenario_status(self, solve_status: ScenarioStatus):
        """
        only the solver should set this to solved
        """
        self.__status = solve_status

    @abstractmethod
    def get_tasks(self) -> List[Task]:
        """
        lists all the tasks within the scenario

        based on the status, those will either be planned, solved or fixed
        """
        pass

    @abstractmethod
    def add_task(self, task: Task) -> None:
        """
        Adds a task to the list, taking into account its status
        """
        pass

    @abstractmethod
    def get_constraints(self) -> List[Constraint]:
        """
        Returns the scenario-wide constraints
        """
        pass

    @abstractmethod
    def add_constraint(self, constraint: Constraint):
        pass

    @abstractmethod
    def get_resources(self) -> List[Resource]:
        """
        Returns the scenario-wide resources
        """
        pass

    @abstractmethod
    def add_resource(self, resource: Resource):
        pass

class Solver(ABC, PlannerSolverBaseModel):
    """
    The solvers are a set of extra settings around the
    cp sat solver. The system depends on the CPSat interface to function
    but various tweaks on the initialization and parameters can be performed and
    stored as Solvers
    """

    @abstractmethod
    def generate_solver(self, model: CpModel) -> CpSolver:
        pass