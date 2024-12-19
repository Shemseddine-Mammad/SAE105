from datetime import datetime

def lire_fichier_ics(nom_fichier):
    """
    Lit le fichier ICS et retourne son contenu sous forme de liste de lignes
    """
    with open(nom_fichier, 'r', encoding='utf-8') as fichier:
        return [ligne.strip() for ligne in fichier if ligne.strip()]

def extraire_evenements(lignes):
    """
    Extrait les événements individuels du fichier ICS
    """
    evenements = []
    evenement_courant = []
    dans_evenement = False
    
    for ligne in lignes:
        if ligne == "BEGIN:VEVENT":
            dans_evenement = True
            evenement_courant = []
        elif ligne == "END:VEVENT":
            dans_evenement = False
            evenements.append(evenement_courant)
        elif dans_evenement:
            evenement_courant.append(ligne)
            
    return evenements

def parser_evenement(evenement):
    """
    Parse un événement ICS et extrait les informations pertinentes
    """
    infos = {
        "SUMMARY": "vide",
        "LOCATION": "vide",
        "DESCRIPTION": "vide",
        "DTSTART": "vide",
        "DTEND": "vide"
    }
    
    for ligne in evenement:
        for cle in infos.keys():
            if ligne.startswith(cle + ":"):
                infos[cle] = ligne.split(":", 1)[1]
                break
                
    return infos

def est_r107(summary):
    """
    Vérifie si l'événement est une séance de R1.07
    """
    return "R1.07" in summary

def est_mon_groupe(description, groupe_tp):
    """
    Vérifie si l'événement correspond au groupe de TP spécifié
    """
    return groupe_tp in description

def determiner_type_seance(description):
    """
    Détermine le type de séance (CM, TD ou TP)
    """
    if "CM" in description:
        return "CM"
    elif "TD" in description:
        return "TD"
    elif "TP" in description:
        return "TP"
    return "Inconnu"

def calculer_duree_minutes(date_debut, date_fin):
    """
    Calcule la durée en minutes entre deux dates au format ICS
    """
    debut = datetime.strptime(date_debut, "%Y%m%dT%H%M%S")
    fin = datetime.strptime(date_fin, "%Y%m%dT%H%M%S")
    duree = (fin - debut).total_seconds() / 60
    return int(duree)

def formater_date(date_ics):
    """
    Formate la date ICS en format lisible
    """
    date = datetime.strptime(date_ics, "%Y%m%dT%H%M%S")
    return date.strftime("%d/%m/%Y %H:%M")

def main():
    nom_fichier = "ADE_RT1_Septembre2023_Decembre2023.ics"
    groupe_tp = "TP"  # À modifier selon votre groupe
    seances_r107 = []
    
    # Lecture du fichier
    lignes = lire_fichier_ics(nom_fichier)
    evenements = extraire_evenements(lignes)
    
    # Traitement de chaque événement
    for evenement in evenements:
        infos = parser_evenement(evenement)
        
        # Filtrer les séances R1.07 pour notre groupe
        if est_r107(infos["SUMMARY"]) and est_mon_groupe(infos["DESCRIPTION"], groupe_tp):
            date = formater_date(infos["DTSTART"])
            duree = calculer_duree_minutes(infos["DTSTART"], infos["DTEND"])
            type_seance = determiner_type_seance(infos["DESCRIPTION"])
            
            seances_r107.append({
                "date": date,
                "duree": duree,
                "type": type_seance
            })
    
    return seances_r107

if __name__ == "__main__":
    seances = main()
    print("Séances R1.07 pour votre groupe :")
    print("Date            | Durée (min) | Type")
    print("-" * 40)
    for seance in seances:
        print(f"{seance['date']} | {seance['duree']:10d} | {seance['type']}")