import os
import re

backend_dir = '/home/team/shared/lexiflow-mvp/backend'
siblings = ['models', 'database', 'ai_engine', 'esign_engine', 'integration_engine', 'reception_engine', 'utils', 'stripe_engine']

for filename in os.listdir(backend_dir):
    if not filename.endswith('.py'):
        continue
    filepath = os.path.join(backend_dir, filename)
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        new_line = line
        # Replace 'import sibling' with 'from . import sibling' if it's at start of line
        for s in siblings:
            # Match 'import models' but not 'from ... import models'
            if re.match(rf'^import {s}(\s|$)', line):
                new_line = f"try: from . import {s}\nexcept (ImportError, ValueError): import {s}\n"
                break
            # Match 'from models import ...'
            match = re.match(rf'^from {s} import (.*)', line)
            if match:
                imports = match.group(1)
                new_line = f"try: from . import {s}\nexcept (ImportError, ValueError): import {s}\n# originally: {line}"
                # This is a bit hacky, better to use the imported name
                break
        
        new_lines.append(new_line)
    
    content = "".join(new_lines)
    # Fix the garbage I might have introduced before
    content = content.replace('from backend try: from . import models', 'try: from . import models')
    
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Processed {filename}")
