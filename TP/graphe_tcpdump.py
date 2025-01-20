import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import csv
"""code fichier csv 
renvoie graphique tcpdump
a mettre dans dossier TP"""

def analyze_tcpdump(file_path):
    """
    Analyse un fichier CSV de données tcpdump et crée un graphique camembert
    
    Args:
        file_path (str): Chemin vers le fichier CSV
    """
    try:
        # Lecture du fichier CSV avec gestion plus flexible des erreurs
        df = pd.read_csv(file_path, 
                        sep=';', 
                        encoding='utf-8',
                        on_bad_lines='skip',    # Ignorer les lignes malformées
                        quoting=csv.QUOTE_NONE) # Désactiver le quotage
        
        # Afficher les informations sur le DataFrame
        print("\nInformations sur le DataFrame:")
        print(f"Nombre de lignes: {len(df)}")
        print(f"Colonnes présentes: {', '.join(df.columns)}")
        
        # Nettoyage du nom des colonnes
        df.columns = df.columns.str.rstrip(':')
        
        # Vérifier si la colonne SUMMARY existe
        summary_col = [col for col in df.columns if 'SUMMARY' in col]
        if not summary_col:
            print("\nAttention: Colonne 'SUMMARY' non trouvée.")
            print("Colonnes disponibles:", df.columns.tolist())
            return None
            
        summary_col = summary_col[0]
        
        # Compter les occurrences des événements
        event_counts = df[summary_col].value_counts()
        
        # Liste de couleurs standard
        colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC', 
                 '#99FFCC', '#FFB366', '#FF99FF', '#99CCFF', '#FFB3B3']
        
        # S'assurer d'avoir assez de couleurs
        while len(colors) < len(event_counts):
            colors.extend(colors)
        colors = colors[:len(event_counts)]
        
        # Création de la figure et des axes
        plt.figure(figsize=(12, 8))
        
        # Création du graphique camembert
        wedges, texts, autotexts = plt.pie(event_counts.values, 
                                         labels=event_counts.index,
                                         autopct='%1.1f%%',
                                         startangle=90,
                                         colors=colors)
        
        # Améliorer la lisibilité des étiquettes
        plt.setp(autotexts, size=8, weight="bold")
        plt.setp(texts, size=8)
        
        # Ajout du titre
        plt.title('Répartition des Événements TCPDump', pad=20)
        
        # Ajout de la légende avec scroll si nécessaire
        if len(event_counts) > 10:
            plt.legend(wedges, event_counts.index,
                      title="Types d'événements",
                      loc="center left",
                      bbox_to_anchor=(1, 0, 0.5, 1),
                      bbox_transform=plt.gcf().transFigure)
        else:
            plt.legend(wedges, event_counts.index,
                      title="Types d'événements",
                      loc="best")
        
        # Ajustement de la mise en page
        plt.tight_layout()
        
        # Sauvegarde du graphique
        plt.savefig('graphe_tcpdump.png', bbox_inches='tight', dpi=300)
        print("\nGraphique sauvegardé sous 'graphe_tcpdump.png'")
        
        # Affichage des statistiques
        print("\nStatistiques des événements:")
        print("-" * 50)
        for event, count in event_counts.items():
            print(f"{event}: {count} occurrences ({count/len(df)*100:.1f}%)")
        
        return event_counts
        
    except Exception as e:
        print(f"Erreur lors de l'analyse du fichier: {str(e)}")
        print("\nConseils de débogage:")
        print("1. Vérifiez le format du fichier CSV")
        print("2. Vérifiez l'encodage du fichier")
        print("3. Vérifiez la cohérence des séparateurs")
        return None

# Exemple d'utilisation
if __name__ == "__main__":
    file_path = "test_dcpdump.csv"
    event_counts = analyze_tcpdump(file_path)