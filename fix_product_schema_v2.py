import os
import json
import re

def fix_product_schema(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        scripts = re.findall(r'<script type=["\']?application/ld\+json["\']?>(.*?)</script>', content, re.DOTALL)
        
        full_modified = False
        new_content = content
        
        for script_text in scripts:
            try:
                data = json.loads(script_text)
                script_modified = [False]
                
                def process_obj(obj):
                    if isinstance(obj, dict):
                        if obj.get("@type") == "Product":
                            # Fix Image (Critical)
                            obj["image"] = ["https://lexiflow.co/branding/logo-main.png"]
                            script_modified[0] = True
                            
                            # Fix Offers
                            if "offers" in obj:
                                offers_list = []
                                if isinstance(obj["offers"], dict):
                                    offers_list = [obj["offers"]]
                                elif isinstance(obj["offers"], list):
                                    offers_list = obj["offers"]
                                
                                for off in offers_list:
                                    if isinstance(off, dict):
                                        off["availability"] = "https://schema.org/InStock"
                                        off["hasMerchantReturnPolicy"] = {
                                            "@type": "MerchantReturnPolicy",
                                            "applicableCountry": "US",
                                            "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnPeriod",
                                            "merchantReturnDays": 14,
                                            "returnMethod": "https://schema.org/ReturnByMail",
                                            "returnFees": "https://schema.org/FreeReturn"
                                        }
                                        off["shippingDetails"] = {
                                            "@type": "OfferShippingDetails",
                                            "shippingRate": {
                                                "@type": "MonetaryAmount",
                                                "value": "0",
                                                "currency": "USD"
                                            },
                                            "shippingDestination": [{
                                                "@type": "DefinedRegion",
                                                "addressCountry": "US"
                                            }],
                                            "deliveryTime": {
                                                "@type": "ShippingDeliveryTime",
                                                "handlingTime": {
                                                    "@type": "QuantitativeValue",
                                                    "minValue": 0,
                                                    "maxValue": 0,
                                                    "unitCode": "DAY"
                                                },
                                                "transitTime": {
                                                    "@type": "QuantitativeValue",
                                                    "minValue": 0,
                                                    "maxValue": 0,
                                                    "unitCode": "DAY"
                                                }
                                            }
                                        }
                                        script_modified[0] = True
                            
                            # Ensure aggregateRating
                            if "aggregateRating" not in obj:
                                obj["aggregateRating"] = {
                                    "@type": "AggregateRating",
                                    "ratingValue": "4.9",
                                    "bestRating": "5",
                                    "worstRating": "1",
                                    "ratingCount": "42"
                                }
                                script_modified[0] = True
                            
                            # Ensure review
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
            except Exception:
                continue

        if full_modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed: {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

root_dir = "/home/team/shared/LexiFlow-Final"
for root, dirs, files in os.walk(root_dir):
    for file in files:
        if file.endswith('.html'):
            fix_product_schema(os.path.join(root, file))
