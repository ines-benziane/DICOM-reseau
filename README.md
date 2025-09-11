##### PRESENTATION #####
Le but est de créer un CLI (interface ligne de commande) qui va :
    - se connecter à Télémis 
    - récupérer les images DICOM souhaitées 

##### NOTES ####
Ce projet est codé comme un SCU (il demande les images) et comme un SCP à la fois (il reçoit la demande de stockage pour les images demandées). On doit préciser son role de scp (role_a dans dicom). 

##### CONTRAINTES #####
On ne doit pas récupérer le nom des patients

##### ARCHITECTURE IN PROGRESS ######

Le projet suit une architecture client/server
Architecture modulaire
Le server est le logicielle Telemis
Respect de la séparation des responsabilités
Responsabilité distinctes mais collaboration = favoriser composition sur héritage
Respect des principes SOLID


dicom_client/
├── config/
│   ├── __init__.py
│   └── server_config.py      # Configuration TELEMIS 
├── core/
│   ├── __init__.py
│   ├── dicom_client.py       # Client principal (envoi des requêtes)
│   ├── query_builder.py      # Construction des requêtes
│   └── image_handler.py      # Gestion des images
├── utils/
│   ├── __init__.py
│   ├── logger.py            # Système de logs
│   └── validators.py        # Validation des données
├── interface/
│   ├── __init__.py
│   └── cli.py              # Interface ligne de commande
├── tests/
│   ├── __init__.py
│   └── test_connection.py   # Tests de base (test automatisés?)
├── main.py                  # Point d'entrée
├── requirements.txt         # Dépendances (Installation : pip install -r requirements.txt)
└── README.md               # Documentation

#### LANGAGES ET PACKAGES ######
python 3.12
pydicom
pynetdicom 