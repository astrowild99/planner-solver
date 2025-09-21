from enum import IntEnum
from ortools.sat.cp_model_pb2 import CpSolverStatus


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