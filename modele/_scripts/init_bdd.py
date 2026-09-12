"""Création (et migration) de la base d'indexation 00_CONTEXTE/index.db.

Idempotent : peut être relancé sans danger. Les évolutions futures du schéma
s'appliquent par migrations successives pilotées par meta.version_schema.

Usage : python3 init_bdd.py
"""

from __future__ import annotations

import argparse
import sqlite3

import bdd
import sortie

VERSION_SCHEMA = 2

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
  cle    TEXT PRIMARY KEY,   -- version_kit, version_schema, racine, phase_installation, date_installation
  valeur TEXT
);

CREATE TABLE IF NOT EXISTS entites (
  id              INTEGER PRIMARY KEY,
  nom             TEXT NOT NULL UNIQUE,
  type            TEXT,               -- societe, sci, entreprise_individuelle, association, personnel
  forme_juridique TEXT,
  siren           TEXT,
  code_ape        TEXT,
  date_cloture    TEXT,               -- 'JJ-MM'
  regime_tva      TEXT,
  comptabilite    TEXT,               -- ex. "Cabinet X (interface Dougs)", "moi-même"
  actif           INTEGER NOT NULL DEFAULT 1,
  notes           TEXT
);

CREATE TABLE IF NOT EXISTS sources (
  id                INTEGER PRIMARY KEY,
  chemin            TEXT NOT NULL UNIQUE,
  type              TEXT,             -- local, onedrive, gdrive, dropbox, export_mail, scan_papier
  description       TEXT,
  exclu             INTEGER NOT NULL DEFAULT 0,   -- 1 = jamais lu par l'assistant
  statut            TEXT NOT NULL DEFAULT 'a_scanner',  -- a_scanner, scannee, indexee, migree
  nb_fichiers       INTEGER,
  date_dernier_scan TEXT
);

CREATE TABLE IF NOT EXISTS fichiers (
  id                          INTEGER PRIMARY KEY,
  chemin                      TEXT NOT NULL UNIQUE,  -- chemin actuel, absolu, normalisé NFC
  chemin_origine              TEXT,                  -- chemin avant migration (retour arrière possible)
  nom                         TEXT NOT NULL,
  extension                   TEXT,
  hash_sha256                 TEXT,
  taille                      INTEGER,
  date_modif_fichier          TEXT,
  date_premiere_detection     TEXT NOT NULL,
  date_derniere_verification  TEXT NOT NULL,
  date_indexation             TEXT,                  -- date de lecture du contenu
  contenu_lu                  INTEGER NOT NULL DEFAULT 0,
  niveau_confiance            TEXT,                  -- faible, moyen, eleve
  entite_id                   INTEGER REFERENCES entites(id),
  source_id                   INTEGER REFERENCES sources(id),
  date_document               TEXT,                  -- 'AAAA-MM-JJ', partiel toléré
  annee                       INTEGER,
  mois                        INTEGER,
  type_document               TEXT,                  -- achat, vente, releve, contrat, fiscal, social, paie...
  sous_type                   TEXT,
  emetteur                    TEXT,
  destinataire                TEXT,
  montant_ht                  REAL,
  montant_ttc                 REAL,
  devise                      TEXT DEFAULT 'EUR',
  resume                      TEXT,
  mots_cles                   TEXT,                  -- séparés par ;
  statut_classement           TEXT NOT NULL DEFAULT 'a_lire',
    -- a_lire, indexe, classe, general, a_valider, a_supprimer, corbeille, illisible, non_disponible
    -- general : document lu qui ne releve d'aucune structure et reste a sa place, sur decision de l'utilisateur
  supprime                    INTEGER NOT NULL DEFAULT 0,  -- 1 = disparu du disque (jamais effacé en base)
  date_suppression            TEXT,
  chemin_corbeille            TEXT,                  -- où le fichier a été déposé par corbeille.py
  qualification_par           TEXT,                  -- 'ia' ou 'humain'
  notes                       TEXT
);
CREATE INDEX IF NOT EXISTS idx_fichiers_hash   ON fichiers(hash_sha256);
CREATE INDEX IF NOT EXISTS idx_fichiers_entite ON fichiers(entite_id, annee, type_document);
CREATE INDEX IF NOT EXISTS idx_fichiers_statut ON fichiers(statut_classement);
CREATE INDEX IF NOT EXISTS idx_fichiers_suppr  ON fichiers(supprime);

CREATE TABLE IF NOT EXISTS fichiers_contenu (
  fichier_id      INTEGER PRIMARY KEY REFERENCES fichiers(id) ON DELETE CASCADE,
  texte           TEXT,               -- texte extrait (limité à ~50000 caractères)
  methode         TEXT,               -- lecture_ia, pdfplumber, python-docx, openpyxl...
  date_extraction TEXT
);

