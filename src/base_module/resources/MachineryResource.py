from planner_solver.models.decorators.resource_type import ResourceParameter, ResourceType


@ResourceType(type_name="machinery_resource")
class MachineryResource:
    machine_name = ResourceParameter()