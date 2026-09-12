"""Tests des scripts du kit. Bibliotheque standard uniquement, Python 3.9+.

Chaque test reproduit un constat d'audit : il echoue sur le code d'avant le
correctif et passe apres. Rien n'est ecrit hors d'un dossier temporaire, et
aucune corbeille systeme reelle n'est sollicitee.

Usage : python3 -m unittest tests_scripts        (depuis le dossier _scripts)
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

DOSSIER_SCRIPTS = Path(__file__).resolve().parent
RACINE_DEPOT = DOSSIER_SCRIPTS.parent.parent
for _chemin in (str(DOSSIER_SCRIPTS), str(RACINE_DEPOT)):
    if _chemin not in sys.path:
        sys.path.insert(0, _chemin)

import bdd  # noqa: E402
import corbeille  # noqa: E402
import init_bdd  # noqa: E402
import manifeste  # noqa: E402
import scan  # noqa: E402


def sans_bruit(fonction, *args, **kwargs):
    """Execute une fonction en avalant sa sortie console, et la renvoie."""
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        fonction(*args, **kwargs)
    return tampon.getvalue()


class BaseTemporaire(unittest.TestCase):
    """Racine documentaire jetable, avec sa base initialisee."""

    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="kit-tests-")).resolve()
        self.racine = self.dossier / "racine"
        # racine documentaire realiste : les scripts vivent dans 00_CONTEXTE/_scripts,
        # donc les sous-processus retrouvent seuls la base et la racine.
        self.scripts = self.racine / "00_CONTEXTE" / "_scripts"
        shutil.copytree(DOSSIER_SCRIPTS, self.scripts,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        self._bdd_origine = bdd.CHEMIN_BDD
        bdd.CHEMIN_BDD = self.racine / "00_CONTEXTE" / "index.db"
        sans_bruit(init_bdd.main)
        self.conn = bdd.connexion()
        bdd.meta_ecrire(self.conn, "racine", str(self.racine))
        self.conn.commit()

    def lancer_script(self, nom, *arguments):
        # HOME est detourne vers le dossier temporaire : meme en cas de regression,
        # aucun test ne peut atteindre la vraie corbeille du poste.
        return subprocess.run(
            [sys.executable, str(self.scripts / nom), *arguments],
            capture_output=True, text=True, timeout=120,
            env=dict(os.environ, HOME=str(self.dossier), XDG_DATA_HOME=str(self.dossier / "xdg")),
        )

    def tearDown(self):
        self.conn.close()
        bdd.CHEMIN_BDD = self._bdd_origine
        shutil.rmtree(self.dossier, ignore_errors=True)

    def dossier_docs(self, nom="docs", fichiers=("a.pdf",)):
        cible = self.racine / nom
        cible.mkdir(parents=True, exist_ok=True)
        for fichier in fichiers:
            (cible / fichier).write_text("contenu " + fichier, encoding="utf-8")
        return cible

    def chemins_en_base(self):
        return {ligne["chemin"] for ligne in self.conn.execute("SELECT chemin FROM fichiers")}


class TestScanRobustesse(BaseTemporaire):

    def test_fichier_a_trous_ne_plante_pas(self):
        """os.getxattr n'existe pas sur macOS : le scan plantait au premier fichier
        annonce a zero bloc (iCloud, OneDrive, fichier a trous)."""
        creux = self.racine / "creux.bin"
        creux.parent.mkdir(parents=True, exist_ok=True)
        with open(creux, "wb") as flux:
            flux.truncate(5 * 1024 * 1024)
        etat = creux.stat()
        if etat.st_blocks != 0:
            self.skipTest("le systeme de fichiers n'a pas cree de fichier a trous")
        self.assertTrue(scan.est_stub_cloud(creux, etat))

    def test_fichier_illisible_et_lien_casse_nx_arretent_pas_le_scan(self):
        source = self.dossier_docs("docs", ("bon1.pdf", "illisible.pdf", "bon2.pdf"))
        illisible = source / "illisible.pdf"
        os.chmod(illisible, 0o000)
        os.symlink(str(source / "nulle-part.pdf"), str(source / "casse.pdf"))
        if os.access(illisible, os.R_OK):
            self.skipTest("les droits POSIX ne sont pas appliques ici (utilisateur privilegie)")

        sortie = sans_bruit(scan.scanner_source, self.conn, bdd.normaliser(source))

        indexes = {Path(c).name for c in self.chemins_en_base()}
        self.assertIn("bon1.pdf", indexes)
        self.assertIn("bon2.pdf", indexes)
        self.assertNotIn("casse.pdf", indexes)
        self.assertIn("illisibles ou en erreur : 1", sortie)
        self.assertIn("liens symboliques ignorés : 1", sortie)
        os.chmod(illisible, 0o644)   # avant le menage du dossier temporaire

    def test_lien_symbolique_de_dossier_jamais_suivi(self):
        source = self.dossier_docs("docs", ("a.pdf",))
        dehors = self.dossier / "dehors"
        dehors.mkdir()
        (dehors / "secret.pdf").write_text("hors perimetre", encoding="utf-8")
        os.symlink(str(dehors), str(source / "raccourci"))

        sans_bruit(scan.scanner_source, self.conn, bdd.normaliser(source))

        self.assertNotIn("secret.pdf", {Path(c).name for c in self.chemins_en_base()})

    def test_readme_du_kit_et_dossier_transmission_ignores(self):
        source = self.dossier_docs("docs", ("a.pdf",))
        (source / "a_trier").mkdir()
        (source / "a_trier" / "README.md").write_text("mode d'emploi du kit", encoding="utf-8")
        (source / "readme.md").write_text("notes de l'utilisateur", encoding="utf-8")
        transmission = source / "transmission_2026-09"
        transmission.mkdir()
        (transmission / "copie.pdf").write_text("copie pour le comptable", encoding="utf-8")
        for dossier in (".gemini/commands", ".agents/skills/indexer"):
            (source / dossier).mkdir(parents=True)
        (source / ".gemini/commands/indexer.toml").write_text('prompt = "x"', encoding="utf-8")
        (source / ".agents/skills/indexer/SKILL.md").write_text("---\nname: indexer\n---", encoding="utf-8")

        sans_bruit(scan.scanner_source, self.conn, bdd.normaliser(source))

        noms = {Path(c).name for c in self.chemins_en_base()}
        self.assertEqual({"a.pdf", "readme.md"}, noms,
                         "seul le README du kit dans un dossier de travail est ignore ; "
                         "un readme de l'utilisateur ailleurs est un document")

    def test_document_restaure_depuis_la_corbeille_redevient_a_lire(self):
        source = self.dossier_docs("docs", ("f1.pdf",))
        chemin = bdd.normaliser(source / "f1.pdf")
        sans_bruit(scan.scanner_source, self.conn, bdd.normaliser(source))
        self.conn.execute(
            "UPDATE fichiers SET supprime = 1, statut_classement = 'corbeille',"
            " chemin_corbeille = '/x/_corbeille/2026-09-10/f1.pdf' WHERE chemin = ?", (chemin,))
        self.conn.commit()

        sans_bruit(scan.scanner_source, self.conn, bdd.normaliser(source))

        ligne = self.conn.execute(
            "SELECT supprime, statut_classement, chemin_corbeille FROM fichiers WHERE chemin = ?",
            (chemin,)).fetchone()
        self.assertEqual((0, "a_lire", None), tuple(ligne))


class TestScanExclusions(BaseTemporaire):

    def declarer_source(self, chemin, exclu=0):
        self.conn.execute("INSERT INTO sources (chemin, exclu) VALUES (?, ?)", (str(chemin), exclu))
        self.conn.commit()

    def test_prefixe_like_avec_souligne_ne_marque_pas_les_voisins(self):
        """Sans ESCAPE, le prefixe « a_b/ » d'un LIKE attrape aussi « axb/ »
        et declare disparus des fichiers d'une autre source, bien presents."""
        cible = self.dossier_docs("a_b", ("dedans.pdf",))
        voisin = self.dossier_docs("axb", ("voisin.pdf",))
        chemin_voisin = bdd.normaliser(voisin / "voisin.pdf")
        quand = bdd.maintenant()
        self.conn.execute(
            "INSERT INTO fichiers (chemin, nom, date_premiere_detection, date_derniere_verification)"
            " VALUES (?, ?, ?, ?)",
            (chemin_voisin, "voisin.pdf", quand, quand),
        )
        self.conn.commit()

        sans_bruit(scan.scanner_source, self.conn, bdd.normaliser(cible))

        etat = self.conn.execute(
            "SELECT supprime FROM fichiers WHERE chemin = ?", (chemin_voisin,)
        ).fetchone()
        self.assertEqual(0, etat["supprime"])

    def test_sous_dossier_d_une_source_exclue_est_refuse(self):
        prive = self.dossier_docs("prive", ("intime.pdf",))
        sous = prive / "sous"
        sous.mkdir()
        (sous / "intime2.pdf").write_text("prive", encoding="utf-8")
        self.declarer_source(bdd.normaliser(prive), exclu=1)

        sortie = sans_bruit(scan.scanner_source, self.conn, bdd.normaliser(sous))

        self.assertIn("exclue", sortie)
        self.assertEqual(set(), self.chemins_en_base())
        nb_sources = self.conn.execute("SELECT COUNT(*) AS n FROM sources").fetchone()["n"]
        self.assertEqual(1, nb_sources)

    def test_source_declaree_avec_separateur_final(self):
        prive = self.dossier_docs("prive", ("intime.pdf",))
        self.declarer_source(str(bdd.normaliser(prive)) + os.sep, exclu=1)

        sortie = sans_bruit(scan.scanner_source, self.conn, bdd.normaliser(prive))

        self.assertIn("exclue", sortie)
        nb_sources = self.conn.execute("SELECT COUNT(*) AS n FROM sources").fetchone()["n"]
        self.assertEqual(1, nb_sources, "un separateur final ne doit pas creer une source en double")


