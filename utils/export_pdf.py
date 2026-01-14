"""
PDF Export Module
Professional PDF report generation using ReportLab
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from typing import List, Dict, Any


def ExportToPDF(results: List[Dict[str, Any]], output_path: str) -> bool:
    """
    Export analysis results to a professional PDF report

    Args:
        results: List of password analysis result dictionaries
        output_path: Path to save PDF file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Container for PDF elements
        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12
        )

        # Title Page
        story.append(Paragraph("Password Security Analysis Report", title_style))
        story.append(Spacer(1, 0.3 * inch))

        # Summary statistics
        total_passwords = len(results)
        avg_score = sum(r['strength_score'] for r in results) / total_passwords if total_passwords > 0 else 0
        common_count = sum(1 for r in results if r.get('is_common', False))
        weak_count = sum(1 for r in results if r['strength_score'] < 40)

        # Check if HIBP data exists
        has_hibp = any('hibp_pwned' in r for r in results)
        breached_count = sum(1 for r in results if r.get('hibp_pwned', False)) if has_hibp else 0

        # Summary section
        story.append(Paragraph("Executive Summary", heading_style))

        summary_data = [
            ['Metric', 'Value'],
            ['Total Passwords Analyzed', str(total_passwords)],
            ['Average Strength Score', f"{avg_score:.1f}/100"],
            ['Common Passwords', f"{common_count} ({common_count/total_passwords*100:.1f}%)"],
            ['Weak Passwords (< 40)', f"{weak_count} ({weak_count/total_passwords*100:.1f}%)"]
        ]

        if has_hibp:
            summary_data.append(['Breached Passwords', f"{breached_count} ({breached_count/total_passwords*100:.1f}%)"])

        summary_data.append(['Report Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 0.4 * inch))

        # Detailed Results
        story.append(Paragraph("Detailed Analysis", heading_style))
        story.append(Spacer(1, 0.2 * inch))

        # Build detailed results table
        if has_hibp:
            table_data = [['#', 'Password', 'Length', 'Score', 'Category', 'Common', 'Breached', 'Patterns']]
        else:
            table_data = [['#', 'Password', 'Length', 'Score', 'Category', 'Common', 'Patterns']]

        for idx, result in enumerate(results, 1):
            # Mask password (show first 2 and last 2 chars)
            password = result['password']
            if len(password) > 4:
                masked = password[:2] + '*' * (len(password) - 4) + password[-2:]
            else:
                masked = '*' * len(password)

            # Format patterns
            patterns = result.get('patterns', {})
            pattern_list = []
            for pattern_type, items in patterns.items():
                if items:
                    pattern_list.append(f"{pattern_type}: {len(items)}")
            pattern_str = '\n'.join(pattern_list[:3])  # Limit to 3 types

            # Get strength color
            score = result['strength_score']
            if score >= 80:
                color_hex = '#20c997'  # Green
            elif score >= 60:
                color_hex = '#28a745'  # Green
            elif score >= 40:
                color_hex = '#ffc107'  # Yellow
            elif score >= 20:
                color_hex = '#fd7e14'  # Orange
            else:
                color_hex = '#dc3545'  # Red

            row = [
                str(idx),
                masked,
                str(result['length']),
                str(int(result['strength_score'])),
                result['strength_category'],
                'YES' if result.get('is_common') else 'NO',
            ]

            if has_hibp:
                breached = result.get('hibp_pwned', False)
                row.append('YES' if breached else 'NO')

            row.append(pattern_str or 'None')
            table_data.append(row)

        # Create table
        if has_hibp:
            col_widths = [0.4*inch, 1.2*inch, 0.6*inch, 0.6*inch, 1*inch, 0.7*inch, 0.8*inch, 1.5*inch]
        else:
            col_widths = [0.4*inch, 1.3*inch, 0.6*inch, 0.6*inch, 1.1*inch, 0.7*inch, 1.8*inch]

        results_table = Table(table_data, colWidths=col_widths)

        # Apply table style
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]

        # Add alternating row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightgrey))

        results_table.setStyle(TableStyle(table_style))
        story.append(results_table)

        # Footer
        story.append(Spacer(1, 0.5 * inch))
        footer_text = (
            "<para align=center>"
            "<font size=8 color='#95a5a6'>"
            "Generated by PassAudit - Password Security Analyzer | "
            "https://github.com/botchx86/PassAudit"
            "</font>"
            "</para>"
        )
        story.append(Paragraph(footer_text, styles['Normal']))

        # Build PDF
        doc.build(story)

        print(f"PDF report saved to: {output_path}")
        return True

    except Exception as e:
        print(f"Error creating PDF report: {e}")
        return False
