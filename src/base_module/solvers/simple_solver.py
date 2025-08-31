from ortools.sat.python.cp_model import CpModel, CpSolver

from planner_solver.decorators.solver_type import SolverType
from planner_solver.models.base_models import Solver


@SolverType(type_name="simple_solver")
class SimpleSolver(Solver):
    """
    This solver uses the default CpSat settings to generate a solver
    """

    def generate_solver(self, model: CpModel) -> CpSolver:
        return CpSolver()

