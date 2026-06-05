import os

NAV_BAR = """
<nav style="position: fixed; top: 0; width: 100%; height: 80px; background: rgba(255,255,255,0.98); border-bottom: 1px solid #e2e8f0; z-index: 1000; display: flex; align-items: center; font-family: 'Inter', sans-serif;">
  <div style="max-width: 1200px; margin: 0 auto; width: 100%; padding: 0 40px; display: flex; justify-content: space-between; align-items: center;">
    <a href="/index.html" style="font-family: 'Playfair Display', serif; font-weight: 700; font-size: 24px; color: #0f172a; text-decoration: none; display: flex; align-items: center; gap: 12px;">
      <span style="background: #0f172a; color: #c9a84c; padding: 4px 8px; border-radius: 4px; font-size: 18px;">LF</span> LexiFlow
    </a>
    <ul style="display: flex; gap: 32px; list-style: none; margin: 0; padding: 0;">
      <li><a href="/dashboard.html" style="text-decoration: none; color: #475569; font-weight: 500; font-size: 15px;">Attorney Portal</a></li>
      <li><a href="/pricing.html" style="text-decoration: none; color: #475569; font-weight: 500; font-size: 15px;">Capabilities</a></li>
      <li><a href="/blog.html" style="text-decoration: none; color: #475569; font-weight: 500; font-size: 15px;">Insights</a></li>
      <li><a href="/cities.html" style="text-decoration: none; color: #475569; font-weight: 500; font-size: 15px;">Areas We Serve</a></li>
    </ul>
    <a href="/pricing.html" style="background: #c9a84c; color: #0f172a; padding: 12px 24px; border-radius: 6px; font-weight: 600; text-decoration: none; font-size: 14px;">Request Access</a>
  </div>
</nav>
<div style="height: 80px;"></div>
"""

FOOTER = """
<footer style="background: #0f172a; color: #94a3b8; padding: 80px 0 40px; font-family: 'Inter', sans-serif;">
  <div style="max-width: 1200px; margin: 0 auto; padding: 0 40px; display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 80px;">
    <div>
      <a href="/index.html" style="font-family: 'Playfair Display', serif; font-weight: 700; font-size: 24px; color: #fff; text-decoration: none; margin-bottom: 20px; display: block;">LexiFlow</a>
      <p style="font-size: 14px; line-height: 1.6;">Enterprise Legal Intelligence. Empowering the next generation of top-tier law firms.</p>
    </div>
    <div>
      <h4 style="color: #fff; margin-bottom: 20px; font-size: 14px; text-transform: uppercase; letter-spacing: 0.1em;">Platform</h4>
      <ul style="list-style: none; padding: 0;">
        <li style="margin-bottom: 12px;"><a href="/pricing.html" style="color: #94a3b8; text-decoration: none; font-size: 14px;">Pricing</a></li>
        <li style="margin-bottom: 12px;"><a href="/dashboard.html" style="color: #94a3b8; text-decoration: none; font-size: 14px;">Attorney Portal</a></li>
        <li style="margin-bottom: 12px;"><a href="/blog.html" style="color: #94a3b8; text-decoration: none; font-size: 14px;">Legal Insights</a></li>
        <li style="margin-bottom: 12px;"><a href="/cities.html" style="color: #94a3b8; text-decoration: none; font-size: 14px;">Areas We Serve</a></li>
      </ul>
    </div>
    <div>
      <h4 style="color: #fff; margin-bottom: 20px; font-size: 14px; text-transform: uppercase; letter-spacing: 0.1em;">Support</h4>
      <ul style="list-style: none; padding: 0;">
        <li style="margin-bottom: 12px;"><a href="#" style="color: #94a3b8; text-decoration: none; font-size: 14px;">Privacy Policy</a></li>
        <li style="margin-bottom: 12px;"><a href="/terms.html" style="color: #94a3b8; text-decoration: none; font-size: 14px;">Terms of Service</a></li>
        <li style="margin-bottom: 12px;"><a href="mailto:leads@lexiflow.co" style="color: #94a3b8; text-decoration: none; font-size: 14px;">Contact Relations</a></li>
      </ul>
    </div>
  </div>
  <div style="max-width: 1200px; margin: 60px auto 0; padding: 40px 40px 0; border-top: 1px solid rgba(255,255,255,0.1); font-size: 13px; text-align: center;">
    &copy; 2026 LexiFlow Legal Suite. All Rights Reserved.
  </div>
</footer>
"""

blog_dir = "/home/agent-lead/lexiflow-repo/blog"
for filename in os.listdir(blog_dir):
    if filename.endswith(".html") and filename != "index.html":
        filepath = os.path.join(blog_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Replace external links
        content = content.replace("https://lexiflow.co/", "/")
        content = content.replace("https://lexiflow.co", "/")
        
        # Insert Nav Bar after <body>
        if "<body>" in content:
            content = content.replace("<body>", "<body>" + NAV_BAR)
        
        # Replace legacy footer
        if "<footer" in content:
            # Simple find and replace for the whole footer section if possible, 
            # or just append our hardened footer before </body> and remove the old one.
            start_footer = content.find("<footer")
            end_footer = content.find("</footer>") + len("</footer>")
            if start_footer != -1 and end_footer != -1:
                content = content[:start_footer] + FOOTER + content[end_footer:]
        
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated {filename}")
