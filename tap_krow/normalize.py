"""Flatten a dict"""
import logging
import types


def _flatten_dict_gen(d, parent_key, delimiter):
    for k, v in d.items():
        new_key = parent_key + delimiter + k if parent_key else k
        if isinstance(v, dict):
            yield from flatten_dict(v, new_key, delimiter=delimiter).items()
        else:
            yield new_key, v


def remove_unnecessary_keys(d, keys_to_remove=types.MappingProxyType({}), path=""):
    """Restructure the dict by removing unnecessary keys
    that just muddle the output. If the key points to a dictionary, the child items are promoted to the removed parent's level"""
    original_path = path
    res = {}
    # loop over keys
    for key, value in d.items():
        path = f"{original_path}/{key}"
        # if any match a key to remove, get the children nodes and make them siblings
        if key in keys_to_remove:
            logging.debug(f'removing key "{key}" from path {path}')
            # if dict, promote the children
            if isinstance(d[key], dict):
                for child_key, child_value in d[key].items():
                    logging.debug(
                        f"""promoting child key "{child_key}" of parent "{key}" in path
                         "{path}/{child_key}", because "{key}" is being removed"""
                    )
                    if child_key in d:
                        raise Exception(
                            f'The key "{child_key}" already exists in the output, so cannot promote the child of key "{key}"'
                        )
                    if isinstance(child_value, dict):
                        res[child_key] = remove_unnecessary_keys(child_value, keys_to_remove, path)
                    else:
                        res[child_key] = child_value
            # else if not a dict, do nothing and the key is effectively removed from the resulting dict
        else:
            if isinstance(d[key], dict):
                # recurse through the children
                res[key] = remove_unnecessary_keys(value, keys_to_remove, path)
            else:
                res[key] = value
    # run the same function for each child dict, using the output as the new value
    return res


def flatten_dict(d, parent_key: str = "", delimiter: str = "_"):
    return dict(_flatten_dict_gen(d, parent_key, delimiter))


def make_fields_meltano_select_compatible(d):
    res = {}
    for k, _v in d.items():
        cleaned_key = k.replace(".", "_")
        if isinstance(d[k], dict):
            res[cleaned_key] = make_fields_meltano_select_compatible(d[k])
        else:
            res[cleaned_key] = d[k]
    return res
