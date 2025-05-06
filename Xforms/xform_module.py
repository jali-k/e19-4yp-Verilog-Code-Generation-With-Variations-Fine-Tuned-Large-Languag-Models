def int_to_shortint_xform(design, xform_to_all=False, xform_target=None):
    """
    # Transform int variables to shortint

    Input:
        - design: The design object that we will be transforming.
        - xform_to_all: If this switch is enable, we will do the transformation wherever possible. Default is False.
        - xform_target: Specific target to transform if not transforming all.

    Note:
        - It will only transform variables with type 'int' to 'shortint'.
        - It will not transform parameter types or struct field types.
    """

    def is_target(obj):
        if not isinstance(obj, (Variable, Declaration)):
            return False
        if xform_target and obj != xform_target:
            return False
        return True

    # Process variable declarations
    for obj in next(iter(design)):
        if not is_target(obj):
            continue

        # Check if variable is of type 'int'
        if hasattr(obj, "type") and obj.type == "int":
            print(f"Transforming {obj.name} from 'int' to 'shortint'")
            obj.type = "shortint"

    # Also process function/task parameters
    for func in design.get_all_objs(Function):
        for param in func.get_params():
            if xform_to_all or (xform_target and param == xform_target):
                if hasattr(param, "type") and param.type == "int":
                    print(
                        f"Transforming parameter {param.name} from 'int' to 'shortint' in function {func.name}"
                    )
                    param.type = "shortint"

    # Also process method parameters
    for method in design.get_all_objs(Method):
        for param in method.get_params():
            if xform_to_all or (xform_target and param == xform_target):
                if hasattr(param, "type") and param.type == "int":
                    print(
                        f"Transforming parameter {param.name} from 'int' to 'shortint' in method {method.name}"
                    )
                    param.type = "shortint"

    return True