class TestScanLigneDeCommande(BaseTemporaire):
    """Tests par sous-processus : ils verifient le comportement reel du script."""

    def lancer(self, *arguments):
        return self.lancer_script("scan.py", *arguments)

    def test_help_ne_cree_pas_de_source_fantome(self):
        resultat = self.lancer("--help")
        self.assertEqual(0, resultat.returncode, resultat.stderr)
        self.assertIn("--toutes", resultat.stdout)
        nb_sources = self.conn.execute("SELECT COUNT(*) AS n FROM sources").fetchone()["n"]
        self.assertEqual(0, nb_sources)

    def test_toutes_continue_apres_une_source_introuvable(self):
        presente = self.dossier_docs("docs", ("a.pdf",))
        absente = self.racine / "disparue"
        self.conn.execute("INSERT INTO sources (chemin) VALUES (?)", (bdd.normaliser(absente),))
        self.conn.execute("INSERT INTO sources (chemin) VALUES (?)", (bdd.normaliser(presente),))
        self.conn.commit()

        resultat = self.lancer("--toutes")

        self.assertEqual(0, resultat.returncode, resultat.stderr)
        self.assertIn("introuvable", resultat.stdout)
        noms = {Path(c).name for c in self.chemins_en_base()}
        self.assertIn("a.pdf", noms, "la source suivante doit avoir ete scannee malgre l'absente")

    def test_sortie_console_sur_terminal_cp1252(self):
        self.dossier_docs("docs", ("facture-recu-ete.pdf",))
        environnement = dict(os.environ, PYTHONIOENCODING="cp1252")
        resultat = subprocess.run(
            [sys.executable, str(self.scripts / "scan.py"), str(self.racine / "docs")],
            capture_output=True, text=True, timeout=120, env=environnement,
        )
        self.assertEqual(0, resultat.returncode, resultat.stderr)
        self.assertIn("modifi", resultat.stdout)
        self.assertNotIn("UnicodeEncodeError", resultat.stderr)


