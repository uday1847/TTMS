import os
import ast
import inspect

def get_service_methods():
    import sys
    sys.path.insert(0, os.getcwd())
    
    methods = {}
    service_dir = 'app/application/services'
    for f in os.listdir(service_dir):
        if f.endswith('.py') and f != '__init__.py':
            module_name = f'app.application.services.{f[:-3]}'
            try:
                mod = __import__(module_name, fromlist=['*'])
                for name, obj in inspect.getmembers(mod, inspect.isclass):
                    if name.endswith('Service'):
                        for m_name, m_obj in inspect.getmembers(obj, inspect.isfunction):
                            methods[f'{name}.{m_name}'] = list(inspect.signature(m_obj).parameters.keys())
            except Exception as e:
                pass
    return methods

def find_api_calls():
    api_dir = 'app/api/v1'
    calls = []
    for f in os.listdir(api_dir):
        if f.endswith('.py') and f != '__init__.py':
            with open(os.path.join(api_dir, f), 'r', encoding='utf-8') as file:
                tree = ast.parse(file.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                        if isinstance(node.func.value, ast.Name) and node.func.value.id.endswith('_service'):
                            service_var = node.func.value.id
                            method_name = node.func.attr
                            kwargs = [kw.arg for kw in node.keywords if kw.arg]
                            calls.append({
                                'file': f,
                                'service_var': service_var,
                                'method': method_name,
                                'kwargs': kwargs
                            })
    return calls

methods = get_service_methods()
calls = find_api_calls()

mismatches = []
for c in calls:
    service_class_name = ''.join(word.capitalize() for word in c['service_var'].split('_'))
    key = f"{service_class_name}.{c['method']}"
    
    if key in methods:
        allowed_args = methods[key]
        for kw in c['kwargs']:
            if kw not in allowed_args:
                mismatches.append(f"- **{c['file']}**: Endpoint calls `{key}` with unexpected kwarg `{kw}`")
    else:
        mismatches.append(f"- **{c['file']}**: Endpoint calls unknown method `{key}`")

with open('service_signature_mismatches.md', 'w') as out:
    out.write('# Service Signature Mismatches\n\n')
    if mismatches:
        out.write('\n'.join(mismatches))
    else:
        out.write('No mismatches found!\n')
