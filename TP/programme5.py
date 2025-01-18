import markdown
from programme3 import extraire_seances_r107
from programme2 import convert_calendar_to_csv
from programme4 import compter_seances_par_mois, creer_graphique
import matplotlib.pyplot as plt

def generer_tableau_markdown(seances):
    """
    Génère la partie Markdown pour le tableau des séances
    """
    # En-tête du tableau
    markdown_text = "## Séances R1.07\n\n"
    markdown_text += "| Date | Durée | Type |\n"
    markdown_text += "|:----:|:-----:|:----:|\n"
    
    # Données du tableau
    for date, duree, type_seance in seances:
        markdown_text += f"| {date} | {duree} | {type_seance} |\n"
    
    return markdown_text

def generer_statistiques_markdown(seances_par_mois):
    """
    Génère la partie Markdown pour les statistiques
    """
    markdown_text = "\n## Statistiques des séances par mois\n\n"
    
    total_seances = sum(seances_par_mois.values())
    markdown_text += f"Nombre total de séances : {total_seances}\n\n"
    
    for mois, nombre in seances_par_mois.items():
        markdown_text += f"- {mois} : {nombre} séances\n"
    
    return markdown_text

def generer_html(groupe_tp):
    """
    Génère le fichier HTML complet
    """
    try:
        # Récupération des données
        events = convert_calendar_to_csv("ADE_RT1_Septembre2023_Decembre2023.ics")
        seances = extraire_seances_r107(events, groupe_tp)
        seances_par_mois = compter_seances_par_mois(events, groupe_tp)
        
        # Création du graphique et sauvegarde
        fig = creer_graphique(seances_par_mois)
        fig.savefig('seances_tp_r107.png', dpi=300, bbox_inches='tight')
        plt.close(fig)  # Fermeture de la figure pour libérer la mémoire
        
        # Construction du contenu Markdown
        markdown_content = f"""# Analyse des séances R1.07 pour le groupe {groupe_tp}

{generer_tableau_markdown(seances)}

{generer_statistiques_markdown(seances_par_mois)}

## Visualisation

![Graphique des séances](seances_tp_r107.png)
"""
        
        # Ajout du style CSS personnalisé
        css = """
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }
            th {
                background-color: #f2f2f2;
            }
            h1, h2 {
                color: #333;
            }
            img {
                max-width: 100%;
                height: auto;
                display: block;
                margin: 20px auto;
            }
        </style>
        """
        
        # Conversion en HTML avec options
        html = markdown.markdown(markdown_content, extensions=['tables'])
        
        # Création du fichier HTML complet
        with open('rapport_r107.html', 'w', encoding='utf-8') as f:
            f.write(f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport R1.07 - {groupe_tp}</title>
    {css}
</head>
<body>
{html}
</body>
</html>""")
        
        print("Le rapport a été généré avec succès dans 'rapport_r107.html'")
        
    except Exception as e:
        print(f"Une erreur s'est produite : {str(e)}")

def main():
    groupe_tp = "RT1-TP B2"  # À modifier selon votre groupe
    generer_html(groupe_tp)

if __name__ == "__main__":
    main()