class TestCorbeille(BaseTemporaire):

    def lancer(self, *arguments):
        return self.lancer_script("corbeille.py", *arguments)

    def test_refuse_un_lien_symbolique(self):
        source = self.dossier_docs("docs", ("vrai.pdf",))
        lien = source / "lien.pdf"
        os.symlink(str(source / "vrai.pdf"), str(lien))

        resultat = self.lancer("--interne", str(lien))

        self.assertEqual(1, resultat.returncode)
        self.assertIn("ECHEC", resultat.stdout)
        self.assertIn("lien symbolique", resultat.stdout)
        self.assertTrue(lien.is_symlink(), "le lien doit rester en place")
        self.assertTrue((source / "vrai.pdf").exists(), "la cible ne doit pas etre touchee")

    def test_refuse_un_chemin_hors_racine(self):
        dehors = self.dossier / "dehors"
        dehors.mkdir()
        etranger = dehors / "etranger.pdf"
        etranger.write_text("hors perimetre", encoding="utf-8")

        resultat = self.lancer("--interne", str(etranger))

        self.assertEqual(1, resultat.returncode)
        self.assertIn("hors du dossier", resultat.stdout)
        self.assertTrue(etranger.exists())

    def test_accepte_une_source_declaree_hors_racine_mais_pas_une_source_exclue(self):
        cloud = self.dossier / "cloud"
        prive = self.dossier / "prive"
        cloud.mkdir()
        prive.mkdir()
        (cloud / "doublon.pdf").write_text("source declaree", encoding="utf-8")
        (prive / "secret.pdf").write_text("source exclue", encoding="utf-8")
        self.conn.execute("INSERT INTO sources (chemin, exclu) VALUES (?, 0)", (bdd.normaliser(cloud),))
        self.conn.execute("INSERT INTO sources (chemin, exclu) VALUES (?, 1)", (bdd.normaliser(prive),))
        self.conn.commit()

        accepte = self.lancer("--interne", str(cloud / "doublon.pdf"))
        refuse = self.lancer("--interne", str(prive / "secret.pdf"))

        self.assertEqual(0, accepte.returncode, accepte.stdout)
        self.assertFalse((cloud / "doublon.pdf").exists())
        self.assertEqual(1, refuse.returncode)
        self.assertTrue((prive / "secret.pdf").exists())

    def test_corbeille_interne_sans_ecrasement_et_base_mise_a_jour(self):
        premier = self.dossier_docs("docs", ("doublon.pdf",)) / "doublon.pdf"
        second_dossier = self.dossier_docs("archives", ())
        second = second_dossier / "doublon.pdf"
        second.write_text("autre contenu", encoding="utf-8")
        quand = bdd.maintenant()
        for chemin in (premier, second):
            self.conn.execute(
                "INSERT INTO fichiers (chemin, nom, date_premiere_detection, date_derniere_verification)"
                " VALUES (?, ?, ?, ?)",
                (bdd.normaliser(chemin), chemin.name, quand, quand),
            )
        self.conn.commit()

        resultat = self.lancer("--interne", str(premier), str(second))

        self.assertEqual(0, resultat.returncode, resultat.stdout + resultat.stderr)
        self.assertIn("corbeille interne", resultat.stdout)
        self.assertFalse(premier.exists())
        self.assertFalse(second.exists())
        deposes = sorted(p.name for p in (self.racine / "_corbeille").rglob("*.pdf"))
        self.assertEqual(["doublon (1).pdf", "doublon.pdf"], deposes)
        self.assertEqual({"autre contenu", "contenu doublon.pdf"},
                         {p.read_text(encoding="utf-8") for p in (self.racine / "_corbeille").rglob("*.pdf")})

        lignes = self.conn.execute(
            "SELECT chemin, supprime, statut_classement, date_suppression, chemin_corbeille FROM fichiers"
        ).fetchall()
        self.assertEqual(2, len(lignes))
        for ligne in lignes:
            self.assertEqual(1, ligne["supprime"])
            self.assertEqual("corbeille", ligne["statut_classement"])
            self.assertTrue(ligne["date_suppression"])
            self.assertTrue(ligne["chemin_corbeille"])
            self.assertTrue(Path(ligne["chemin_corbeille"]).exists())

    def test_readme_de_la_corbeille_identique_a_celui_du_depot(self):
        modele = RACINE_DEPOT / "arborescence" / "_corbeille" / "README.md"
        self.assertTrue(modele.exists(), "le README de la corbeille manque dans arborescence/")
        self.assertEqual(modele.read_text(encoding="utf-8"), corbeille.README_CORBEILLE)


