import matplotlib.pyplot as plt
from programme2 import convert_calendar_to_csv
from collections import defaultdict

def compter_seances_par_mois(events, groupe_tp):
    """
    Compte le nombre de séances de TP par mois pour un groupe donné
    """
    # Dictionnaire pour stocker le compte des séances par mois
    seances_par_mois = defaultdict(int)
    
    # Noms des mois pour l'affichage
    noms_mois = {
        "09": "Septembre",
        "10": "Octobre",
        "11": "Novembre",
        "12": "Décembre"
    }
    
    for event in events:
        elements = event.split(';')
        if len(elements) < 9:
            continue
            
        date = elements[1]        # Format: JJ-MM-AAAA
        type_seance = elements[4] # CM/TD/TP
        intitule = elements[5]    # Titre de l'événement
        groupes = elements[8]     # Liste des groupes
        
        # Extraction du mois de la date
        mois = date.split('-')[1]
        
        # Ne considérer que les TP pour le groupe spécifié
        if (type_seance == "TP" and 
            "R1.07" in intitule and 
            groupe_tp in groupes.split('|')):
            seances_par_mois[noms_mois[mois]] += 1
    
    return seances_par_mois

def creer_graphique(seances_par_mois):
    """
    Crée un graphique en barres montrant la répartition des séances par mois
    """
    # Configuration du style de matplotlib
    plt.style.use('classic')    # Utilisation d'un style standard
    
    # Création de la figure et des axes
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Création du graphique en barres
    mois = list(seances_par_mois.keys())
    nombres = list(seances_par_mois.values())
    
    bars = ax.bar(mois, nombres)
    
    # Personnalisation du graphique
    ax.set_title('Nombre de séances de TP R1.07 par mois', pad=20)
    ax.set_xlabel('Mois')
    ax.set_ylabel('Nombre de séances')
    
    # Rotation des labels de l'axe x pour une meilleure lisibilité
    plt.xticks(rotation=45)
    
    # Ajout des valeurs au-dessus des barres
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom')
    
    # Ajustement automatique de la mise en page
    plt.tight_layout()
    
    return fig

def main():
    # Configuration
    filename = "ADE_RT1_Septembre2023_Decembre2023.ics"
    groupe_tp = "RT1-TP B2"  # À modifier selon votre groupe
    
    try:
        # Récupération de tous les événements
        events = convert_calendar_to_csv(filename)
        
        # Comptage des séances par mois
        seances_par_mois = compter_seances_par_mois(events, groupe_tp)
        
        # Création du graphique
        fig = creer_graphique(seances_par_mois)
        
        # Affichage des données numériques
        print("\nNombre de séances de TP par mois :")
        for mois, nombre in seances_par_mois.items():
            print(f"{mois}: {nombre} séances")
        
        # Export au format PNG
        fig.savefig('seances_tp_r107.png', dpi=300, bbox_inches='tight')
        print("\nLe graphique a été exporté sous le nom 'seances_tp_r107.png'")
        
        # Affichage du graphique
        plt.show()
        
    except FileNotFoundError:
        print(f"Le fichier {filename} n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur s'est produite : {str(e)}")

if __name__ == "__main__":
    main()