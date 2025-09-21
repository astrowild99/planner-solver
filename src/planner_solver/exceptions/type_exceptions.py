class TypeException(Exception):
    pass

class ConstraintAttachTypeException(Exception):
    """
    thrown when a constraint is attached to a non-related type
    see constraint::attachable_to property
    """
    pass