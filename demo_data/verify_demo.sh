#!/bin/bash
# Verify Demo API Endpoints
echo "Checking LexiFlow API Status..."
curl -s http://localhost:3000/api/health | grep -q "healthy" && echo "✅ Backend Health: OK" || echo "❌ Backend Health: FAIL"

echo "Checking NY Damage Caps (Jurisdictional Intelligence)..."
curl -s http://localhost:3000/api/enterprise/settlement/caps/NY | grep -q "None" && echo "✅ NY Settlement Logic: OK" || echo "❌ NY Settlement Logic: FAIL"

echo "Checking Enterprise Dashboard..."
# Note: Requires JWT for real test, but we check if endpoint exists
curl -s -o /dev/null -I -w "%{http_code}" http://localhost:3000/api/enterprise/dashboard | grep -q "401" && echo "✅ Enterprise Endpoints: OK (Access Restricted as expected)" || echo "❌ Enterprise Endpoints: FAIL"

echo "Demo Readiness Check Complete."
