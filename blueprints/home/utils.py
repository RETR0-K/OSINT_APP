# blueprints/home/utils.py
import json
import csv
import io
from datetime import datetime
from flask import make_response
from models import Scan

def export_scan_to_json(scan):
    """Export a scan to JSON format"""
    if not scan:
        return None
    
    # Parse the stored JSON results
    try:
        scan_data = json.loads(scan.results_json)
    except:
        scan_data = {}
    
    # Add metadata
    export_data = {
        'scan_id': scan.id,
        'scan_type': scan.scan_type,
        'target': scan.target,
        'scan_date': scan.scan_date.isoformat(),
        'status': scan.status,
        'findings': scan.findings,
        'risk_score': scan.risk_score,
        'results': scan_data
    }
    
    # Create response with JSON data
    response = make_response(json.dumps(export_data, indent=4))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = f'attachment; filename=scan_{scan.id}_{scan.scan_type}_{datetime.now().strftime("%Y%m%d")}.json'
    
    return response

def export_scan_to_csv(scan):
    """Export a scan to CSV format"""
    if not scan:
        return None
    
    # Create CSV file in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Scan ID', 'Type', 'Target', 'Date', 'Status', 'Findings', 'Risk Score'])
    
    # Write scan metadata
    writer.writerow([
        scan.id,
        scan.scan_type,
        scan.target,
        scan.scan_date.strftime('%Y-%m-%d %H:%M:%S'),
        scan.status,
        scan.findings,
        scan.risk_score
    ])
    
    # Add blank row
    writer.writerow([])
    
    # Try to add scan-specific data
    try:
        scan_data = json.loads(scan.results_json)
        
        if scan.scan_type == 'username':
            # For username scans, add found accounts
            writer.writerow(['Platform', 'Category', 'URL', 'Source'])
            
            for account in scan_data.get('combined_results', []):
                writer.writerow([
                    account.get('site_name', ''),
                    account.get('category', ''),
                    account.get('url', ''),
                    account.get('source', '')
                ])
                
        elif scan.scan_type == 'email':
            # For email breach scans, add breach data
            writer.writerow(['Source', 'Breach Count'])
            
            for source in scan_data.get('sources', []):
                writer.writerow([
                    source.get('name', ''),
                    len(source.get('breaches', []))
                ])
                
        elif scan.scan_type == 'ai_analysis':
            # For AI analysis, add insights
            writer.writerow(['Insight', 'Confidence', 'Category'])
            
            for insight in scan_data.get('insights', []):
                writer.writerow([
                    insight.get('title', ''),
                    insight.get('confidence', ''),
                    insight.get('category', '')
                ])
    except:
        # If we can't parse the JSON, just skip the additional data
        pass
    
    # Create response with CSV data
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=scan_{scan.id}_{scan.scan_type}_{datetime.now().strftime("%Y%m%d")}.csv'
    
    return response

def export_scans_to_csv(scans):
    """Export multiple scans to a single CSV file"""
    if not scans:
        return None
    
    # Create CSV file in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Scan ID', 'Type', 'Target', 'Date', 'Status', 'Findings', 'Risk Score'])
    
    # Write each scan
    for scan in scans:
        writer.writerow([
            scan.id,
            scan.scan_type,
            scan.target,
            scan.scan_date.strftime('%Y-%m-%d %H:%M:%S'),
            scan.status,
            scan.findings,
            scan.risk_score
        ])
    
    # Create response with CSV data
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=all_scans_{datetime.now().strftime("%Y%m%d")}.csv'
    
    return response