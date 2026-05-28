import os

filepath = '/home/team/shared/lexiflow-mvp/backend/main.py'
with open(filepath, 'r') as f:
    content = f.read()

# Fix demo_request call
old_code = 'demo_req = models.DemoRequest(name=name, email=email, firm=firm)'
new_code = 'demo_req = models.DemoRequest(full_name=name, email=email, firm_name=firm)'

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(filepath, 'w') as f:
        f.write(content)
    print("Successfully patched main.py")
else:
    print("Could not find the code to patch. Checking for variations...")
    # Maybe it was already changed or different?
    if 'full_name=name' in content:
        print("Already patched or uses full_name.")
    else:
        print("Content snippet around demo_request:")
        idx = content.find('/demo-request')
        if idx != -1:
            print(content[idx:idx+200])
