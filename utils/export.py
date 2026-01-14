import csv
import json
from datetime import datetime
from pathlib import Path

def get_entropy_category(entropy):
    """Categorize entropy level"""
    if entropy < 28:
        return 'Very Low'
    elif entropy < 36:
        return 'Low'
    elif entropy < 60:
        return 'Medium'
    elif entropy < 128:
        return 'High'
    else:
        return 'Very High'

def ExportToCSV(results, output_path):
    """Export analysis results to CSV file"""
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            # Define CSV headers
            fieldnames = [
                'Password',
                'Length',
                'Strength Score',
                'Strength Category',
                'Shannon Entropy',
                'Pool Entropy',
                'Entropy Category',
                'Is Common',
                'Sequences',
                'Keyboard Walks',
                'Repeated Chars',
                'Dates',
                'Common Words',
                'Leetspeak',
                'Context Patterns',
                'Feedback Count',
                'Timestamp'
            ]

            # Add HIBP fields if present
            if results and 'hibp_pwned' in results[0]:
                fieldnames.extend(['HIBP Pwned', 'HIBP Count'])

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Write data rows
            for result in results:
                row = {
                    'Password': result['password'],
                    'Length': result['length'],
                    'Strength Score': result['strength_score'],
                    'Strength Category': result['strength_category'],
                    'Shannon Entropy': result['entropy'],
                    'Pool Entropy': result['pool_entropy'],
                    'Entropy Category': get_entropy_category(result['entropy']),
                    'Is Common': 'YES' if result['is_common'] else 'NO',
                    'Sequences': ', '.join(result['patterns'].get('sequences', [])) if result['patterns'].get('sequences') else '',
                    'Keyboard Walks': ', '.join(result['patterns'].get('keyboard_walks', [])) if result['patterns'].get('keyboard_walks') else '',
                    'Repeated Chars': ', '.join(result['patterns'].get('repeated_chars', [])) if result['patterns'].get('repeated_chars') else '',
                    'Dates': ', '.join(result['patterns'].get('dates', [])) if result['patterns'].get('dates') else '',
                    'Common Words': ', '.join(result['patterns'].get('common_words', [])) if result['patterns'].get('common_words') else '',
                    'Leetspeak': ', '.join(result['patterns'].get('leetspeak', [])) if result['patterns'].get('leetspeak') else '',
                    'Context Patterns': ', '.join(result['patterns'].get('context_patterns', [])) if result['patterns'].get('context_patterns') else '',
                    'Feedback Count': len(result['feedback']),
                    'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                # Add HIBP data if present
                if 'hibp_pwned' in result:
                    row['HIBP Pwned'] = 'YES' if result['hibp_pwned'] else 'NO'
                    row['HIBP Count'] = result['hibp_count'] if result['hibp_count'] >= 0 else 'N/A'

                writer.writerow(row)

        print(f"\n[SUCCESS] CSV report exported to: {output_path}")
        return True

    except Exception as e:
        print(f"\n[ERROR] Error exporting CSV: {e}")
        return False

def ExportToHTML(results, output_path):
    """Export analysis results to HTML file"""
    try:
        # Calculate summary statistics
        total = len(results)
        avg_score = sum(r['strength_score'] for r in results) / total if total > 0 else 0
        common_count = sum(1 for r in results if r['is_common'])
        weak_count = sum(1 for r in results if r['strength_score'] < 40)

        # Check if HIBP data is present
        has_hibp = results and 'hibp_pwned' in results[0]
        hibp_pwned_count = sum(1 for r in results if r.get('hibp_pwned', False)) if has_hibp else 0

        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PassAudit - Password Analysis Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2em;
        }}
        .header p {{
            margin: 0;
            opacity: 0.9;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
        }}
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        table {{
            width: 100%;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-collapse: collapse;
        }}
        th {{
            background-color: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .strength-very-weak {{ color: #dc3545; font-weight: bold; }}
        .strength-weak {{ color: #fd7e14; font-weight: bold; }}
        .strength-medium {{ color: #ffc107; font-weight: bold; }}
        .strength-strong {{ color: #28a745; font-weight: bold; }}
        .strength-very-strong {{ color: #20c997; font-weight: bold; }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .badge-yes {{
            background-color: #dc3545;
            color: white;
        }}
        .badge-no {{
            background-color: #28a745;
            color: white;
        }}
        .password-masked {{
            font-family: 'Courier New', monospace;
            background-color: #f8f9fa;
            padding: 4px 8px;
            border-radius: 4px;
        }}
        .footer {{
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        .patterns {{
            font-size: 0.85em;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 Password Risk Analysis Report</h1>
        <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>

    <div class="summary">
        <div class="summary-card">
            <h3>Total Passwords</h3>
            <div class="value">{total}</div>
        </div>
        <div class="summary-card">
            <h3>Average Score</h3>
            <div class="value">{avg_score:.1f}/100</div>
        </div>
        <div class="summary-card">
            <h3>Common Passwords</h3>
            <div class="value" style="color: #dc3545;">{common_count}</div>
        </div>
        <div class="summary-card">
            <h3>Weak Passwords</h3>
            <div class="value" style="color: #fd7e14;">{weak_count}</div>
        </div>
"""

        if has_hibp:
            html += f"""        <div class="summary-card">
            <h3>Breached (HIBP)</h3>
            <div class="value" style="color: #dc3545;">{hibp_pwned_count}</div>
        </div>
"""

        html += """    </div>

    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Password</th>
                <th>Length</th>
                <th>Score</th>
                <th>Category</th>
                <th>Entropy</th>
                <th>Common</th>
"""

        if has_hibp:
            html += """                <th>Breached</th>
"""

        html += """                <th>Patterns Detected</th>
            </tr>
        </thead>
        <tbody>
"""

        # Generate table rows
        for i, result in enumerate(results, 1):
            # Determine strength class
            score = result['strength_score']
            if score >= 80:
                strength_class = 'strength-very-strong'
            elif score >= 60:
                strength_class = 'strength-strong'
            elif score >= 40:
                strength_class = 'strength-medium'
            elif score >= 20:
                strength_class = 'strength-weak'
            else:
                strength_class = 'strength-very-weak'

            # Mask password
            pwd = result['password']
            if len(pwd) <= 6:
                masked = pwd[:2] + "*" * (len(pwd) - 2) if len(pwd) > 2 else "*" * len(pwd)
            else:
                masked = pwd[:2] + "*" * (len(pwd) - 4) + pwd[-2:]

            # Collect patterns
            patterns = []
            for pattern_type, items in result['patterns'].items():
                if items:
                    patterns.append(f"{pattern_type.replace('_', ' ').title()}: {', '.join(str(x) for x in items[:3])}")

            patterns_html = '<br>'.join(patterns) if patterns else '<em>None</em>'

            html += f"""            <tr>
                <td>{i}</td>
                <td><span class="password-masked">{masked}</span></td>
                <td>{result['length']}</td>
                <td class="{strength_class}">{result['strength_score']:.1f}</td>
                <td class="{strength_class}">{result['strength_category']}</td>
                <td>{result['entropy']:.1f} bits</td>
                <td><span class="badge {'badge-yes' if result['is_common'] else 'badge-no'}">{'YES' if result['is_common'] else 'NO'}</span></td>
"""

            if has_hibp:
                hibp_class = 'badge-yes' if result.get('hibp_pwned', False) else 'badge-no'
                hibp_text = 'YES' if result.get('hibp_pwned', False) else 'NO'
                html += f"""                <td><span class="badge {hibp_class}">{hibp_text}</span></td>
"""

            html += f"""                <td class="patterns">{patterns_html}</td>
            </tr>
"""

        html += """        </tbody>
    </table>

    <div class="footer">
        <p>Generated by <strong>PassAudit</strong></p>
        <p>⚠️ This report contains sensitive information. Store securely.</p>
    </div>
</body>
</html>"""

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"\n[SUCCESS] HTML report exported to: {output_path}")
        return True

    except Exception as e:
        print(f"\n[ERROR] Error exporting HTML: {e}")
        return False
