# codesys-builder

Strumento di automazione per la compilazione di applicazioni CODESYS PLC da repository SVN. Avvia il CODESYS IDE in modalità headless, esegue il checkout del sorgente, compila il progetto e genera il boot application pronto per il deploy sul PLC.

## Funzionamento

```
python main.py
```

Il flusso di esecuzione è il seguente:

1. Scansiona la directory di installazione CODESYS per rilevare i profili disponibili
2. Propone una selezione interattiva del profilo se ne sono presenti più di uno
3. Esegue il checkout del progetto dal repository SVN nella directory `repos/`
4. Avvia CODESYS in modalità `--noUI` con lo script di build `codesys_build.py`
5. Compila l'applicazione e genera il boot application (`.app`)
6. Riporta l'esito della build con gli eventuali errori

## Output

Gli artefatti generati vengono salvati nella directory `output/`:

| File | Descrizione |
|------|-------------|
| `Application.app` | Boot application compilata da caricare sul PLC |
| `Application.crc` | Checksum CRC del file `.app` |

## Requisiti

- **Windows 10/11**
- **CODESYS IDE 3.5.17.30** installato in `C:\Program Files\CODESYS 3.5.17.30\`
- **Python 3.x** (solo libreria standard, nessuna dipendenza esterna)
- Accesso al repository SVN configurato in `main.py`

## Configurazione

I parametri di build sono definiti direttamente in [main.py](main.py):

| Parametro | Descrizione |
|-----------|-------------|
| `SVN_URL` | URL del repository SVN contenente il progetto CODESYS |
| `REPO_DIR` | Directory locale per il checkout SVN (`./repos/`) |
| `OUTPUT_DIR` | Directory di destinazione degli artefatti (`./output/`) |
| `PROJECT_NAME` | Nome del progetto CODESYS |
| `SVN_USER` / `SVN_PASS` | Credenziali SVN (opzionali) |
| `CODESYS_EXE` | Percorso dell'eseguibile CODESYS |

## Struttura del progetto

```
codesys-builder/
├── main.py            # Entry point: orchestrazione del processo di build
├── codesys_build.py   # Script eseguito da CODESYS in modalità headless
├── repos/             # Cache del checkout SVN (ignorata da git)
└── output/            # Artefatti generati dalla build (ignorati da git)
```

## Come funziona l'integrazione con CODESYS

`main.py` costruisce ed esegue il seguente comando:

```
CODESYS.exe --noUI --profile=<profilo> --runscript=codesys_build.py --scriptargs="<parametri>"
```

`codesys_build.py` viene eseguito internamente dal motore di scripting CODESYS e riceve i parametri via `--scriptargs`. Si occupa di: checkout SVN, apertura del progetto, compilazione e generazione del boot application.
