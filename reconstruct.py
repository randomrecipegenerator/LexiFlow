import os

def replace_header(filename, header_file, skip_lines):
    filepath = os.path.join('/home/team/shared/lexiflow-mvp/backend', filename)
    header_path = os.path.join('/home/team/shared/lexiflow-mvp/backend', header_file)
    
    with open(header_path, 'r') as f:
        header = f.read()
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    rest = "".join(lines[skip_lines:])
    
    with open(filepath, 'w') as f:
        f.write(header + rest)
    print(f"Reconstructed {filename}")

replace_header('reception_engine.py', 'reception_engine_header.py', 13)
replace_header('stripe_engine.py', 'simple_header.py', 15)
replace_header('reports.py', 'simple_header.py', 10)
replace_header('esign_engine.py', 'simple_header.py', 10)
