from abc import ABC
from typing import Type, get_origin, Union, get_args, Optional, Literal


class Parameter(ABC):
    """
    the parameters that you can add to the single
    resource type
    """
    def __init__(
            self,
            param_type: Type,
            link: Optional[Literal['task', 'resource', 'constraint']] = None,
            extra_name: str | None = None
    ):
        self.param_type = param_type
        self.name = None
        self.extra_name = extra_name
        self.private_name = None
        self.link = link

    def __set_name__(self, owner, name):
        """
        Called when this is assigned to an attribute, the ONLY place you can use it
        """
        self.name = name
        if self.extra_name is None:
            self.extra_name = name
        self.private_name = f"_{name}"
        if self.link is not None:
            setattr(owner, f"_ps_link_{name}", self.link)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.private_name, None)

    def __set__(self, instance, value):

        setattr(instance, self.private_name, value)

    def resolve_value(self, instance):
        """
        Resolves the parameter value. If it's a string UUID, it should be hydrated.
        If it's already an object, return it directly.
        This method is used by constraints and other components to get the resolved value.
        """
        value = getattr(instance, self.private_name, None)

        if value is None:
            return None

        # If it's already an object (hydrated), return it
        if not isinstance(value, str):
            return value

        # If it's a string UUID, it should have been hydrated by mongodb_service.hydrate_parameter_links()
        # If we reach here with a string, it means hydration wasn't called
        raise ValueError(f"Parameter '{self.name}' contains unresolved UUID '{value}'. "
                        f"Call mongodb_service.hydrate_parameter_links() first.")

    # region type validation

    def _is_valid_type(self, value) -> bool:
        try:
            # Handle Union types (e.g., str | int, Union[str, int])
            origin = get_origin(self.param_type)
            if origin is Union:
                union_args = get_args(self.param_type)
                return any(self._check_single_type(value, arg) for arg in union_args)

            # Handle single types
            return self._check_single_type(value, self.param_type)

        except Exception:
            # Fallback to isinstance for complex cases
            return isinstance(value, self.param_type)

    def _check_single_type(self, value, expected_type) -> bool:
        """Check if value matches a single type (not Union)"""
        try:
            # For generic types (List, Dict, etc.), check the origin
            origin = get_origin(expected_type)
            if origin is not None:
                return isinstance(value, origin)

            # For regular types, use isinstance
            return isinstance(value, expected_type)

        except TypeError:
            # Handle cases where isinstance doesn't work with certain types
            return type(value) == expected_type

    # endregion type validation