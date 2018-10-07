# Important note / Note importante
(EN) This is an exploratory and experimental open project. The project is currently in development and all the material on this page
should be considered as part of work in progress. / (FR) Ce projet ouvert est exploratoire et expérimental. Le
projet est en cours de développement et tout le contenu de cette page doit être considéré comme faisant partie des travaux en cours.

# OpenBusinessRepository

The OpenBusinessRepository (OBR) is a repository of businesses micro-records from open data sources. It includes only data or information that is available to the public on the Internet under an open data license. The management and progression of the project is openly available as well at [taiga.io - OpenBusinessRepository](https://tree.taiga.io/project/virtualtorus-openbusinessrepository/).

OpenBusinessRepository (OBR) est un répertoire de micro-enregistrements d'entreprises développé à partir de sources de données ouvertes. Il ne comprend que des données ou des informations accessibles au public sur Internet sous une licence de données ouvertes. La gestion et la progression du projet sont également disponibles sur taiga.io

## Open data contribution / Contribution aux données ouvertes

The repository already contains a source file section and `sources.csv` for existing open data and points of reference to those data. In the future development of the project, one option will be to host the processed and cleaned data on a server for the public to download. You can contribute to the OBR, with data available under an open data license. This can be done by referring us to data we do not have on the list or communicating with us directly if you are a group that maintains business micro data. The best way to add new business data is to write a source file for it (see documentation references below).

Le répertoire contient déjà une section de fichiers sources et `sources.csv` pour les données ouvertes existantes et les points de référence à ces données. Dans le développement futur du projet, une option sera d’héberger les données traitées et nettoyées sur un serveur pour que le public puisse les télécharger. Vous pouvez contribuer à l'OBR avec des données disponibles sous une licence de données ouvertes. Cela peut être fait en nous référant aux données que nous n'avons pas sur la liste ou en communiquant directement avec nous si vous êtes un groupe qui gère des microdonnées d'entreprise. La meilleure façon d'ajouter de nouvelles données d'entreprise consiste à y écrire un fichier source (voir les références de la documentation ci-dessous).

## Installation / Installation

The host of the OBR must be a Linux-based operating system, so packages such as `coreutils` are (often) included by default. To start, simply clone the repository:

```bash
$ git clone https://github.com/CSBP-CPSE/OpenBusinessRepository
```
Then execute the `obr-init.py` script to create the data processing directories.

To operate the data processing, which is managed by the `pdctl.py` script, you will need to install:
- Python (version 3.5+)
- [libpostal](https://github.com/openvenues/libpostal)
- [pypostal](https://github.com/openvenues/pypostal)

## Help / Aide

#### Interactive script and code

Assuming you are in the cloned directory, run 

```shell
$ python tools/obrpdctl.py --help
```

which should print to standard output:

```
usage: obrpdctl.py [-h] [-p] [-u] [-j N] [--log FILE] SOURCE [SOURCE ...]

A command-line interactive tool with the OBR.

positional arguments:
  SOURCE             path to source file

optional arguments:
  -h, --help         show this help message and exit
  -p, --ignore-proc  check source files without processing data
  -u, --ignore-url   ignore "url" entries from source files
  -j N, --jobs N     run at most N jobs asynchronously
  --log FILE         log output to FILE
```

#### Documentation

In the `docs` folder there is documentation on how to write source files, a primer to operate the system, and so forth.

- `CONTRIB.md` : A manual describing the features and options when writing a source file. For source file examples, see `sources`.
- `SCHEME.md` : A summary of the production system and its features.
- `FAQ.md` : Frequently asked questions page.
- `SCRIPTS.md` : N/A.

The code of the OBR has been commented and documented. If you are interested in developing or inspecting, keep in mind that the OBR is an exploratory project and all the codes and documentation are work in progress. 

## Issues / Problèmes

You can post questions, enhancement requests, and bugs in [Issues](https://github.com/CSBP-CPSE/OpenBusinessRepository/issues).
