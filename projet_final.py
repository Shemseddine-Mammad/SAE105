import pandas as pd
import re
from datetime import datetime
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import webbrowser
import os
from collections import Counter
"""code pour fichier .txt
site internet a terminer 
version a mettre pour le prof """
def analyze_tcpdump(file_path):
    """Analyse un fichier tcpdump et retourne les statistiques détaillées"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Extraction des protocoles et des IPs
        protocols = []
        ip_src = []
        ip_dst = []
        packets = []
        
        # Expression régulière pour extraire les IPs et protocoles
        ip_pattern = r'IP (?:([0-9]+(?:\.[0-9]+){3})\.([0-9]+))? ?([0-9]+(?:\.[0-9]+){3})?'
        packet_pattern = re.compile(r'(\d{2}:\d{2}:\d{2}\.\d{6})\s+IP\s+(.*?)\s+>\s+(.*?):\s+(.*)')
        
        for line in lines:
            # Extraction des informations détaillées des paquets
            match = packet_pattern.match(line)
            if match:
                timestamp, src, dst, info = match.groups()
                packets.append({
                    'timestamp': timestamp,
                    'source': src,
                    'destination': dst,
                    'info': info
                })
            
            if 'IP' in line:
                # Extraction du protocole
                if '>' in line:
                    parts = line.split('>')
                    if len(parts) > 1:
                        proto = parts[1].strip().split(':')[0].strip().split('.')[-1]
                        protocols.append(proto)
                
                # Extraction des IPs
                ip_match = re.search(ip_pattern, line)
                if ip_match:
                    if ip_match.group(1):
                        ip_src.append(ip_match.group(1))
                    if ip_match.group(3):
                        ip_dst.append(ip_match.group(3))

        protocol_counts = Counter(protocols)
        ip_counts = Counter(ip_src)
        
        # Statistiques de base
        stats = {
            'network_stats': {
                'packets_analyzed': len(packets),
                'packets_rate': f"{len(packets)/60:.1f}/s",
                'anomalies': {
                    'count': sum(1 for p in packets if 'Flags [S]' in p['info']),
                    'percentage': f"{sum(1 for p in packets if 'Flags [S]' in p['info'])/len(packets)*100:.1f}%"
                },
                'suspicious_ips': {
                    'count': len(set([p['source'] for p in packets if 'Flags [S]' in p['info']])),
                    'percentage': f"{len(set([p['source'] for p in packets if 'Flags [S]' in p['info']]))/len(set([p['source'] for p in packets]))*100:.1f}%"
                },
                'services': {
                    'count': len(set([p['destination'].split('.')[-1] for p in packets if '.' in p['destination']])),
                    'percentage': '-'
                }
            },
            'protocol_distribution': protocol_counts,
            'ip_distribution': dict(sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            'detected_anomalies': []
        }

        # Détection des anomalies
        threshold = len(packets) / len(set([p['source'] for p in packets])) * 2
        for src, count in ip_counts.items():
            if count > threshold:
                stats['detected_anomalies'].append({
                    'timestamp': packets[0]['timestamp'] if packets else '',
                    'ip_source': src,
                    'type': 'Traffic Burst',
                    'details': f'Pic de trafic: {count/60:.2f} paquets/s',
                    'level': 'HIGH'
                })

        return stats

    except Exception as e:
        print(f"Erreur lors de l'analyse du fichier: {str(e)}")
        return None

def generate_dual_pie_charts(protocol_counts, ip_counts):
    """Génère deux graphiques camembert côte à côte"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    
    colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC', 
             '#99FFCC', '#FFB366', '#FF99FF', '#99CCFF', '#FFB3B3']
    
    # Graphique des protocoles
    wedges1, texts1, autotexts1 = ax1.pie(protocol_counts.values(),
                                         labels=protocol_counts.keys(),
                                         autopct='%1.1f%%',
                                         colors=colors[:len(protocol_counts)])
    ax1.set_title('Répartition des Protocoles')
    
    # Graphique des IPs
    wedges2, texts2, autotexts2 = ax2.pie(ip_counts.values(),
                                         labels=ip_counts.keys(),
                                         autopct='%1.1f%%',
                                         colors=colors[:len(ip_counts)])
    ax2.set_title('Top 5 des IPs Sources')
    
    plt.setp(autotexts1 + autotexts2, size=8, weight="bold")
    plt.setp(texts1 + texts2, size=8)
    
    plt.tight_layout()
    
    return plot_to_base64()

