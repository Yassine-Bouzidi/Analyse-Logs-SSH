import re
import csv
from datetime import datetime

def load_templates():
    """Charge les templates d'événements"""
    event_patterns = {
        'E1': r'Accepted password for .+ from .+ port .+ ssh2',
        'E2': r'Connection closed by .+ \[preauth\]',
        'E3': r'Did not receive identification string from',
        'E4': r'Disconnecting: Too many authentication failures for admin',
        'E5': r'Disconnecting: Too many authentication failures for root',
        'E6': r'error: Received disconnect from .+: .+: com\.jcraft\.jsch\.JSchException: Auth fail',
        'E7': r'error: Received disconnect from .+: .+: No more user authentication methods available',
        'E8': r'Failed none for invalid user .+ from .+ port .+ ssh2',
        'E9': r'Failed password for (?!invalid user).+ from .+ port .+ ssh2',
        'E10': r'Failed password for invalid user .+ from .+ port .+ ssh2',
        'E11': r'fatal: Write failed: Connection reset by peer',
        'E12': r'input_?userauth_?request: invalid user .+ \[preauth\]',
        'E13': r'Invalid user .+ from \d+\.\d+\.\d+\.\d+',
        'E14': r'message repeated .+ times: \[ Failed password for root',
        'E15': r'PAM \d+ more authentication failure;',
        'E16': r'PAM \d+ more authentication failures;',
        'E17': r'PAM \d+ more authentication failures;.*user=root',
        'E18': r'PAM service\(sshd\) ignoring max retries',
        'E19': r'pam_unix\(sshd:auth\): authentication failure;(?!.*user=)',
        'E20': r'pam_unix\(sshd:auth\): authentication failure;.*user=',
        'E21': r'pam_unix\(sshd:auth\): check pass; user unknown',
        'E22': r'pam_unix\(sshd:session\): session closed for user',
        'E23': r'pam_unix\(sshd:session\): session opened for user',
        'E24': r'Received disconnect from .+: \d+: Bye Bye \[preauth\]',
        'E25': r'Received disconnect from .+: \d+: Closed due to user request',
        'E26': r'Received disconnect from .+: \d+: disconnected by user',
        'E27': r'reverse mapping checking getaddrinfo for .+ \[.+\] failed - POSSIBLE BREAK-IN ATTEMPT!',
        'E28': r'fatal: Read from socket failed: Connection reset by peer',
        'E29': r'error: Received disconnect from .+: 13: User request',
        'E30': r'Disconnecting: Too many authentication failures for support \[preauth\]',
        'E31': r'Disconnecting: Too many authentication failures for pi \[preauth\]',
        'E32': r'Bad packet length \d+',
        'E33': r'Disconnecting: Packet corrupt',
        'E34': r'Address .+ maps to .+, but this does not map back to the address - POSSIBLE',
        'E35': r'Received disconnect from .+: 11:',
        'E36': r'Disconnecting: Too many authentication failures for user',
        'E37': r'fatal: no hostkey alg \[preauth\]',
        'E38': r'Bad protocol version identification .+ from .+ port',
        'E39': r'Invalid user .+ from \d+\.\d+\.\d+\.\d+ port',  # Variante avec "port"
        'E40': r'Failed none for invalid user .+ from .+ port .+ ssh2',  # Déjà E8 mais à vérifier
        'E41': r'Disconnecting: Too many authentication failures for supervisor', # ✅ Pattern GÉNÉRIQUE pour "Too many auth failures" (tous les users restants)
        'E42': r'Disconnecting: Too many authentication failures for \w+',
        'E43': r'error: Received disconnect from .+: 3: java\.net\.SocketTimeoutException',
        'E44': r'error: Received disconnect from .+: 3: com\.jcraft\.jsch\.JSchException: timeout',
        'E45': r'Failed none for invalid user\s+from \d+\.\d+\.\d+\.\d+ port \d+ ssh2',  # Sans nom
        'E46': r'Invalid user\s+from \d+\.\d+\.\d+\.\d+',  # Sans nom
        'E47': r'input_userauth_request:\s+invalid user\s+\[preauth\]',  # Sans nom 
        'E48': r'error: connect_to .+ port \d+: failed', # Erreurs de connexion
        'E49': r'Corrupted MAC on input\. \[preauth\]', # MAC corrompu
        'E50': r'error: Received disconnect from .+: 3: org\.vngx\.jsch\.userauth\.AuthCancelException', # Erreurs d'authentification (variantes Java)
        'E51': r'Server listening on .+ port \d+', # Messages système (démarrage serveur SSH)
        'E52': r'error: Received disconnect from .+: 13: Authentication cancelled',  #Authentication cancelled by user
        'E53': r'error: Received disconnect from .+: 3: com\.jcraft\.jsch\.JSchException: reject', # JSchException: reject HostKey
        'E54': r'error: Received disconnect from .+: 3: com\.jcraft\.jsch\.JSchException: Auth cancel', # JSchException: Auth cancel
        'E55': r'syslogin_perform_logout:', # Erreur de logout système

    }
    return event_patterns

