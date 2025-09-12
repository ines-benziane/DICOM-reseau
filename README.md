##### PRESENTATION #####
Le but est de créer un CLI (interface ligne de commande) qui va :
    - se connecter à Télémis 
    - récupérer les images DICOM souhaitées 

##### NOTES ####
Ce projet est codé comme un SCU (il demande les images) et comme un SCP à la fois (il reçoit la demande de stockage pour les images demandées). On doit préciser son role de scp (role_a dans dicom). **The key insight**: When you perform a C-GET operation in pynetdicom, your client must act as both a requester (C-GET SCU) and a receiver (C-STORE SCP) because DICOM's C-GET operation involves **role reversal within the same association**. The server that receives your C-GET request switches roles to become a C-STORE client that sends the actual data back to you. [PyPI +3](https://pypi.org/project/pynetdicom/); The client that requested the data must also handle receiving it through C-STORE operations over the same network connection.

This design pattern eliminates the need for multiple network connections and simplifies firewall configuration, but requires clients to implement dual functionality. Understanding this relationship is crucial for successful DICOM implementations.

##### CONTRAINTES #####
On ne doit pas récupérer le nom des patients
### Protocol requirements

The DICOM standard mandates that **"The C-STORE Sub-operations shall be accomplished on the same Association as the C-GET operation. Hence, the SCP of the Query/Retrieve Service Class serves as the SCU of the Storage Service Class."** [github +5](https://pydicom.github.io/pynetdicom/stable/examples/qr_get.html)

This means your client application must:

- **Negotiate dual contexts**: Both for sending C-GET requests AND receiving various storage types
- **Implement role selection**: Indicate SCP capability for Storage SOP Classes
- **Handle storage operations**: Process incoming C-STORE requests and manage received data
- **Provide storage responses**: Return success/failure status for each received instance

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