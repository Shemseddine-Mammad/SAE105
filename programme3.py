from programme2 import convert_calendar_to_csv

def extraire_seances_r107(events, groupe_tp):
    """
    Extrait les séances R1.07 pour un groupe de TP spécifique.
    Retourne une liste de tuples (date, durée, type_seance)
    """
    seances_r107 = []
    
    for event in events:
        # Découpage de l'événement en ses composantes
        elements = event.split(';')
        if len(elements) < 9:  # Vérification du format
            continue
            
        # Extraction des informations pertinentes
        date = elements[1]        # Format: JJ-MM-AAAA
        heure = elements[2]       # Format: HH:MM
        duree = elements[3]       # Format: HH:MM
        type_seance = elements[4] # CM/TD/TP
        intitule = elements[5]    # Titre de l'événement
        groupes = elements[8]     # Liste des groupes séparés par |
        
        # Vérification si c'est une séance R1.07
        if not "R1.07" in intitule:
            continue
            
        # Vérification si le groupe de TP est concerné
        if groupes == "vide" or (groupe_tp not in groupes.split('|') and "S1" not in groupes.split('|')):
            continue
            
        # Création d'un horodatage complet pour le tri
        horodatage = f"{date} {heure}"
        
        # Ajout de la séance à la liste
        seances_r107.append((horodatage, date, duree, type_seance))
    
    # Tri des séances par date et heure
    seances_r107.sort(key=lambda x: x[0])
    
    # Retourne les séances sans l'horodatage utilisé pour le tri
    return [(seance[1], seance[2], seance[3]) for seance in seances_r107]

def afficher_seances(seances):
    """
    Affiche les séances de manière formatée
    """
    print("Séances R1.07 :")
    print("─" * 50)
    print(f"{'Date':^12} | {'Durée':^8} | {'Type':^6}")
    print("─" * 50)
    
    for date, duree, type_seance in seances:
        print(f"{date:^12} | {duree:^8} | {type_seance:^6}")

def main():
    # Nom du fichier ICS
    filename = "ADE_RT1_Septembre2023_Decembre2023.ics"
    
    # Groupe de TP à filtrer
    groupe_tp = "RT1-TP B1"  # À modifier selon votre groupe
    
    try:
        # Récupération de tous les événements
        events = convert_calendar_to_csv(filename)
        
        # Extraction des séances R1.07
        seances = extraire_seances_r107(events, groupe_tp)
        
        # Affichage des résultats
        print(f"\nExtractions des séances R1.07 pour le groupe {groupe_tp}")
        print(f"Nombre de séances trouvées : {len(seances)}")
        
        afficher_seances(seances)
        
    except FileNotFoundError:
        print(f"Le fichier {filename} n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur s'est produite : {str(e)}")

if __name__ == "__main__":
    main()