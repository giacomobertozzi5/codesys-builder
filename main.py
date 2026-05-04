import subprocess
import os
import json
import getpass
from cryptography.fernet import Fernet

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SVN_CONFIG_FILE = os.path.join(SCRIPT_DIR, "svn.json")
SVN_KEY_FILE    = os.path.join(SCRIPT_DIR, "svn.key")
REPO_DIR        = os.path.join(SCRIPT_DIR, "repos")
OUTPUT_DIR      = os.path.join(SCRIPT_DIR, "output")
PROJECT_NAME    = "release"
CODESYS_EXE     = r"C:\Program Files\CODESYS 3.5.17.30\CODESYS\Common\CODESYS.exe"
BUILD_SCRIPT    = os.path.join(SCRIPT_DIR, "codesys_build.py")


def load_key() -> Fernet:
    if os.path.exists(SVN_KEY_FILE):
        with open(SVN_KEY_FILE, "rb") as f:
            return Fernet(f.read())
    key = Fernet.generate_key()
    with open(SVN_KEY_FILE, "wb") as f:
        f.write(key)
    return Fernet(key)


def load_svn_config() -> tuple:
    fernet = load_key()
    if os.path.exists(SVN_CONFIG_FILE):
        with open(SVN_CONFIG_FILE, "r") as f:
            cfg = json.load(f)
        password = fernet.decrypt(cfg["password"].encode()).decode()
        return cfg["url"], cfg["user"], password

    print("File svn.json non trovato. Inserisci le credenziali SVN:")
    url      = input("  URL:      ").strip()
    user     = input("  Utente:   ").strip()
    password = getpass.getpass("  Password: ")

    cfg = {
        "url":      url,
        "user":     user,
        "password": fernet.encrypt(password.encode()).decode()
    }
    with open(SVN_CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"Credenziali salvate in {SVN_CONFIG_FILE} (password cifrata).")
    return url, user, password


def select_profile() -> str:
    profile_dir = os.path.join(os.path.dirname(os.path.dirname(CODESYS_EXE)), "Profiles")
    if not os.path.isdir(profile_dir):
        raise RuntimeError(f"Cartella profili non trovata: {profile_dir}")
    profiles = [
        f.replace(".profile.xml", "")
        for f in os.listdir(profile_dir)
        if f.endswith(".profile.xml")
    ]
    if not profiles:
        raise RuntimeError(f"Nessun profilo trovato in {profile_dir}")
    if len(profiles) == 1:
        print(f"Profilo trovato: {profiles[0]}")
        return profiles[0]
    print("Profili CODESYS disponibili:")
    for i, p in enumerate(profiles, 1):
        print(f"  {i}) {p}")
    while True:
        choice = input(f"Scegli un profilo [1-{len(profiles)}]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(profiles):
            return profiles[int(choice) - 1]
        print("Scelta non valida, riprova.")


# 1. Carica config SVN
SVN_URL, SVN_USER, SVN_PASS = load_svn_config()

# 2. Seleziona profilo
profile = select_profile()

# 3. Avvia CODESYS in modalità headless con script di build
cmd = (
    f'"{CODESYS_EXE}" --noUI --profile="{profile}"'
    f' --runscript="{BUILD_SCRIPT}"'
    f' --scriptargs="{SVN_URL}|{REPO_DIR}|{PROJECT_NAME}|{SVN_USER}|{SVN_PASS}|{OUTPUT_DIR}"'
)
print(f"Comando: {cmd}")
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        text=True, shell=True)
output_lines = []
for line in proc.stdout:
    print(line, end="")
    output_lines.append(line)
proc.wait()

if proc.returncode != 0:
    raise RuntimeError("Build fallita:\n" + "".join(output_lines))

build_errors = [l for l in output_lines if "Build: Error:" in l]
if build_errors:
    raise RuntimeError("Errori di compilazione:\n" + "".join(build_errors))
