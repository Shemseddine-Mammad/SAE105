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

def extraire_professeurs_salles(description):
    """
    Extrait les professeurs et salles de la description
    """
    profs = []
    salles = []
    
    if description != "vide":
        elements = description.split()
        for element in elements:
            if element.startswith("(") and element.endswith(")"):
                profs.append(element[1:-1])
            elif element.startswith("[") and element.endswith("]"):
                salles.append(element[1:-1])
    
    return profs if profs else ["vide"], salles if salles else ["vide"]

def formater_pseudo_csv(infos, profs, salles):
    """
    Formate les informations en pseudo-code CSV
    """
    date_debut = infos["DTSTART"]
    date_fin = infos["DTEND"]
    matiere = infos["SUMMARY"]
    profs_str = ",".join(profs)
    salles_str = ",".join(salles)
    
    return f"{date_debut};{date_fin};{matiere};{profs_str};{salles_str}"

def main():
    nom_fichier = "ADE_RT1_Septembre2023_Decembre2023.ics"
    resultat = []
    
    # Lecture du fichier
    lignes = lire_fichier_ics(nom_fichier)
    
    # Extraction des événements
    evenements = extraire_evenements(lignes)
    
    # Traitement de chaque événement
    for evenement in evenements:
        infos = parser_evenement(evenement)
        profs, salles = extraire_professeurs_salles(infos["DESCRIPTION"])
        ligne_csv = formater_pseudo_csv(infos, profs, salles)
        resultat.append(ligne_csv)
    
    return resultat

if __name__ == "__main__":
    resultat = main()
    # Affichage des résultats
    for ligne in resultat:
        print(ligne)