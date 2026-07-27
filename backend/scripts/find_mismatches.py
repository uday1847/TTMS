import os
import re
import json
import httpx
import asyncio

FRONTEND_FEATURES_DIR = "../../frontend/src/features"

async def fetch_openapi():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:8000/openapi.json")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        print(f"Failed to fetch openapi.json: {e}")
        return None

def extract_ts_interfaces(directory):
    interfaces = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".types.ts") or file.endswith(".schema.ts") or file.endswith(".ts"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # A naive regex to grab interfaces and their properties
                    matches = re.finditer(r'export\s+interface\s+(\w+)\s*{([^}]+)}', content)
                    for match in matches:
                        name = match.group(1)
                        body = match.group(2)
                        
                        props = {}
                        prop_matches = re.finditer(r'(\w+)(\??)\s*:\s*([^;]+);', body)
                        for pm in prop_matches:
                            p_name = pm.group(1)
                            p_opt = bool(pm.group(2))
                            p_type = pm.group(3).strip()
                            props[p_name] = {"optional": p_opt, "type": p_type}
                            
                        interfaces[name] = props
    return interfaces

def check_mismatches(openapi, ts_interfaces):
    mismatches = []
    schemas = openapi.get("components", {}).get("schemas", {})
    
    # Map Backend Schemas to Frontend DTOs based on naming conventions
    # e.g., TripResponse -> TripResponseDto, UserCreate -> UserCreateDto, etc.
    for backend_name, schema in schemas.items():
        if backend_name.endswith("Exception") or backend_name == "APIResponse":
            continue
            
        # Very simple heuristic for finding matching TS interface
        frontend_candidates = [backend_name, backend_name + "Dto", backend_name + "Response", backend_name.replace("Response", "ResponseDto")]
        matched_ts = None
        matched_name = None
        for candidate in frontend_candidates:
            if candidate in ts_interfaces:
                matched_ts = ts_interfaces[candidate]
                matched_name = candidate
                break
                
        if not matched_ts:
            # We don't report missing matching names as it's too noisy, only if fields mismatch
            continue
            
        backend_props = schema.get("properties", {})
        backend_required = schema.get("required", [])
        
        for prop_name, prop_details in backend_props.items():
            if prop_name not in matched_ts:
                mismatches.append(f"[FAIL] [Missing Field] Backend {backend_name}.{prop_name} not found in Frontend {matched_name}")
            else:
                ts_prop = matched_ts[prop_name]
                is_req_backend = prop_name in backend_required
                is_req_frontend = not ts_prop["optional"]
                
                # Check snake_case vs camelCase mismatch typically
                if "_" in prop_name and not prop_name.islower():
                    mismatches.append(f"[WARN] [Naming] {backend_name}.{prop_name} has mixed case (ensure snake_case/camelCase alignment)")
                    
                if is_req_backend != is_req_frontend:
                    mismatches.append(f"[WARN] [Optionality] {backend_name}.{prop_name} required={is_req_backend} but Frontend optional={ts_prop['optional']}")

    return mismatches

async def main():
    print("Fetching OpenAPI Spec from backend...")
    openapi = await fetch_openapi()
    if not openapi:
        return
        
    print("Extracting TypeScript interfaces from frontend...")
    # Use absolute path to avoid cwd issues
    current_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.abspath(os.path.join(current_dir, "../../frontend/src/features"))
    ts_interfaces = extract_ts_interfaces(frontend_dir)
    
    print("Checking for mismatches...")
    mismatches = check_mismatches(openapi, ts_interfaces)
    
    if mismatches:
        print("\n--- API Contract Mismatches Found ---")
        for m in mismatches:
            print(m)
        print("-------------------------------------")
    else:
        print("\n[OK] No significant API contract mismatches found!")

if __name__ == "__main__":
    asyncio.run(main())
