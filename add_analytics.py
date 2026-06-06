import os
import re

files_to_update = [
    "ai-intake-agent.html",
    "ai-medical-chronologies.html",
    "depolens-app.html",
    "medical-chronologies-app.html"
]

base_path = "/home/team/shared/LexiFlow-Final"

analytics_html = """
    <!-- Performance Analytics -->
    <section class="section" id="analytics" style="background: #f8fafc; padding: 80px 0; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; margin: 40px 0;">
        <div style="max-width: 1200px; margin: 0 auto; padding: 0 40px;">
            <div style="text-align: center; margin-bottom: 48px;">
                <span style="display: inline-block; padding: 4px 12px; background: rgba(201, 168, 76, 0.1); color: #c9a84c; border-radius: 100px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 12px;">Live Analytics</span>
                <h2 style="font-family: 'Playfair Display', serif; font-size: 32px; color: #0f172a; margin-bottom: 8px;">Lead Conversion Trend & Volume</h2>
                <p style="color: #475569; max-width: 600px; margin: 0 auto;">Real-time performance monitoring across all automated intake channels.</p>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px;">
                <div style="background: white; padding: 32px; border-radius: 24px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                    <h4 style="font-family: 'Playfair Display', serif; font-size: 18px; color: #0f172a; margin-bottom: 24px;">📈 Lead Conversion Trend</h4>
                    <div style="height: 250px;"><canvas id="chart-conversion"></canvas></div>
                </div>
                <div style="background: white; padding: 32px; border-radius: 24px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                    <h4 style="font-family: 'Playfair Display', serif; font-size: 18px; color: #0f172a; margin-bottom: 24px;">📊 Volume by Channel</h4>
                    <div style="height: 250px;"><canvas id="chart-channel"></canvas></div>
                </div>
            </div>
        </div>
    </section>
"""

analytics_js = """
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
    <script>
        (function() {
            const NAVY = '#0f172a';
            const GOLD = '#c9a84c';
            
            // Check if canvas exists before initializing
            const ctx1 = document.getElementById('chart-conversion');
            if (ctx1) {
                new Chart(ctx1, {
                    type: 'line',
                    data: {
                        labels: ['Jan','Feb','Mar','Apr','May','Jun'],
                        datasets: [{
                            label: 'Conversion Rate %',
                            data: [2.1, 2.4, 2.8, 3.2, 3.5, 3.8],
                            borderColor: GOLD,
                            backgroundColor: GOLD + '20',
                            fill: true,
                            tension: 0.4,
                            pointBackgroundColor: GOLD
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
                            x: { grid: { display: false } }
                        }
                    }
                });
            }

            const ctx2 = document.getElementById('chart-channel');
            if (ctx2) {
                new Chart(ctx2, {
                    type: 'doughnut',
                    data: {
                        labels: ['Web Widget', 'Voice AI', 'Email', 'Other'],
                        datasets: [{
                            data: [48, 32, 14, 6],
                            backgroundColor: [NAVY, GOLD, '#16a34a', '#94a3b8'],
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '70%',
                        plugins: {
                            legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 11 } } }
                        }
                    }
                });
            }
        })();
    </script>
"""

for filename in files_to_update:
    filepath = os.path.join(base_path, filename)
    if not os.path.exists(filepath):
        print(f"Skipping {filename} (not found)")
        continue
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    if 'id="analytics"' in content:
        print(f"Analytics already present in {filename}")
        continue
    
    # Inject HTML before ethics-resources or footer
    if '<section id="ethics-resources"' in content:
        new_content = content.replace('<section id="ethics-resources"', analytics_html + '\n<section id="ethics-resources"')
    elif '<footer' in content:
        new_content = content.replace('<footer', analytics_html + '\n<footer')
    else:
        new_content = content.replace('</body>', analytics_html + '\n</body>')
    
    # Inject JS before </body>
    new_content = new_content.replace('</body>', analytics_js + '\n</body>')
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    print(f"Updated {filename}")
