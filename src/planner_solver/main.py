from planner_solver.containers.application import ApplicationContainer
from datetime import datetime

def run():
    container = ApplicationContainer()

    time_service = container.time_service()
    
    print (time_service.convert(datetime.now()))