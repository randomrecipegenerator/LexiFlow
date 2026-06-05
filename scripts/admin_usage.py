import requests
import json
import sys

def get_usage_report(api_url):
    try:
        response = requests.get(f"{api_url}/api/admin/usage-report")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def print_report(report):
    if not report:
        print("No report data available.")
        return

    print("=" * 100)
    print(f"{'FIRM NAME':<25} | {'PLAN':<10} | {'DOCS':<8} | {'VOICE':<8} | {'WEB':<6} | {'FORM':<6} | {'EMAIL':<6} | {'RECP':<6}")
    print("-" * 100)
    
    for firm in report:
        name = firm['firm_name']
        plan = firm['plan_status']
        totals = firm['totals']
        
        docs = totals.get('document_analysis', 0)
        voice = totals.get('voice_minutes', 0.0)
        email = totals.get('email_intake', 0)
        web = totals.get('web_intake', 0)
        form = totals.get('form_intake', 0)
        recp = totals.get('receptionist_intake', 0)
        
        print(f"{name:<25} | {plan:<10} | {docs:<8} | {voice:<8.1f} | {web:<6} | {form:<6} | {email:<6} | {recp:<6}")
    
    print("=" * 100)

if __name__ == "__main__":
    url = "http://localhost:8000"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    data = get_usage_report(url)
    print_report(data)