def identify_event(message, event_patterns):
    """Identifie l'EventId correspondant au message"""
    priority_order = ['E27', 'E10', 'E9', 'E13', 'E20', 'E19', 'E17', 'E16', 'E15', 
                     'E7', 'E6', 'E5', 'E4', 'E24', 'E25', 'E26', 'E12', 'E1', 'E21']
    
    for event_id in priority_order:
        if event_id in event_patterns and re.search(event_patterns[event_id], message, re.IGNORECASE):
            return event_id
    
    for event_id, pattern in event_patterns.items():
        if event_id not in priority_order and re.search(pattern, message, re.IGNORECASE):
            return event_id
    
    return "UNKNOWN"

def extract_ip(message):
    """Extrait l'adresse IP source du message"""
    ip_patterns = [
        r'from\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
        r'rhost=?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
        r'\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]'
    ]
    
    for pattern in ip_patterns:
        match = re.search(pattern, message)
        if match:
            return match.group(1)
    return ""

def extract_user(message):
    """Extrait le nom d'utilisateur du message"""
    user_patterns = [
        r'for\s+invalid\s+user\s+(\S+)',
        r'for\s+user\s+(\S+)',
        r'for\s+(\w+)\s+from',
        r'user=(\S+)',
        r'invalid\s+user\s+(\S+)\s+\[preauth\]'
    ]
    
    for pattern in user_patterns:
        match = re.search(pattern, message)
        if match:
            return match.group(1)
    return ""

def smart_parse_ssh_log(line, event_patterns, previous_timestamp=None):
    """Parse avec détection automatique du changement d'année - VERSION UNIVERSELLE FINALE"""
    log_pattern = r'^(\w+\s+\d+\s+\d+:\d+:\d+)\s+(\S+)\s+sshd\[(\d+)\]:\s+(.*)$'
    match = re.match(log_pattern, line)
    
    if not match:
        return None, None
    
    timestamp_str, hostname, pid, message = match.groups()
    
    try:
        # Extraire le mois du log
        month_str = timestamp_str.split()[0]
        month_map = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        log_month = month_map.get(month_str, 1)
        
        # ✅ DÉTERMINATION DE L'ANNÉE
        if previous_timestamp is None:
            # Premier log : Logique basée sur le mois actuel
            current_year = datetime.now().year
            current_month_now = datetime.now().month
            
            # Si le mois du log est après le mois actuel, c'est l'année précédente
            if log_month > current_month_now:
                current_year = current_year - 1
        else:
            # Logs suivants : même année que le précédent par défaut
            current_year = previous_timestamp.year
        
        # Parser avec l'année déterminée
        timestamp = datetime.strptime(timestamp_str + f" {current_year}", "%b %d %H:%M:%S %Y")
        
        # ✅ DÉTECTION UNIVERSELLE DU CHANGEMENT D'ANNÉE
        if previous_timestamp is not None:
            time_diff = timestamp - previous_timestamp
            
            # Si on recule de plus de 300 jours (environ 10 mois), c'est un changement d'année
            # Exemple : 31 Dec → 1 Jan donne -365 jours, donc on incrémente l'année
            if time_diff.days < -300:
                timestamp = timestamp.replace(year=current_year + 1)
        
        timestamp_formatted = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        timestamp_formatted = timestamp_str
        timestamp = None
    
    event_id = identify_event(message, event_patterns)
    source_ip = extract_ip(message)
    user = extract_user(message)
    
    parsed_data = {
        'Timestamp': timestamp_formatted,
        'EventId': event_id,
        'SourceIP': source_ip,
        'User': user,
        'Raw_Message': message.strip()
    }
    
    return parsed_data, timestamp



