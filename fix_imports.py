import os

backend_dir = '/home/team/shared/lexiflow-mvp/backend'
files_to_fix = [
    'integration_engine.py',
    'reception_engine.py',
    'utils.py',
    'reports.py',
    'seed_demo_data.py',
    'stripe_engine.py',
    'seed_analytics_data.py'
]

for filename in files_to_fix:
    filepath = os.path.join(backend_dir, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Replace 'import models' with robust import
        new_content = content.replace('import models', 'try: from . import models\nexcept (ImportError, ValueError): import models')
        # Also replace 'import database' etc if needed
        new_content = new_content.replace('import database', 'try: from . import database\nexcept (ImportError, ValueError): import database')
        new_content = new_content.replace('import ai_engine', 'try: from . import ai_engine\nexcept (ImportError, ValueError): import ai_engine')
        new_content = new_content.replace('import utils', 'try: from . import utils\nexcept (ImportError, ValueError): import utils')
        new_content = new_content.replace('import integration_engine', 'try: from . import integration_engine\nexcept (ImportError, ValueError): import integration_engine')

        if new_content != content:
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"Patched {filename}")
    else:
        print(f"Skipping {filename}, not found")
