import os

base_path = "/home/team/shared/LexiFlow-Final"
old_email = "lexiflow-legal-suite-88a6f8e9@ctomail.io"
new_email = "lexiflow-legal-suite-88a6f8e9@ctomail.io"

def fix_emails(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith((".html", ".js", ".py", ".md")):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if old_email in content:
                        new_content = content.replace(old_email, new_email)
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Fixed email in: {filepath}")
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    fix_emails(base_path)
    # Also fix in the repo if it's separate
    # fix_emails("/home/agent-lead/lexiflow-repo")
