import ast
import os
import json
import sys

def parse_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            content = f.read()
            tree = ast.parse(content)
        except Exception as e:
            return {'error': str(e)}

    classes = []
    functions = []
    imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
            methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            classes.append({'name': node.name, 'bases': bases, 'methods': methods})
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Just capture all functions to be safe, including async ones
            functions.append({'name': node.name})
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    # Filter top-level functions vs methods
    class_methods = set()
    for c in classes:
        for m in c['methods']:
            class_methods.add(m)
            
    return {
        'classes': classes,
        'functions': [f for f in functions if f['name'] not in class_methods], # rough approx
        'imports': list(set(imports))
    }

def main():
    root_dir = r"c:\Users\zalau\OneDrive\Project\TTMS\backend\app"
    data = {}
    for root, dirs, files in os.walk(root_dir):
        if '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, root_dir)
                data[rel_path] = parse_file(path)
                
    with open('arch_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print("DONE")

if __name__ == '__main__':
    main()
