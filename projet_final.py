import pandas as pd
import re
from datetime import datetime
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import webbrowser
import os
from collections import Counter
import csv

def detect_anomalies(packet_info):
    """Détecte les anomalies dans les paquets"""
    suspicious_flags = ['[S]', '[S.]', '[SF]', '[P.]']
    return any(flag in packet_info for flag in suspicious_flags)

def analyze_tcpdump(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        protocols = []
        ip_src = []
        ip_dst = []
        packets = []
        anomalies = []
        
        ip_pattern = r'IP (?:([0-9]+(?:\.[0-9]+){3})\.([0-9]+))? ?([0-9]+(?:\.[0-9]+){3})?'
        packet_pattern = re.compile(r'(\d{2}:\d{2}:\d{2}\.\d{6})\s+(.*?)(?: > |, )(.*?)(?:,|\:) (.*)')
        
        for line in lines:
            if not line.startswith('\t'):
                match = packet_pattern.match(line)
                if match:
                    timestamp, src, dst, info = match.groups()
                    packet = {
                        'timestamp': timestamp,
                        'source': src,
                        'destination': dst,
                        'info': info
                    }
                    packets.append(packet)
                    
                    if detect_anomalies(info):
                        anomalies.append(packet)
                
                if 'IP' in line or 'ARP' in line or 'STP' in line:
                    if '>' in line:
                        proto = line.split('>')[1].strip().split(':')[0].strip().split('.')[-1]
                    else:
                        proto = line.split(',')[0].split()[1].rstrip(',')
                    protocols.append(proto)
                
                ip_match = re.search(ip_pattern, line)
                if ip_match:
                    if ip_match.group(1):
                        ip_src.append(ip_match.group(1))
                    if ip_match.group(3):
                        ip_dst.append(ip_match.group(3))

        protocol_counts = Counter(protocols)
        ip_counts = Counter(ip_src)
        
        # Calcul du seuil pour les pics de trafic
        seuil = len(packets) / len(set([p['source'] for p in packets])) * 2
        anomalies_trafic = []
        ips_suspectes = set()
        
        for src, count in ip_counts.items():
            if count > seuil:
                anomalies_trafic.append({
                    'timestamp': packets[0]['timestamp'] if packets else '',
                    'ip_source': src,
                    'type': 'Pic de Trafic',
                    'details': f'Pic de trafic: {count/60:.2f} paquets/s',
                    'level': 'ÉLEVÉ'
                })
                ips_suspectes.add(src)

        # Mise à jour des statistiques avec les compteurs d'anomalies
        total_anomalies = len(anomalies_trafic)
        stats = {
            'network_stats': {
                'packets_analyzed': len(packets),
                'packets_rate': f"{len(packets)/60:.1f}/s",
                'anomalies': {
                    'count': total_anomalies,
                    'percentage': f"{(total_anomalies/len(packets)*100) if packets else 0:.1f}%"
                },
                'suspicious_ips': {
                    'count': len(ips_suspectes),
                    'percentage': f"{(len(ips_suspectes)/len(set(ip_src))*100) if ip_src else 0:.1f}%"
                },
                'services': {
                    'count': len(set([p['destination'].split('.')[-1] for p in packets if '.' in p['destination']])),
                    'percentage': '-'
                }
            },
            'protocol_distribution': protocol_counts,
            'detected_anomalies': anomalies_trafic
        }

        return stats

    except Exception as e:
        print(f"Erreur lors de l'analyse du fichier: {str(e)}")
        return None


def generate_protocol_chart(protocol_counts):
    """Génère un graphique camembert des 10 protocoles les plus utilisés"""
    plt.figure(figsize=(10, 7))
    
    colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC', 
             '#99FFCC', '#FFB366', '#FF99FF', '#99CCFF', '#FFB3B3']
    
    # Prendre les 10 protocoles les plus fréquents
    top_10_protocols = dict(sorted(protocol_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    
    plt.pie(top_10_protocols.values(),
            labels=top_10_protocols.keys(),
            autopct='%1.1f%%',
            colors=colors[:len(top_10_protocols)])
    plt.title('Top 10 des Protocoles les Plus Utilisés')
    
    plt.tight_layout()
    
    return plot_to_base64()

def plot_to_base64():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    return base64.b64encode(image_png).decode()

def generate_csv_report(stats, output_file='rapport_analyse.csv'):
    """
    Génère un rapport CSV à partir des statistiques d'analyse réseau
    """
    csv_content = [
        ['Type d\'analyse', 'Valeur', 'Détails'],
        ['Paquets analysés', 
         stats['network_stats']['packets_analyzed'],
         stats['network_stats']['packets_rate']],
        ['Anomalies',
         stats['network_stats']['anomalies']['count'],
         stats['network_stats']['anomalies']['percentage']],
        ['IPs suspectes',
         stats['network_stats']['suspicious_ips']['count'],
         stats['network_stats']['suspicious_ips']['percentage']],
        ['Services',
         stats['network_stats']['services']['count'],
         stats['network_stats']['services']['percentage']]
    ]

    # Ajouter la distribution des protocoles
    for protocol, percentage in stats['protocol_distribution'].items():
        csv_content.append([
            'Distribution protocoles',
            protocol,
            f"{(percentage/stats['network_stats']['packets_analyzed'])*100:.1f}%"
        ])

    # Ajouter les anomalies détectées
    for i, anomaly in enumerate(stats['detected_anomalies'], 1):
        csv_content.append([
            f'Anomalie {i}',
            anomaly['ip_source'],
            anomaly['details']
        ])
    # Écriture dans le fichier CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(csv_content)
    
    return output_file

# Usage dans le main:
# stats = analyze_tcpdump(file_path)
# if stats:
#     csv_file = generate_csv_report(stats)
#     print(f"Rapport CSV généré: {csv_file}")

def generate_html_report(stats):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Rapport d'analyse du trafic réseau</title>
        <style>
            :root {{
                --primary-color: #4285f4;
                --warning-color: #ff9800;
                --danger-color: #dc3545;
                --success-color: #4caf50;
                --background-color: #f8f9fa;
                --border-radius: 10px;
                --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
                min-height: 100vh;
                padding: 2rem;
            }}

            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background-color: white;
                border-radius: var(--border-radius);
                box-shadow: var(--box-shadow);
                padding: 2rem;
            }}

            h1, h2, h3 {{
                color: #2c3e50;
                margin-bottom: 1.5rem;
            }}

            h1 {{
                text-align: center;
                font-size: 2.5rem;
                padding-bottom: 1rem;
                border-bottom: 3px solid var(--primary-color);
                margin-bottom: 2rem;
            }}

            .stats-overview {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2.5rem;
            }}

            .stat-card {{
                background: white;
                padding: 1.5rem;
                border-radius: var(--border-radius);
                box-shadow: var(--box-shadow);
                transition: transform 0.3s ease;
                border: 1px solid #e0e0e0;
            }}

            .stat-card:hover {{
                transform: translateY(-5px);
            }}

            .stat-card h3 {{
                font-size: 1.1rem;
                color: #666;
                margin-bottom: 1rem;
            }}

            .stat-card .value {{
                font-size: 2rem;
                font-weight: bold;
                margin-bottom: 0.5rem;
            }}

            .stat-card .subvalue {{
                color: #666;
                font-size: 0.9rem;
                font-weight: 500;
            }}

            .charts-section {{
                background: white;
                border-radius: var(--border-radius);
                padding: 2rem;
                margin: 2rem 0;
                box-shadow: var(--box-shadow);
            }}

            .charts-section img {{
                width: 100%;
                height: auto;
                border-radius: var(--border-radius);
            }}

            .stats-section {{
                background: white;
                border-radius: var(--border-radius);
                padding: 2rem;
                margin: 2rem 0;
                box-shadow: var(--box-shadow);
            }}

            .anomalies-table {{
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                margin-top: 1rem;
            }}

            .anomalies-table th,
            .anomalies-table td {{
                padding: 1rem;
                text-align: left;
                border: 1px solid #e0e0e0;
            }}

            .anomalies-table th {{
                background-color: var(--background-color);
                font-weight: 600;
                color: #2c3e50;
                position: sticky;
                top: 0;
            }}

            .anomalies-table tr:nth-child(even) {{
                background-color: var(--background-color);
            }}

            .anomalies-table tr:hover {{
                background-color: #f0f4f8;
            }}

            .level-high {{
                color: var(--danger-color);
                font-weight: bold;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                background-color: rgba(220, 53, 69, 0.1);
            }}

            @media (max-width: 768px) {{
                body {{
                    padding: 1rem;
                }}

                .stats-overview {{
                    grid-template-columns: 1fr;
                }}

                .container {{
                    padding: 1rem;
                }}

                h1 {{
                    font-size: 2rem;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Rapport d'analyse du trafic réseau</h1>
            
            <div class="stats-overview">
                <div class="stat-card">
                    <h3>Paquets analysés</h3>
                    <div class="value" style="color: var(--primary-color);">{stats['network_stats']['packets_analyzed']}</div>
                    <div class="subvalue">{stats['network_stats']['packets_rate']}</div>
                </div>
                
                <div class="stat-card">
                    <h3>Anomalies</h3>
                    <div class="value" style="color: var(--danger-color);">{stats['network_stats']['anomalies']['count']}</div>
                    <div class="subvalue">{stats['network_stats']['anomalies']['percentage']}</div>
                </div>
                
                <div class="stat-card">
                    <h3>IPs suspectes</h3>
                    <div class="value" style="color: var(--warning-color);">{stats['network_stats']['suspicious_ips']['count']}</div>
                    <div class="subvalue">{stats['network_stats']['suspicious_ips']['percentage']}</div>
                </div>
                
                <div class="stat-card">
                    <h3>Services</h3>
                    <div class="value" style="color: var(--success-color);">{stats['network_stats']['services']['count']}</div>
                    <div class="subvalue">{stats['network_stats']['services']['percentage']}</div>
                </div>
            </div>

            <div class="charts-section">
                <a href= "{generate_csv_report(stats)}"><img src="data:image/png;base64,{generate_protocol_chart(stats['protocol_distribution'])}" 
                     alt="Distribution des protocoles"> </a>
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
    file_path = 'DumpFile05.txt'
    stats = analyze_tcpdump(file_path)
    if stats:
        generate_html_report(stats)
        generate_csv_report(stats)
    else:
        print("Erreur lors de l'analyse des données")

if __name__ == "__main__":
    main()