class TestVerifier(BaseTemporaire):

    def lancer(self):
        return self.lancer_script("verifier.py")

    def inscrire(self, chemin, **colonnes):
        quand = bdd.maintenant()
        colonnes.setdefault("nom", Path(chemin).name)
        champs = ", ".join(["chemin", "date_premiere_detection", "date_derniere_verification"] + list(colonnes))
        trous = ", ".join("?" * (3 + len(colonnes)))
        self.conn.execute(
            f"INSERT INTO fichiers ({champs}) VALUES ({trous})",
            (str(chemin), quand, quand, *colonnes.values()),
        )
        self.conn.commit()

    def test_un_fichier_en_corbeille_n_est_pas_signale_absent(self):
        self.inscrire(self.racine / "docs" / "parti.pdf",
                      statut_classement="corbeille", supprime=1)
        resultat = self.lancer()
        self.assertEqual(0, resultat.returncode, resultat.stdout)
        self.assertNotIn("absent :", resultat.stdout)

    def test_heuristique_a_trier_limitee_au_segment_de_chemin(self):
        """« societe_a_trier_2024 » n'est pas un dossier a_trier : pas d'anomalie."""
        piege = self.dossier_docs("societe_a_trier_2024", ("classe.pdf",)) / "classe.pdf"
        self.inscrire(piege, statut_classement="classe", contenu_lu=1,
                      resume="ok", type_document="achat", entite_id=None)
        resultat = self.lancer()
        self.assertNotIn("societe_a_trier_2024", resultat.stdout.split("--- Statuts")[-1])

    def test_document_general_sans_structure_n_est_pas_une_fiche_incomplete(self):
        """Un document « general » n'a volontairement aucune structure : pas d'anomalie."""
        note = self.dossier_docs("docs", ("note.txt",)) / "note.txt"
        self.inscrire(note, statut_classement="general", contenu_lu=1,
                      resume="note de reunion", type_document="note", entite_id=None)
        resultat = self.lancer()
        self.assertEqual(0, resultat.returncode, resultat.stdout)
        self.assertNotIn("note.txt", resultat.stdout)

    def test_document_indexe_sans_structure_reste_signale(self):
        """Non-regression : sans decision de l'utilisateur, l'absence de structure reste un oubli."""
        note = self.dossier_docs("docs", ("oubli.txt",)) / "oubli.txt"
        self.inscrire(note, statut_classement="indexe", contenu_lu=1,
                      resume="note", type_document="note", entite_id=None)
        resultat = self.lancer()
        self.assertIn("oubli.txt", resultat.stdout)
        self.assertEqual(1, resultat.returncode)

    def test_document_general_dans_un_dossier_de_transit_reste_signale(self):
        """Un dossier de depot n'est pas une destination, meme pour un document general."""
        note = self.dossier_docs("a_trier", ("note.txt",)) / "note.txt"
        self.inscrire(note, statut_classement="general", contenu_lu=1,
                      resume="note de reunion", type_document="note", entite_id=None)
        resultat = self.lancer()
        self.assertIn("note.txt", resultat.stdout.split("--- Statuts")[-1])
        self.assertEqual(1, resultat.returncode)

    def test_document_general_a_fiche_incomplete_reste_signale(self):
        """Non-regression : le statut general dispense de structure, pas de type ni de resume."""
        note = self.dossier_docs("docs", ("sans-type.txt",)) / "sans-type.txt"
        self.inscrire(note, statut_classement="general", contenu_lu=1,
                      resume="une note", type_document=None, entite_id=None)
        resultat = self.lancer()
        self.assertIn("sans-type.txt", resultat.stdout)
        self.assertEqual(1, resultat.returncode)

    def test_un_vrai_dossier_a_trier_reste_signale(self):
        vrai = self.dossier_docs("a_trier", ("classe.pdf",)) / "classe.pdf"
        self.inscrire(vrai, statut_classement="classe", contenu_lu=1,
                      resume="ok", type_document="achat")
        resultat = self.lancer()
        self.assertIn("a_trier", resultat.stdout.split("--- Statuts")[-1])
        self.assertEqual(1, resultat.returncode)


