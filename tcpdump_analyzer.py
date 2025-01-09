import re
from collections import defaultdict
import matplotlib.pyplot as plt
from datetime import datetime
import os

class TcpdumpAnalyzer:
    def __init__(self, filename):
        """Initialise l'analyseur avec le fichier tcpdump"""
        self.filename = filename
        self.packets = []
        self.stats = {
            'total_packets': 0,
            'protocols': defaultdict(int),
            'src_ips': defaultdict(int),
            'dst_ips': defaultdict(int),
            'packet_sizes': [],
            'timestamps': []
        }

    def parse_file(self):
        """Parse le fichier tcpdump"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                for line in f:
                    self.parse_line(line.strip())
            return True
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier : {str(e)}")
            return False

    def parse_line(self, line):
        """Parse une ligne de tcpdump"""
        # Pattern pour extraire les informations importantes
        timestamp_pattern = r'^(\d{2}:\d{2}:\d{2}\.\d{6})'
        ip_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        protocol_pattern = r'(TCP|UDP|ICMP|ARP)'
        length_pattern = r'length (\d+)'

        # Extraction des informations
        timestamp_match = re.search(timestamp_pattern, line)
        ip_matches = re.findall(ip_pattern, line)
        protocol_match = re.search(protocol_pattern, line)
        length_match = re.search(length_pattern, line)

        if timestamp_match:
            self.stats['timestamps'].append(timestamp_match.group(1))

        if ip_matches and len(ip_matches) >= 2:
            src_ip, dst_ip = ip_matches[0], ip_matches[1]
            self.stats['src_ips'][src_ip] += 1
            self.stats['dst_ips'][dst_ip] += 1

        if protocol_match:
            self.stats['protocols'][protocol_match.group(1)] += 1

        if length_match:
            self.stats['packet_sizes'].append(int(length_match.group(1)))

        self.stats['total_packets'] += 1

    def generate_graphs(self, output_dir):
        """Génère les graphiques pour le rapport"""
        # Graphique des protocoles
        plt.figure(figsize=(10, 6))
        protocols = list(self.stats['protocols'].keys())
        values = list(self.stats['protocols'].values())
        plt.bar(protocols, values)
        plt.title('Distribution des Protocoles')
        plt.xlabel('Protocole')
        plt.ylabel('Nombre de Paquets')
        plt.savefig(os.path.join(output_dir, 'protocols.png'))
        plt.close()

        # Graphique des tailles de paquets
        plt.figure(figsize=(10, 6))
        plt.hist(self.stats['packet_sizes'], bins=50)
        plt.title('Distribution des Tailles de Paquets')
        plt.xlabel('Taille (bytes)')
        plt.ylabel('Fréquence')
        plt.savefig(os.path.join(output_dir, 'packet_sizes.png'))
        plt.close()

    def generate_html_report(self, output_dir='tcpdump_report'):
        """Génère le rapport HTML"""
        # Création du dossier de sortie
        os.makedirs(output_dir, exist_ok=True)

        # Génération des graphiques
        self.generate_graphs(output_dir)

        # Top 10 des IPs les plus actives
        top_src_ips = dict(sorted(self.stats['src_ips'].items(), key=lambda x: x[1], reverse=True)[:10])
        top_dst_ips = dict(sorted(self.stats['dst_ips'].items(), key=lambda x: x[1], reverse=True)[:10])

        # Création du contenu HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Rapport d'Analyse Tcpdump</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        .container {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        img {{
            max-width: 100%;
            height: auto;
            margin: 20px 0;
        }}
        h2 {{
            color: #333;
            border-bottom: 2px solid #ddd;
            padding-bottom: 10px;
        }}
    </style>
</head>
<body>
    <h1>Rapport d'Analyse Tcpdump</h1>
    <div class="container">
        <h2>Informations Générales</h2>
        <p>Nombre total de paquets : {self.stats['total_packets']}</p>
        <p>Date d'analyse : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="container">
        <h2>Distribution des Protocoles</h2>
        <img src="protocols.png" alt="Distribution des Protocoles">
        <table>
            <tr>
                <th>Protocole</th>
                <th>Nombre de Paquets</th>
            </tr>
            {''.join(f'<tr><td>{proto}</td><td>{count}</td></tr>' for proto, count in self.stats['protocols'].items())}
        </table>
    </div>

    <div class="container">
        <h2>Distribution des Tailles de Paquets</h2>
        <img src="packet_sizes.png" alt="Distribution des Tailles de Paquets">
        <p>Taille moyenne des paquets : {sum(self.stats['packet_sizes']) / len(self.stats['packet_sizes']):.2f} bytes</p>
    </div>

    <div class="container">
        <h2>Top 10 des Adresses IP Source</h2>
        <table>
            <tr>
                <th>Adresse IP</th>
                <th>Nombre de Paquets</th>
            </tr>
            {''.join(f'<tr><td>{ip}</td><td>{count}</td></tr>' for ip, count in top_src_ips.items())}
        </table>
    </div>

    <div class="container">
        <h2>Top 10 des Adresses IP Destination</h2>
        <table>
            <tr>
                <th>Adresse IP</th>
                <th>Nombre de Paquets</th>
            </tr>
            {''.join(f'<tr><td>{ip}</td><td>{count}</td></tr>' for ip, count in top_dst_ips.items())}
        </table>
    </div>
</body>
</html>
        """

        # Sauvegarde du rapport HTML
        with open(os.path.join(output_dir, 'report.html'), 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"Rapport généré dans le dossier : {output_dir}")

def main():
    # Configuration
    tcpdump_file = "fichier182.txt"  # Remplacer par le nom de votre fichier tcpdump
    
    # Création et exécution de l'analyseur
    analyzer = TcpdumpAnalyzer(tcpdump_file)
    
    if analyzer.parse_file():
        print("Analyse du fichier tcpdump réussie")
        analyzer.generate_html_report()
    else:
        print("Erreur lors de l'analyse du fichier tcpdump")

if __name__ == "__main__":
    main()