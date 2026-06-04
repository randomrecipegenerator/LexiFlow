import os

def check_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for correct Nav
    has_nav = '<nav><div class="nav-container">' in content
    # Check for correct Footer
    has_footer = '<footer>' in content
    # Check for signup link
    has_signup = '/signup.html' in content
    
    return has_nav and has_footer and has_signup

def audit(directory):
    total = 0
    passed = 0
    failed_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                if file in ['dashboard.html', 'app.html', 'meritscan-app.html', 'depolens-app.html', 'form_view.html']:
                    continue
                total += 1
                filepath = os.path.join(root, file)
                if check_file(filepath):
                    passed += 1
                else:
                    failed_files.append(filepath)
    
    print(f"Total files audited: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    if failed_files:
        print("\nFirst 5 failed files:")
        for f in failed_files[:5]:
            print(f)

if __name__ == "__main__":
    audit("/home/team/shared/LexiFlow-Final")