class TestExtraireTexte(BaseTemporaire):

    def lancer(self, *arguments):
        return self.lancer_script("extraire_texte.py", *arguments)

    def preparer(self):
        source = self.dossier_docs("docs", ("note1.txt", "note2.txt"))
        quand = bdd.maintenant()
        for fichier in sorted(source.glob("*.txt")):
            self.conn.execute(
                "INSERT INTO fichiers (chemin, nom, extension, date_premiere_detection,"
                " date_derniere_verification, statut_classement) VALUES (?, ?, '.txt', ?, ?, 'a_lire')",
                (bdd.normaliser(fichier), fichier.name, quand, quand),
            )
        self.conn.commit()

    def test_limite_zero_ne_traite_aucun_fichier(self):
        self.preparer()
        resultat = self.lancer("--limite", "0")
        self.assertEqual(0, resultat.returncode, resultat.stderr)
        self.assertIn("extraits : 0", resultat.stdout)
        reste = self.conn.execute("SELECT COUNT(*) AS n FROM fichiers_contenu").fetchone()["n"]
        self.assertEqual(0, reste)

    def test_limite_negative_refusee(self):
        self.preparer()
        resultat = self.lancer("--limite", "-1")
        self.assertNotEqual(0, resultat.returncode)

    def test_limite_sans_valeur_refusee(self):
        self.preparer()
        resultat = self.lancer("--limite")
        self.assertNotEqual(0, resultat.returncode)

    def test_extraction_normale(self):
        self.preparer()
        resultat = self.lancer("--limite", "1")
        self.assertEqual(0, resultat.returncode, resultat.stderr)
        self.assertIn("extraits : 1", resultat.stdout)


