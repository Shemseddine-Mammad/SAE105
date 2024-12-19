def lire_fichier_ics(nom_fichier):
    """
    Lit un fichier ICS et retourne son contenu sous forme de dictionnaire
    """
    event_data = {}
    try:
        with open(nom_fichier, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    event_data[key] = value
    except FileNotFoundError:
        print(f"Erreur: Le fichier {nom_fichier} n'a pas été trouvé.")
        return None
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier: {e}")
        return None
    
    return event_data

def convertir_date_heure(chaine_date):
    """
    Convertit une date au format ICS (20240110T080000Z) en format JJ-MM-AAAA et HH:MM
    """
    annee = chaine_date[0:4]
    mois = chaine_date[4:6]
    jour = chaine_date[6:8]
    heure = chaine_date[9:11]
    minutes = chaine_date[11:13]
    
    date = f"{jour}-{mois}-{annee}"
    heure = f"{heure}:{minutes}"
    
    return date, heure

def calculer_duree(debut, fin):
    """
    Calcule la durée entre deux horaires au format ICS
    """
    debut_heure = int(debut[9:11])
    debut_min = int(debut[11:13])
    fin_heure = int(fin[9:11])
    fin_min = int(fin[11:13])
    
    # Calcul de la durée
    duree_heures = fin_heure - debut_heure
    duree_minutes = fin_min - debut_min
    
    if duree_minutes < 0:
        duree_heures -= 1
        duree_minutes += 60
        
    return f"{duree_heures:02d}:{duree_minutes:02d}"

def extraire_infos_description(description):
    """
    Extrait les informations du champ DESCRIPTION
    """
    lignes = description.split('\\n')
    groupe = ""
    prof = ""
    
    for ligne in lignes:
        if "RT1-" in ligne:
            groupe = ligne.strip()
        elif ligne and "Exporté" not in ligne and ligne != "\n":
            prof = ligne.strip()
    
    return groupe, prof

def convertir_en_csv(event_data):
    """
    Convertit les données de l'événement en format pseudo-CSV
    """
    if not event_data:
        return ""
        
    # Extraction des données
    uid = event_data.get('UID', 'vide')
    date, heure = convertir_date_heure(event_data['DTSTART'])
    duree = calculer_duree(event_data['DTSTART'], event_data['DTEND'])
    modalite = "CM"  # Par défaut pour cet exemple, à adapter selon les besoins
    intitule = event_data.get('SUMMARY', 'vide')
    salle = event_data.get('LOCATION', 'vide')
    groupe, prof = extraire_infos_description(event_data.get('DESCRIPTION', ''))
    
    # Construction de la ligne CSV
    return f"{uid};{date};{heure};{duree};{modalite};{intitule};{salle};{prof};{groupe}"

def ecrire_fichier_csv(ligne_csv, nom_fichier_sortie):
    """
    Écrit la ligne CSV dans un fichier
    """
    try:
        with open(nom_fichier_sortie, 'w', encoding='utf-8') as file:
            # Écriture de l'en-tête
            en_tete = "uid;date;heure;duree;modalite;intitule;salle;professeur;groupe\n"
            file.write(en_tete)
            # Écriture des données
            file.write(ligne_csv)
        print(f"Le fichier {nom_fichier_sortie} a été créé avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'écriture du fichier: {e}")

def main():
    # Noms des fichiers
    nom_fichier_entree = "ADE_RT1_Septembre2023_Decembre2023.ics"
    nom_fichier_sortie = "evenement.csv"
    
    # Lecture et conversion
    event_data = lire_fichier_ics(nom_fichier_entree)
    if event_data:
        ligne_csv = convertir_en_csv(event_data)
        ecrire_fichier_csv(ligne_csv, nom_fichier_sortie)

if __name__ == "__main__":
    main()

print("hello word")