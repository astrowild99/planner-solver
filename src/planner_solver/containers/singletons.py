"""
this file contains all the singletons

Using a separate file to avoid circular dependencies, only put
here the boot of singletons that cannot pass through the dependency
injection

whenever possible, add services to the dependency injector and NOT HERE
"""
from planner_solver.services.types_service import TypesService

# beware! this is created every time you import this file, so be sure
# to handle it with care
types_service = TypesService()