@unittest.skipUnless((RACINE_DEPOT / "manifeste.py").exists(),
                     "tests du depot : manifeste.py absent (copie installee chez l'utilisateur)")
class TestManifeste(unittest.TestCase):

    def setUp(self):
        self.depot = Path(tempfile.mkdtemp(prefix="kit-manifeste-")).resolve()
        subprocess.run(["git", "init", "-q"], cwd=self.depot, check=True, timeout=60)
        (self.depot / "modele").mkdir()
        (self.depot / "arborescence" / "_corbeille").mkdir(parents=True)
        (self.depot / "README.md").write_text("doc", encoding="utf-8")
        (self.depot / "modele" / "INSTRUCTIONS.md").write_text("instructions", encoding="utf-8")
        (self.depot / "arborescence" / "_corbeille" / "README.md").write_text("corbeille", encoding="utf-8")
        (self.depot / "MANIFESTE.txt").write_text(
            "# ancien manifeste\nutilisateur  modele/INSTRUCTIONS.md\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=self.depot, check=True, timeout=60)

    def tearDown(self):
        shutil.rmtree(self.depot, ignore_errors=True)

    def lancer(self, *arguments):
        return subprocess.run(
            [sys.executable, str(RACINE_DEPOT / "manifeste.py"), *arguments],
            capture_output=True, text=True, timeout=120,
        )

    def test_generer_puis_verifier_puis_alterer(self):
        resultat = self.lancer("--generer", "--depot", str(self.depot))
        self.assertEqual(0, resultat.returncode, resultat.stderr)
        texte = (self.depot / "MANIFESTE.txt").read_text(encoding="utf-8")

        self.assertIn("CLAUDE.md", texte.split("\n\n")[0], "l'en-tete doit parler de la copie personnalisee")
        lignes = manifeste.lire(self.depot / "MANIFESTE.txt")
        self.assertEqual("utilisateur", lignes["modele/INSTRUCTIONS.md"].marque,
                         "une marque deja posee doit etre conservee")
        self.assertEqual("utilisateur", lignes["arborescence/_corbeille/README.md"].marque)
        self.assertEqual("kit", lignes["README.md"].marque)
        self.assertEqual(64, len(lignes["README.md"].empreinte))

        controle = self.lancer("--verifier", str(self.depot), "--depot", str(self.depot))
        self.assertEqual(0, controle.returncode, controle.stdout + controle.stderr)

        (self.depot / "README.md").write_text("doc alteree", encoding="utf-8")
        (self.depot / "modele" / "INSTRUCTIONS.md").unlink()
        ecarts = self.lancer("--verifier", str(self.depot), "--depot", str(self.depot))
        self.assertEqual(1, ecarts.returncode)
        self.assertIn("README.md", ecarts.stdout)
        self.assertIn("modele/INSTRUCTIONS.md", ecarts.stdout)
        self.assertIn("absent", ecarts.stdout)

    def test_manifeste_du_depot_a_jour(self):
        """Le MANIFESTE versionne doit correspondre au contenu du depot, dans les deux sens."""
        resultat = self.lancer("--verifier", str(RACINE_DEPOT))
        self.assertEqual(0, resultat.returncode, resultat.stdout)
        suivis = subprocess.run(["git", "ls-files"], cwd=RACINE_DEPOT, capture_output=True,
                                text=True, timeout=60)
        if suivis.returncode != 0:
            self.skipTest("depot git indisponible")
        attendus = set(suivis.stdout.split())
        inscrits = set(manifeste.lire(RACINE_DEPOT / "MANIFESTE.txt"))
        self.assertEqual(attendus, inscrits, "fichiers suivis par git absents du manifeste, ou l'inverse")

    def test_fichier_de_code_en_trop_detecte(self):
        self.lancer("--generer")
        (self.depot / "extra.py").write_text("print(1)\n", encoding="utf-8")
        ecarts = self.lancer("--verifier", str(self.depot))
        self.assertEqual(1, ecarts.returncode)
        self.assertIn("en trop", ecarts.stdout)


@unittest.skipUnless((RACINE_DEPOT / "manifeste.py").exists(),
                     "tests du depot : copie installee chez l'utilisateur")
class TestConfiguration(unittest.TestCase):

    def test_tous_les_scripts_compilent_en_python_39(self):
        import ast

        scripts = sorted(RACINE_DEPOT.glob("*.py"))
        scripts += sorted(DOSSIER_SCRIPTS.glob("*.py"))
        scripts += sorted((RACINE_DEPOT / "modules").rglob("*.py"))
        self.assertTrue(scripts)
        for script in scripts:
            with self.subTest(script=script.name):
                ast.parse(script.read_text(encoding="utf-8"), filename=str(script),
                          feature_version=(3, 9))

    def test_settings_claude_code_valide(self):
        fichier = RACINE_DEPOT / "modele" / ".claude" / "settings.json"
        donnees = json.loads(fichier.read_text(encoding="utf-8"))
        refus = donnees["permissions"]["deny"]
        for motif in ("Bash(rm *)", "Bash(rmdir *)", "Bash(del *)", "Bash(Remove-Item *)",
                      "Bash(git push *)", "Bash(curl -X POST *)", "Bash(wget --post*)",
                      "Bash(osascript *)"):
            self.assertIn(motif, refus)

    def test_requirements_epingle(self):
        fichier = DOSSIER_SCRIPTS / "requirements.txt"
        lignes = [l.strip() for l in fichier.read_text(encoding="utf-8").splitlines()
                  if l.strip() and not l.startswith("#")]
        self.assertTrue(lignes)
        for ligne in lignes:
            self.assertIn("==", ligne, f"dependance non epinglee : {ligne}")

    def test_base_creee_avec_des_droits_restreints(self):
        dossier = Path(tempfile.mkdtemp(prefix="kit-droits-")).resolve()
        self.addCleanup(shutil.rmtree, dossier, ignore_errors=True)
        origine = bdd.CHEMIN_BDD
        bdd.CHEMIN_BDD = dossier / "index.db"
        try:
            sans_bruit(init_bdd.main)
            if os.name != "nt":
                mode = bdd.CHEMIN_BDD.stat().st_mode & 0o777
                self.assertEqual(0o600, mode, f"droits trop larges : {oct(mode)}")
            conn = sqlite3.connect(bdd.CHEMIN_BDD)
            journal = conn.execute("PRAGMA journal_mode").fetchone()[0]
            conn.close()
            self.assertEqual("wal", journal)
        finally:
            bdd.CHEMIN_BDD = origine


if __name__ == "__main__":
    unittest.main()
