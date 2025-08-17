from planner_solver.containers.application import ApplicationContainer
from datetime import datetime

from planner_solver.services.types_service import TypesService

def run():
    container = ApplicationContainer()
    container.init_resources()

    time_service = container.time_service()
    module_loader = container.module_loader_service()
    mongodb_service = container.mongodb_service()
    rabbitmq_service = container.rabbitmq_service()

    module_loader.load_all()
    
    print (time_service.convert(datetime.now()))
    print ("Loaded " + str(len(module_loader.loaded_modules)) + " modules")

def runner_run():
    container = ApplicationContainer()
    container.init_resources()

    time_service = container.time_service()
    module_loader = container.module_loader_service()
    mongodb_service = container.mongodb_service()
    rabbitmq_service = container.rabbitmq_service()

    module_loader.load_all()

    print (time_service.convert(datetime.now()))
    print ("Loaded " + str(len(module_loader.loaded_modules)) + " modules")