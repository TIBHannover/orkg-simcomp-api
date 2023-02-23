def _query_enums(openapi_schema):
    """
    returns a list of query parameter names that are defined as enums in our openapi_schema.
    """
    params = _query_params(openapi_schema)

    enums = []
    for param in params:
        refs = _param_refs(param)

        for ref in refs:
            if 'enum' in openapi_schema['components']['schemas'][ref]:
                enums.append(param['name'])

    return enums


def _query_params(openapi_schema):
    """
    returns a list of dicts of query parameter names and their schemas that are defined in our openapi_schema.
    """

    params = []

    for _, path_schema in openapi_schema['paths'].items():
        for _, method_schema in path_schema.items():
            for param in method_schema.get('parameters', []):
                params.append({
                    'name': param['name'],
                    'schema': param['schema']
                })

    return params


def _param_refs(param):
    """
    returns a list of component refs for the given param.
    """
    refs = []

    if '$ref' in param['schema']:
        ref = param['schema'].get('$ref', '')
        _, _, ref = ref.rpartition('/')
        refs.append(ref)

    for item in param['schema'].get('allOf', []):
        if '$ref' in item:
            ref = item.get('$ref', '')
            _, _, ref = ref.rpartition('/')
            refs.append(ref)

    return refs
