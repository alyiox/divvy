from typing import Any


def apply_dict_updates[T](entity: object, update_data: dict[str, Any], excluded_attrs: set[str] | None) -> None:
    """
    Dynamically applies key-value pairs from a dictionary to a type-safe ORM entity.

    Args:
        entity: The SQLAlchemy ORM object loaded into the session. Type is inferred as T.
        update_data: Dictionary of fields and values to update.
        excluded_attrs: List of attribute names to explicitly ignore/skip updating.
    """
    excluded_attrs = excluded_attrs if excluded_attrs else set()
    for key, value in update_data.items():

        if key in excluded_attrs:
            continue

        if hasattr(entity, key):
            setattr(entity, key, value)
