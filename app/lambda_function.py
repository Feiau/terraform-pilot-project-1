import json
import os
from datetime import datetime, timezone


def handler(event, context):
    env = os.environ.get("ENVIRONMENT", "unknown")
    region = os.environ.get("AWS_REGION", "unknown")
    request_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    source_ip = event.get("requestContext", {}).get("http", {}).get("sourceIp", "unknown")
    user_agent = event.get("requestContext", {}).get("http", {}).get("userAgent", "unknown")
    request_id = event.get("requestContext", {}).get("requestId", "unknown")

    env_colors = {
        "dev": ("#10b981", "#065f46", "#d1fae5"),
        "prod": ("#3b82f6", "#1e3a5f", "#dbeafe"),
    }
    accent, dark, light = env_colors.get(env, ("#8b5cf6", "#4c1d95", "#ede9fe"))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pilot Project - {env.upper()}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #e2e8f0;
        }}
        .container {{
            max-width: 600px;
            width: 90%;
            padding: 2.5rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
        }}
        .header {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            background: {accent};
            color: white;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 1rem;
        }}
        h1 {{
            font-size: 1.875rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            background: linear-gradient(to right, {accent}, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .subtitle {{
            color: #94a3b8;
            font-size: 0.95rem;
        }}
        .info-grid {{
            display: grid;
            gap: 0.75rem;
            margin-top: 1.5rem;
        }}
        .info-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 1rem;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 0.5rem;
            border: 1px solid rgba(255, 255, 255, 0.06);
        }}
        .info-label {{
            font-size: 0.8rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .info-value {{
            font-size: 0.9rem;
            color: #e2e8f0;
            font-family: 'SF Mono', 'Fira Code', monospace;
        }}
        .tech-stack {{
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            text-align: center;
        }}
        .tech-stack p {{
            font-size: 0.75rem;
            color: #64748b;
            margin-bottom: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        .tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            justify-content: center;
        }}
        .tag {{
            padding: 0.25rem 0.6rem;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 0.375rem;
            font-size: 0.75rem;
            color: #94a3b8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="badge">{env}</span>
            <h1>Terraform Pilot Project</h1>
            <p class="subtitle">Serverless application deployed via CI/CD pipeline</p>
        </div>
        <div class="info-grid">
            <div class="info-item">
                <span class="info-label">Environment</span>
                <span class="info-value">{env}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Region</span>
                <span class="info-value">{region}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Timestamp</span>
                <span class="info-value">{request_time}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Request ID</span>
                <span class="info-value">{request_id[:16]}...</span>
            </div>
            <div class="info-item">
                <span class="info-label">Source IP</span>
                <span class="info-value">{source_ip}</span>
            </div>
        </div>
        <div class="tech-stack">
            <p>Built with</p>
            <div class="tags">
                <span class="tag">Terraform</span>
                <span class="tag">AWS Lambda</span>
                <span class="tag">API Gateway</span>
                <span class="tag">GitHub Actions</span>
                <span class="tag">Python 3.12</span>
            </div>
        </div>
    </div>
</body>
</html>"""

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": html,
    }
