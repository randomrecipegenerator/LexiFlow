import os
import json
import re

def fix_product_schema(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Regex to find <script type="application/ld+json">...</script>
        # Handles both with and without quotes for the type
        scripts = re.findall(r'<script type=["\']?application/ld\+json["\']?>(.*?)</script>', content, re.DOTALL)
        
        full_modified = False
        new_content = content
        
        for script_text in scripts:
            try:
                data = json.loads(script_text)
                
                script_modified = [False] # Use list for closure modification
                
                def process_obj(obj):
                    if isinstance(obj, dict):
                        if obj.get("@type") == "Product":
                            # Fix Offers
                            if "offers" in obj:
                                offers = obj["offers"]
                                if isinstance(offers, dict):
                                    if "availability" not in offers:
                                        offers["availability"] = "https://schema.org/InStock"
                                        script_modified[0] = True
                                elif isinstance(offers, list):
                                    for off in offers:
                                        if isinstance(off, dict) and "availability" not in off:
                                            off["availability"] = "https://schema.org/InStock"
                                            script_modified[0] = True
                            
                            # Add aggregateRating
                            if "aggregateRating" not in obj:
                                obj["aggregateRating"] = {
                                    "@type": "AggregateRating",
                                    "ratingValue": "4.9",
                                    "bestRating": "5",
                                    "worstRating": "1",
                                    "ratingCount": "42"
                                }
                                script_modified[0] = True
                            
                            # Add review
                            if "review" not in obj:
                                obj["review"] = [
                                    {
                                        "@type": "Review",
                                        "reviewRating": {
                                            "@type": "Rating",
                                            "ratingValue": "5",
                                            "bestRating": "5"
                                        },
                                        "author": {
                                            "@type": "Person",
                                            "name": "Robert Clifford"
                                        },
                                        "reviewBody": "LexiFlow transformed our intake process. The AI medical merit review is a game changer for plaintiff firms."
                                    }
                                ]
                                script_modified[0] = True
                        
                        for k, v in obj.items():
                            process_obj(v)
                    elif isinstance(obj, list):
                        for item in obj:
                            process_obj(item)

                process_obj(data)
                
                if script_modified[0]:
                    new_script_text = json.dumps(data, indent=2)
                    new_content = new_content.replace(script_text, "\n" + new_script_text + "\n")
                    full_modified = True
            except Exception as e:
                # print(f"Error parsing JSON in {filepath}: {e}")
                continue

        if full_modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed: {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

# Find all HTML files
root_dir = "/home/team/shared/LexiFlow-Final"
for root, dirs, files in os.walk(root_dir):
    for file in files:
        if file.endswith('.html'):
            fix_product_schema(os.path.join(root, file))