def plot_to_base64():
    """Convertit le plot matplotlib actuel en image base64"""
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    return base64.b64encode(image_png).decode()

def generate_html_report(stats):
    """Génère le rapport HTML avec les graphiques et statistiques"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Rapport d'analyse du trafic réseau</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .stats-overview {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .stat-card .value {{
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .stat-card .subvalue {{
                color: #666;
                font-size: 14px;
            }}
            .charts-section {{
                margin: 20px 0;
                text-align: center;
            }}
            .anomalies-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            .anomalies-table th, .anomalies-table td {{
                padding: 12px;
                border: 1px solid #ddd;
                text-align: left;
            }}
            .anomalies-table th {{
                background-color: #f8f9fa;
            }}
            .level-high {{
                color: #dc3545;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Rapport d'analyse du trafic réseau</h1>
            
            <div class="stats-overview">
                <div class="stat-card">
                    <h3>Paquets analysés</h3>
                    <div class="value" style="color: #4285f4;">{stats['network_stats']['packets_analyzed']}</div>
                    <div class="subvalue">{stats['network_stats']['packets_rate']}</div>
                </div>
                
                <div class="stat-card">
                    <h3>Anomalies</h3>
                    <div class="value" style="color: #dc3545;">{stats['network_stats']['anomalies']['count']}</div>
                    <div class="subvalue">{stats['network_stats']['anomalies']['percentage']}</div>
                </div>
                
                <div class="stat-card">
                    <h3>IPs suspectes</h3>
                    <div class="value" style="color: #ff9800;">{stats['network_stats']['suspicious_ips']['count']}</div>
                    <div class="subvalue">{stats['network_stats']['suspicious_ips']['percentage']}</div>
                </div>
                
                <div class="stat-card">
                    <h3>Services</h3>
                    <div class="value" style="color: #4caf50;">{stats['network_stats']['services']['count']}</div>
                    <div class="subvalue">{stats['network_stats']['services']['percentage']}</div>
                </div>
            </div>

            <div class="charts-section">
                <img src="data:image/png;base64,{generate_dual_pie_charts(stats['protocol_distribution'], stats['ip_distribution'])}" 
                     alt="Distribution des protocoles et IPs">
            </div>
            
            <div class="stats-section">
                <h2>Anomalies détectées</h2>
                <table class="anomalies-table">
                    <tr>
                        <th>Timestamp</th>
                        <th>IP Source</th>
                        <th>Type</th>
                        <th>Détails</th>
                        <th>Niveau</th>
                    </tr>
    """
    
    for anomaly in stats['detected_anomalies']:
        html_content += f"""
                    <tr>
                        <td>{anomaly['timestamp']}</td>
                        <td>{anomaly['ip_source']}</td>
                        <td>{anomaly['type']}</td>
                        <td>{anomaly['details']}</td>
                        <td class="level-high">{anomaly['level']}</td>
                    </tr>
        """

    html_content += """
                </table>
            </div>
        </div>
    </body>
    </html>
    """

    with open('rapport_projet_final.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    webbrowser.open('file://' + os.path.realpath('rapport_projet_final.html'))

def main():
    file_path = 'fichier182.txt'
    stats = analyze_tcpdump(file_path)
    if stats:
        generate_html_report(stats)
    else:
        print("Erreur lors de l'analyse des données")

if __name__ == "__main__":
    main()