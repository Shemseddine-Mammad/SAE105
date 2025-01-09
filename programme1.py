def convert_date_ics_to_csv(date_ics):
    """
    Convertit une date du format ICS (AAAAMMDDTHHMMSSZ) vers le format CSV (JJ-MM-AAAA)
    """
    # Extraction des composants de la date
    annee = date_ics[0:4]
    mois = date_ics[4:6]
    jour = date_ics[6:8]
    return f"{jour}-{mois}-{annee}"

def convert_time_ics_to_csv(time_ics):
    """
    Extrait l'heure et les minutes d'une date ICS (AAAAMMDDTHHMMSSZ) vers le format HH:MM
    """
    # L'heure commence après le T (position 9)
    heure = time_ics[9:11]
    minutes = time_ics[11:13]
    return f"{heure}:{minutes}"

def calculate_duration(start_time, end_time):
    """
    Calcule la durée entre deux timestamps ICS et retourne au format HH:MM
    """
    # Conversion des heures et minutes en entiers
    start_hour = int(start_time[9:11])
    start_min = int(start_time[11:13])
    end_hour = int(end_time[9:11])
    end_min = int(end_time[11:13])
    
    # Calcul de la différence
    duration_min = (end_hour * 60 + end_min) - (start_hour * 60 + start_min)
    hours = duration_min // 60
    minutes = duration_min % 60
    
    return f"{hours:02d}:{minutes:02d}"

def extract_event_details(content):
    """
    Extrait les détails d'un événement à partir du contenu ICS
    """
    lines = content.split('\n')
    event_data = {}
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            event_data[key] = value.strip()
    
    return event_data

def parse_description(description):
    """
    Parse la description pour extraire les groupes et les professeurs
    """
    # La description contient typiquement les groupes et/ou les professeurs
    groups = []
    profs = []
    
    # Séparation des lignes de la description
    for item in description.split('\\n'):
        item = item.strip()
        if item.startswith('RT'):  # Supposé être un groupe
            groups.append(item)
        elif item and not item.startswith('('):  # Supposé être un prof
            profs.append(item)
    
    return groups, profs

def convert_ics_to_csv(filename):
    """
    Convertit un fichier ICS en format pseudo-CSV
    """
    # Lecture du fichier
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Extraction des détails
    event_data = extract_event_details(content)
    
    # Extraction des informations nécessaires
    uid = event_data.get('UID', '')
    start_date = convert_date_ics_to_csv(event_data.get('DTSTART', ''))
    start_time = convert_time_ics_to_csv(event_data.get('DTSTART', ''))
    duration = calculate_duration(event_data.get('DTSTART', ''), event_data.get('DTEND', ''))
    
    # Extraction des informations de la description
    groups, profs = parse_description(event_data.get('DESCRIPTION', ''))
    
    # Détermination de la modalité (à adapter selon les besoins)
    modalite = "CM"  # Par défaut, à adapter selon les règles spécifiques
    
    # Construction de la chaîne CSV
    csv_parts = [
        uid,
        start_date,
        start_time,
        duration,
        modalite,
        event_data.get('SUMMARY', ''),
        event_data.get('LOCATION', '').replace(',', '|'),
        '|'.join(profs),
        '|'.join(groups)
    ]
    
    return ';'.join(csv_parts)

# Programme principal
if __name__ == "__main__":
    # Exemple d'utilisation
    filename = "evenementSAE_15.ics"
    try:
        result = convert_ics_to_csv(filename)
        print(result)
    except FileNotFoundError:
        print(f"Le fichier {filename} n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur s'est produite : {str(e)}")