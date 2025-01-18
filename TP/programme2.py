def convert_date_ics_to_csv(date_ics):
    """
    Convertit une date du format ICS (AAAAMMDDTHHMMSSZ) vers le format CSV (JJ-MM-AAAA)
    """
    annee = date_ics[0:4]
    mois = date_ics[4:6]
    jour = date_ics[6:8]
    return f"{jour}-{mois}-{annee}"

def convert_time_ics_to_csv(time_ics):
    """
    Extrait l'heure et les minutes d'une date ICS (AAAAMMDDTHHMMSSZ) vers le format HH:MM
    """
    heure = time_ics[9:11]
    minutes = time_ics[11:13]
    return f"{heure}:{minutes}"

def calculate_duration(start_time, end_time):
    """
    Calcule la durée entre deux timestamps ICS et retourne au format HH:MM
    """
    start_hour = int(start_time[9:11])
    start_min = int(start_time[11:13])
    end_hour = int(end_time[9:11])
    end_min = int(end_time[11:13])
    
    duration_min = (end_hour * 60 + end_min) - (start_hour * 60 + start_min)
    hours = duration_min // 60
    minutes = duration_min % 60
    
    return f"{hours:02d}:{minutes:02d}"

def extract_event_data(event_lines):
    """
    Extrait les données d'un événement à partir de ses lignes
    """
    event_data = {}
    for line in event_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            event_data[key] = value.strip()
    return event_data

def parse_description(description):
    """
    Parse la description pour extraire les groupes et les professeurs
    """
    if not description:
        return [], []
    
    groups = []
    profs = []
    
    for item in description.split('\\n'):
        item = item.strip()
        if not item:
            continue
        if 'RT' in item or 'S1' in item:  # Supposé être un groupe
            groups.append(item)
        elif not item.startswith('('):  # Supposé être un prof
            profs.append(item)
    
    return groups, profs

def detect_modality(summary, location):
    """
    Détecte la modalité de l'événement basée sur le résumé et la localisation
    """
    summary = summary.upper()
    if 'CM' in summary:
        return 'CM'
    elif 'TD' in summary:
        return 'TD'
    elif 'TP' in summary:
        return 'TP'
    elif 'DS' in summary:
        return 'DS'
    elif 'PROJ' in summary:
        return 'Proj'
    # Par défaut, on essaie de détecter à partir de la salle
    if location and ('AMPHI' in location.upper()):
        return 'CM'
    return 'CM'  # Valeur par défaut si aucune modalité n'est détectée

def parse_location(location):
    """
    Parse la localisation pour gérer plusieurs salles
    """
    if not location:
        return 'vide'
    return location.replace(',', '|').replace(' ', '')

def event_to_csv(event_data):
    """
    Convertit les données d'un événement en format pseudo-CSV
    """
    # Extraction des données de base
    uid = event_data.get('UID', 'vide')
    start_date = convert_date_ics_to_csv(event_data.get('DTSTART', ''))
    start_time = convert_time_ics_to_csv(event_data.get('DTSTART', ''))
    duration = calculate_duration(event_data.get('DTSTART', ''), event_data.get('DTEND', ''))
    
    # Traitement de la description
    groups, profs = parse_description(event_data.get('DESCRIPTION', ''))
    
    # Gestion des cas particuliers
    summary = event_data.get('SUMMARY', 'vide')
    location = parse_location(event_data.get('LOCATION', ''))
    modalite = detect_modality(summary, location)
    
    # Si aucun professeur ou groupe n'est trouvé, utiliser 'vide'
    profs_str = '|'.join(profs) if profs else 'vide'
    groups_str = '|'.join(groups) if groups else 'vide'
    
    # Construction de la chaîne CSV
    csv_parts = [
        uid,
        start_date,
        start_time,
        duration,
        modalite,
        summary,
        location,
        profs_str,
        groups_str
    ]
    
    return ';'.join(csv_parts)

def convert_calendar_to_csv(filename):
    """
    Convertit un fichier ICS calendrier complet en un tableau de chaînes pseudo-CSV
    """
    events_csv = []
    current_event_lines = []
    in_event = False
    
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('BEGIN:VEVENT'):
                in_event = True
                current_event_lines = []
            elif line.startswith('END:VEVENT'):
                in_event = False
                event_data = extract_event_data(current_event_lines)
                events_csv.append(event_to_csv(event_data))
            elif in_event:
                current_event_lines.append(line)
    
    return events_csv

# Programme principal
if __name__ == "__main__":
    filename = "ADE_RT1_Septembre2023_Decembre2023.ics"
    try:
        events = convert_calendar_to_csv(filename)
        print(f"Nombre d'événements traités : {len(events)}")
        print("\nExemple des 3 premiers événements :")
        for i, event in enumerate(events[:3], 1):
            print(f"\nÉvénement {i}:")
            print(event)
    except FileNotFoundError:
        print(f"Le fichier {filename} n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur s'est produite : {str(e)}")