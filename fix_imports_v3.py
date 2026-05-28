import os

backend_dir = '/home/team/shared/lexiflow-mvp/backend'

def fix_file(filename, replacements):
    filepath = os.path.join(backend_dir, filename)
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r') as f:
        content = f.read()
    
    new_content = content
    for old, new in replacements:
        new_content = new_content.replace(old, new)
    
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Fixed {filename}")

# Standard clean import block
clean_imports = """try:
    from . import models, database, ai_engine, esign_engine, integration_engine, reception_engine, utils, stripe_engine
    from .database import engine, get_db, SessionLocal
except (ImportError, ValueError):
    import models, database, ai_engine, esign_engine, integration_engine, reception_engine, utils, stripe_engine
    from database import engine, get_db, SessionLocal"""

# For integration_engine.py specifically
integration_replacements = [
    ("""try:
    from . try: from . import models
except (ImportError, ValueError): import models
    from .database import SessionLocal
except ImportError:
    try: from . import models
except (ImportError, ValueError): import models
    from database import SessionLocal""", 
    """try:
    from . import models
    from .database import SessionLocal
except (ImportError, ValueError):
    import models
    from database import SessionLocal""")
]

# For reception_engine.py
reception_replacements = [
    ("""from backend try: from . import models
except (ImportError, ValueError): import models, ai_engine, integration_engine, utils""",
    """try:
    from . import models, ai_engine, integration_engine, utils
except (ImportError, ValueError):
    import models, ai_engine, integration_engine, utils""")
]

# For utils.py
utils_replacements = [
    ("""try: from . import models
except (ImportError, ValueError): import models""",
    """try:
    from . import models
except (ImportError, ValueError):
    import models"""),
    ("""try: from . import stripe_engine
except (ImportError, ValueError): import stripe_engine""",
    """try:
    from . import stripe_engine
except (ImportError, ValueError):
    import stripe_engine""")
]

fix_file('integration_engine.py', integration_replacements)
fix_file('reception_engine.py', reception_replacements)
fix_file('utils.py', utils_replacements)

# Add relative imports to other files if missing or clean them up
# ai_engine.py
fix_file('ai_engine.py', [
    ("import models", "try: from . import models\nexcept (ImportError, ValueError): import models")
])
# stripe_engine.py
fix_file('stripe_engine.py', [
    ("import models", "try: from . import models\nexcept (ImportError, ValueError): import models")
])
