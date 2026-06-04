import os

def fix_links_in_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Replace broken Start Free Trial links
            new_content = content.replace('href="/pricing.html" class="btn-plan', 'href="/signup.html" class="btn-plan')
            new_content = new_content.replace('href="/pricing.html" class="btn-cta">Get Started</a>', 'href="/signup.html" class="btn-cta">Get Started</a>')
            
            # Also handle the specific case in pricing.html where it's href="/pricing.html" but should be /signup.html
            if filename == "pricing.html":
                new_content = new_content.replace('href="/pricing.html" class="btn-plan', 'href="/signup.html" class="btn-plan')
            
            # General cleanup for any button-like link that points to its own page or pricing erroneously
            if new_content != content:
                with open(filepath, 'w') as f:
                    f.write(new_content)
                print(f"Fixed links in {filename}")

if __name__ == "__main__":
    base_dir = "/home/team/shared/LexiFlow-Final"
    fix_links_in_directory(base_dir)