CREATE TABLE IF NOT EXISTS comptes_bancaires (
  id          INTEGER PRIMARY KEY,
  entite_id   INTEGER REFERENCES entites(id),
  banque      TEXT NOT NULL,
  iban_masque TEXT,                   -- 4 derniers caractères uniquement, jamais l'IBAN complet
  api         TEXT,                   -- 'qonto', 'aucune', 'a_verifier'... la clé vit HORS base et HORS racine
  actif       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS transactions (
  id                   INTEGER PRIMARY KEY,
  compte_id            INTEGER REFERENCES comptes_bancaires(id),
  reference_externe    TEXT UNIQUE,   -- identifiant côté banque : anti-doublon de synchronisation
  date_operation       TEXT,
  libelle              TEXT,
  montant              REAL,
  sens                 TEXT,          -- debit, credit
  fichier_id           INTEGER REFERENCES fichiers(id),   -- justificatif rapproché
  statut_rapprochement TEXT NOT NULL DEFAULT 'a_rapprocher'
    -- a_rapprocher, rapproche, incertain, sans_justificatif
);

CREATE TABLE IF NOT EXISTS echeances (
  id            INTEGER PRIMARY KEY,
  entite_id     INTEGER REFERENCES entites(id),
  type          TEXT,                 -- fiscal, social, juridique, bancaire, autre
  libelle       TEXT NOT NULL,
  date_echeance TEXT NOT NULL,        -- 'AAAA-MM-JJ'
  periodicite   TEXT,                 -- ponctuelle, mensuelle, trimestrielle, annuelle
  statut        TEXT NOT NULL DEFAULT 'a_venir',   -- a_venir, faite, depassee
  source        TEXT,                 -- 'document', 'enrichissement_legal', 'utilisateur'
  fichier_id    INTEGER REFERENCES fichiers(id),
  notes         TEXT
);

CREATE TABLE IF NOT EXISTS lots (
  id          INTEGER PRIMARY KEY,
  phase       TEXT,                   -- indexation, migration
  description TEXT,                   -- ex. "Source OneDrive / 2024"
  nb_fichiers INTEGER,
  nb_traites  INTEGER NOT NULL DEFAULT 0,
  statut      TEXT NOT NULL DEFAULT 'a_faire',   -- a_faire, en_cours, termine
  date_debut  TEXT,
  date_fin    TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS fichiers_fts USING fts5(
  nom, emetteur, destinataire, resume, mots_cles, notes,
  content='fichiers',
  content_rowid='id',
  tokenize='unicode61 remove_diacritics 2'
);

CREATE TRIGGER IF NOT EXISTS fichiers_fts_insert AFTER INSERT ON fichiers BEGIN
  INSERT INTO fichiers_fts(rowid, nom, emetteur, destinataire, resume, mots_cles, notes)
  VALUES (new.id, new.nom, new.emetteur, new.destinataire, new.resume, new.mots_cles, new.notes);
END;

CREATE TRIGGER IF NOT EXISTS fichiers_fts_delete AFTER DELETE ON fichiers BEGIN
  INSERT INTO fichiers_fts(fichiers_fts, rowid, nom, emetteur, destinataire, resume, mots_cles, notes)
  VALUES ('delete', old.id, old.nom, old.emetteur, old.destinataire, old.resume, old.mots_cles, old.notes);
END;

CREATE TRIGGER IF NOT EXISTS fichiers_fts_update AFTER UPDATE ON fichiers BEGIN
  INSERT INTO fichiers_fts(fichiers_fts, rowid, nom, emetteur, destinataire, resume, mots_cles, notes)
  VALUES ('delete', old.id, old.nom, old.emetteur, old.destinataire, old.resume, old.mots_cles, old.notes);
  INSERT INTO fichiers_fts(rowid, nom, emetteur, destinataire, resume, mots_cles, notes)
  VALUES (new.id, new.nom, new.emetteur, new.destinataire, new.resume, new.mots_cles, new.notes);
END;
"""

def colonne_existe(conn: sqlite3.Connection, table: str, colonne: str) -> bool:
    # Les noms de table et de colonne sont des constantes de ce fichier, jamais une saisie.
    return any(ligne["name"] == colonne for ligne in conn.execute(f"PRAGMA table_info({table})"))


def ajouter_colonne(conn: sqlite3.Connection, table: str, colonne: str, definition: str) -> None:
    """Ajout de colonne rejouable : ne fait rien si la colonne est déjà là."""
    if not colonne_existe(conn, table, colonne):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {colonne} {definition}")


def migration_2(conn: sqlite3.Connection) -> None:
    """Mémorise où corbeille.py a déposé un document, pour pouvoir le remettre en place."""
    ajouter_colonne(conn, "fichiers", "chemin_corbeille", "TEXT")


# Migrations successives, chacune rejouable sans danger.
MIGRATIONS = {2: [migration_2]}


def main(argv: list[str] | None = None) -> None:
    # `argv` reste None en ligne de commande (argparse lit alors sys.argv) ;
    # un appelant Python passe [] pour que les arguments du programme hôte,
    # un lanceur de tests par exemple, ne soient pas pris pour les siens.
    sortie.configurer()
    argparse.ArgumentParser(
        description="Crée la base 00_CONTEXTE/index.db (ou applique les migrations de schéma si elle existe)."
    ).parse_args(argv)
    creation = not bdd.CHEMIN_BDD.exists()
    conn = bdd.connexion(creer=True)
    # executescript() valide la transaction en cours : jamais dans un bloc `with conn`.
    conn.executescript(SCHEMA)
    conn.commit()
    with conn:
        if creation:
            bdd.meta_ecrire(conn, "version_schema", str(VERSION_SCHEMA))
            bdd.meta_ecrire(conn, "date_installation", bdd.maintenant())
        else:
            version = int(bdd.meta_lire(conn, "version_schema") or "1")
            for cible in sorted(v for v in MIGRATIONS if v > version):
                for etape in MIGRATIONS[cible]:
                    etape(conn)
                bdd.meta_ecrire(conn, "version_schema", str(cible))
                print(f"Migration de schéma appliquée : version {cible}")
    etat = "créée" if creation else "vérifiée (déjà en place)"
    print(f"Base {etat} : {bdd.CHEMIN_BDD}")
    conn.close()


if __name__ == "__main__":
    main()
