from planner_solver.models.decorators.resource import ResourceParameter, Resource


@Resource(type_name="machinery_resource")
class MachineryResource:
    machine_name = ResourceParameter()