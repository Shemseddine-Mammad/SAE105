def extraire_date_heure(chaine_date):
    """Convertit une date au format ICS en format JJ-MM-AAAA et HH:MM"""
    # Format attendu: YYYYMMDDTHHMMSSZ
    annee = chaine_date[0:4]
    mois = chaine_date[4:6]
    jour = chaine_date[6:8]
    heure = chaine_date[9:11]
    minutes = chaine_date[11:13]
    
    date = f"{jour}-{mois}-{annee}"
    heure_formattee = f"{heure}:{minutes}"
    
    return date, heure_formattee

def calculer_duree(debut, fin):
    """Calcule la durée entre deux dates au format ICS"""
    # Extraction des heures et minutes
    heure_debut = int(debut[9:11])
    min_debut = int(debut[11:13])
    heure_fin = int(fin[9:11])
    min_fin = int(fin[11:13])
    
    # Calcul de la différence
    total_minutes = (heure_fin * 60 + min_fin) - (heure_debut * 60 + min_debut)
    heures = total_minutes // 60
    minutes = total_minutes % 60
    
    return f"{heures:02d}:{minutes:02d}"

def extraire_infos_description(description):
    """Extrait les groupes et professeurs de la description"""
    lignes = description.split('\\n')
    groupes = []
    profs = []
    
    for ligne in lignes:
        if ligne.strip():
            if ligne.startswith('RT'):
                groupes.append(ligne.strip())
            elif not ligne.startswith('('):
                profs.append(ligne.strip())
    
    return '|'.join(profs), '|'.join(groupes)

def lire_fichier_ics(nom_fichier):
    """Lit le fichier ICS et retourne son contenu"""
    with open(nom_fichier, 'r', encoding='utf-8') as fichier:
        return fichier.read()

def convertir_ics_vers_csv(contenu_ics):
    """Convertit le contenu ICS en format pseudo-CSV"""
    lignes = contenu_ics.split('\n')
    infos = {}
    
    # Extraction des informations
    for ligne in lignes:
        if ':' in ligne:
            cle, valeur = ligne.split(':', 1)
            infos[cle] = valeur.strip()
    
    # Traitement des dates
    date, heure = extraire_date_heure(infos['DTSTART'])
    duree = calculer_duree(infos['DTSTART'], infos['DTEND'])
    
    # Extraction des professeurs et groupes
    profs, groupes = extraire_infos_description(infos.get('DESCRIPTION', ''))
    
    # Par défaut, on considère que c'est un CM
    modalite = "CM"
    
    # Construction de la chaîne CSV avec retours à la ligne
    elements = [
        infos.get('UID', ''),
        date,
        heure,
        duree,
        modalite,
        infos.get('SUMMARY', ''),
        infos.get('LOCATION', ''),
        profs,
        groupes
    ]
    
    # Joindre les éléments avec ;\n pour avoir un retour à la ligne après chaque point-virgule
    return ';\n'.join(elements)

def main():
    try:
        # Lecture du fichier
        contenu = lire_fichier_ics('evenementSAE_15.ics')
        
        # Conversion et affichage
        resultat = convertir_ics_vers_csv(contenu)
        print(resultat)
        
    except FileNotFoundError:
        print("Erreur: Le fichier n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur est survenue: {str(e)}")

if __name__ == "__main__":
    main()