def main():
    """Fonction principale du script ETL avec gestion intelligente des années"""
    input_file = 'data/SSH.txt'
    output_file = 'data/datasetssh.csv'
    
    print(f"[*] Chargement des templates...")
    event_patterns = load_templates()
    print(f"[+] {len(event_patterns)} templates chargés\n")
    
    print(f"[*] Traitement du fichier {input_file}...")
    results = []
    line_count = 0
    parsed_count = 0
    previous_timestamp = None
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                line_count += 1
                # ✅ CORRECTION : Seulement 2 valeurs retournées
                parsed, timestamp = smart_parse_ssh_log(line, event_patterns, previous_timestamp)
                
                if parsed:
                    results.append(parsed)
                    parsed_count += 1
                    previous_timestamp = timestamp
                
                if line_count % 500 == 0:
                    print(f"    Traité {line_count} lignes...")
    except FileNotFoundError:
        print(f"[ERREUR] Le fichier {input_file} n'a pas été trouvé!")
        return
    
    print(f"\n[+] Traitement terminé:")
    print(f"    - Total de lignes: {line_count}")
    print(f"    - Lignes parsées: {parsed_count}")
    if line_count > 0:
        print(f"    - Taux de succès: {(parsed_count/line_count)*100:.1f}%")
    
    if parsed_count == 0:
        print("\n[ATTENTION] Aucune donnée n'a été parsée!")
        return
    
    # Écrire le fichier CSV
    print(f"\n[*] Écriture du fichier {output_file}...")
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Timestamp', 'EventId', 'SourceIP', 'User', 'Raw_Message']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(results)
    
    print(f"[+] Fichier CSV créé avec succès: {output_file}")
    
    # Convertir en DataFrame pour les statistiques
    import pandas as pd
    df = pd.DataFrame(results)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # Statistiques des EventIds
    event_counts = df['EventId'].value_counts()
    
    print(f"\n[*] Top 10 des événements détectés:")
    for event_id, count in event_counts.head(10).items():
        print(f"    {event_id}: {count} occurrences")
    
    # IPs les plus actives
    ip_counts = df[df['SourceIP'].notna()]['SourceIP'].value_counts()
    
    if len(ip_counts) > 0:
        print(f"\n[*] Top 5 des IPs sources:")
        for ip, count in ip_counts.head(5).items():
            print(f"    {ip}: {count} tentatives")    # ================================================   
    # ANALYSE DES UNKNOWN
    # ================================================
    unknown_logs = df[df['EventId'] == 'UNKNOWN']
    
    if len(unknown_logs) > 0:
        print("\n" + "="*70)
        print(" " * 20 + "🔍 ANALYSE DES UNKNOWN")
        print("="*70)
        
        print(f"\n📊 STATISTIQUES")
        print(f"  • Total UNKNOWN          : {len(unknown_logs)} ({len(unknown_logs)/len(df)*100:.1f}%)")
        print(f"  • IPs sources uniques    : {unknown_logs['SourceIP'].nunique()}")
        
        # Messages les plus fréquents
        print(f"\n📋 MESSAGES TYPES (premiers 5 uniques) :\n")
        unique_messages = unknown_logs['Raw_Message'].unique()[:5]
        for i, msg in enumerate(unique_messages, 1):
            print(f"  {i}. {msg[:80]}...")
        
        # IPs sources
        print(f"\n🌐 TOP 3 IPS SOURCES DES UNKNOWN :")
        if unknown_logs['SourceIP'].notna().any():
            unknown_ips = unknown_logs[unknown_logs['SourceIP'].notna()]['SourceIP'].value_counts().head(3)
            for ip, count in unknown_ips.items():
                print(f"    • {ip}: {count} occurrences")
        else:
            print("    Aucune IP associée")
        
        print("="*70 + "\n")
    # ================================================
    # FIN ANALYSE DES UNKNOWN
    # ================================================
    
    # ✅ RAPPORT EXÉCUTIF (UNE SEULE FOIS)
    print("="*70)
    print(" " * 15 + "📋 RAPPORT EXÉCUTIF - ANALYSE SOC SSH")
    print("="*70)
    
    print(f"\n📊 STATISTIQUES GLOBALES")
    print(f"  • Total d'événements analysés    : {len(df):,}")
    print(f"  • Période d'analyse              : {df['Timestamp'].min()} → {df['Timestamp'].max()}")
    print(f"  • Durée totale                   : {(df['Timestamp'].max() - df['Timestamp'].min()).total_seconds() / 3600:.2f}h")
    print(f"  • IPs sources uniques            : {df['SourceIP'].nunique()}")
    print(f"  • Utilisateurs ciblés uniques    : {df['User'].nunique()}")
    print(f"  • Types d'événements détectés    : {df['EventId'].nunique()}")
    
    print(f"\n🚨 MENACES CRITIQUES")
    if len(ip_counts) > 0:
        top_ip = ip_counts.iloc[0]
        print(f"  • IP la plus agressive           : {ip_counts.index[0]} ({top_ip} attaques)")
    
    root_attacks = len(df[df['User'] == 'root'])
    print(f"  • Tentatives sur root            : {root_attacks}")
    
    if len(event_counts) > 0:
        print(f"  • Événement le plus fréquent     : {event_counts.index[0]} ({event_counts.iloc[0]} fois)")
    
    print(f"\n⚠️ NIVEAU DE MENACE               : 🔴 CRITIQUE")
    print("="*70)


if __name__ == "__main__":
    main()
