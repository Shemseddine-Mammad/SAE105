# Programme2.py
def lire_fichier_ics(nom_fichier):
    """Lit le fichier ICS et retourne son contenu"""
    with open(nom_fichier, 'r', encoding='utf-8') as fichier:
        return fichier.read()

def extraire_evenements(contenu_ics):
    """Extrait tous les événements du calendrier"""
    evenements = []
    evenement_courant = []
    est_dans_evenement = False
    
    for ligne in contenu_ics.split('\n'):
        if ligne.startswith('BEGIN:VEVENT'):
            est_dans_evenement = True
            evenement_courant = []
        elif ligne.startswith('END:VEVENT'):
            est_dans_evenement = False
            evenements.append('\n'.join(evenement_courant))
        elif est_dans_evenement:
            evenement_courant.append(ligne)
            
    return evenements

def extraire_date_heure(chaine_date):
    """Convertit une date au format ICS en format JJ-MM-AAAA et HH:MM"""
    annee = chaine_date[0:4]
    mois = chaine_date[4:6]
    jour = chaine_date[6:8]
    heure = chaine_date[9:11]
    minutes = chaine_date[11:13]
    
    return f"{jour}-{mois}-{annee}", f"{heure}:{minutes}"

def calculer_duree(debut, fin):
    """Calcule la durée entre deux dates au format ICS"""
    heure_debut = int(debut[9:11])
    min_debut = int(debut[11:13])
    heure_fin = int(fin[9:11])
    min_fin = int(fin[11:13])
    
    total_minutes = (heure_fin * 60 + min_fin) - (heure_debut * 60 + min_debut)
    heures = total_minutes // 60
    minutes = total_minutes % 60
    
    return f"{heures:02d}:{minutes:02d}"

def extraire_infos_description(description):
    """Extrait les groupes et professeurs de la description"""
    if not description:
        return "vide", "vide"
        
    lignes = description.split('\\n')
    groupes = []
    profs = []
    
    for ligne in lignes:
        if ligne.strip():
            if ligne.startswith('RT'):
                groupes.append(ligne.strip())
            elif not ligne.startswith('('):
                profs.append(ligne.strip())
    
    return ('|'.join(profs) or "vide"), ('|'.join(groupes) or "vide")

def determiner_modalite(summary, description):
    """Détermine la modalité de l'événement"""
    if "CM" in summary or "CM" in description:
        return "CM"
    elif "TD" in summary or "TD" in description:
        return "TD"
    elif "TP" in summary or "TP" in description:
        return "TP"
    elif "DS" in summary or "DS" in description:
        return "DS"
    elif "Proj" in summary or "Proj" in description:
        return "Proj"
    return "CM"  # Par défaut

def convertir_evenement_vers_csv(contenu_evenement):
    """Convertit un événement ICS en format pseudo-CSV"""
    infos = {}
    for ligne in contenu_evenement.split('\n'):
        if ':' in ligne:
            cle, valeur = ligne.split(':', 1)
            infos[cle] = valeur.strip()
    
    date, heure = extraire_date_heure(infos['DTSTART'])
    duree = calculer_duree(infos['DTSTART'], infos['DTEND'])
    profs, groupes = extraire_infos_description(infos.get('DESCRIPTION', ''))
    modalite = determiner_modalite(infos.get('SUMMARY', ''), infos.get('DESCRIPTION', ''))
    
    elements = [
        infos.get('UID', 'vide'),
        date,
        heure,
        duree,
        modalite,
        infos.get('SUMMARY', 'vide'),
        infos.get('LOCATION', 'vide'),
        profs,
        groupes
    ]
    
    return ';'.join(elements)

def programme2():
    try:
        # Lecture du fichier
        contenu = lire_fichier_ics('ADE_RT1_Septembre2023_Decembre2023.ics')
        
        # Extraction des événements
        evenements = extraire_evenements(contenu)
        
        # Conversion de chaque événement
        resultats = []
        for evenement in evenements:
            csv_event = convertir_evenement_vers_csv(evenement)
            resultats.append(csv_event)
        
        return resultats
        
    except Exception as e:
        print(f"Une erreur est survenue: {str(e)}")
        return []

# Programme3.py
def filtrer_r107(evenements, groupe_tp):
    """Filtre les séances de R1.07 pour un groupe spécifique"""
    seances_r107 = []
    
    for evenement in evenements:
        infos = evenement.split(';')
        if 'R1.07' in infos[5] and groupe_tp in infos[8]:
            seances_r107.append([
                infos[1],  # date
                infos[3],  # durée
                infos[4]   # type
            ])
    
    return seances_r107

# Programme4.py
import matplotlib.pyplot as plt
from datetime import datetime

def compter_tp_par_mois(evenements, groupe):
    """Compte le nombre de TP par mois pour un groupe donné"""
    tp_par_mois = {'09': 0, '10': 0, '11': 0, '12': 0}
    
    for evenement in evenements:
        infos = evenement.split(';')
        if infos[4] == 'TP' and groupe in infos[8]:
            date = datetime.strptime(infos[1], '%d-%m-%Y')
            mois = date.strftime('%m')
            if mois in tp_par_mois:
                tp_par_mois[mois] += 1
    
    return tp_par_mois

def creer_graphique(tp_par_mois):
    """Crée un graphique en barres des TP par mois"""
    mois = ['Septembre', 'Octobre', 'Novembre', 'Décembre']
    valeurs = list(tp_par_mois.values())
    
    plt.figure(figsize=(10, 6))
    plt.bar(mois, valeurs)
    plt.title('Nombre de séances de TP par mois (Groupe A1)')
    plt.xlabel('Mois')
    plt.ylabel('Nombre de séances')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig('tp_par_mois.png')
    plt.close()

def main():
    # Exécution du Programme2
    resultats = programme2()
    print("Résultat Programme2 (premiers événements) :")
    for resultat in resultats[:3]:  # Affiche les 3 premiers événements
        print(resultat)
        print("-" * 50)
    
    # Exécution du Programme3
    seances_r107 = filtrer_r107(resultats, "A1")
    print("\nRésultat Programme3 (séances R1.07) :")
    print("Date | Durée | Type")
    print("-" * 30)
    for seance in seances_r107:
        print(" | ".join(seance))
    
    # Exécution du Programme4
    tp_par_mois = compter_tp_par_mois(resultats, "A1")
    print("\nRésultat Programme4 (nombre de TP par mois) :")
    for mois, nombre in tp_par_mois.items():
        print(f"Mois {mois}: {nombre} TP")
    creer_graphique(tp_par_mois)

if __name__ == "__main__":
    main()