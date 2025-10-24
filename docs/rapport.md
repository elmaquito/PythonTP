# Rapport Technique - Système de Contrôle d'Accès Restaurant

## 1. Introduction

### 1.1 Objectif du Projet
Le projet consiste à développer une application de contrôle d'accès pour restaurant scolaire utilisant la reconnaissance faciale. L'objectif est de vérifier l'identité des étudiants et contrôler leur accès en fonction de leur solde.

# Rapport Technique - Système de Contrôle d'Accès Restaurant

## 1. Introduction

Ce document a été mis à jour pour refléter l'état actuel de l'application au 24 Octobre 2025.
La version courte: l'application est fonctionnelle pour un usage éducatif local — flux caméra non bloquant, identification en tâche de fond,
historique des reconnaissances et journal d'audit pour les opérations sensibles.

### Objectif
Fournir un système simple et autonome de contrôle d'accès basé sur la reconnaissance faciale, adapté à des environnements pédagogiques.

## 2. Organisation minimale du projet (après nettoyage)

Seuls les modules nécessaires au fonctionnement et à la maintenance locale sont conservés à la racine. Les outils et scripts auxiliaires ont été archivés
dans le répertoire `archive/` pour garder l'historique sans alourdir la structure.

Structure simplifiée:

```
PythonTP/
├── main.py                    # Point d'entrée et authentification
├── gui.py                     # Interface Tkinter (flux caméra, identification)
├── face_recognition_utils.py  # Encodages et identification faciale
├── db.py                      # Gestion des données students.json et audit
├── requirements.txt           # Dépendances minimales
├── students.json              # Base de données application (JSON)
├── images/                    # Photos des étudiants
├── docs/                      # Documentation (rapport, guide)
└── archive/                   # Scripts et helpers mis en archive (non actifs)
```

Remarques:
- Le dossier `archive/` contient les scripts de déploiement, d'installation, de tests et autres utilitaires qui ne sont pas nécessaires au fonctionnement courant.
- L'architecture favorise la simplicité : GUI (présentation), `db.py` (données + audit), `face_recognition_utils.py` (reconnaissance).

## 3. État applicatif actuel (fonctionnelités clés)

- Camera feed: le flux caméra tourne et met à jour l'UI via `root.after()` (~30 FPS). La détection/encodage s'exécute en arrière-plan pour éviter de bloquer l'interface.
- Capture & Identify: fonctionne en tâche de fond, prend le dernier frame capturé et calcule l'encodage puis identifie le visage.
- Liste des reconnus: une colonne à droite affiche l'historique des reconnaissances (Nom, ID, Solde, Heure, Statut).
- Audit: `db.py` écrit un journal d'audit (`access.log`) pour les opérations sensibles (déductions, ajouts, consultations de solde).
- Rôles: ajout d'un compte restreint `StudentX` (rôle `student`) et logique pour masquer les options d'administration quand l'utilisateur est en rôle étudiant.
 - Logout / Switch User: menu "User" → "Switch User" / "Logout" implémenté; la fonctionnalité "Switch User" utilise désormais une boîte de dialogue de re-login en-process (pas de redémarrage), améliorant l'UX.


## 4. Décisions techniques récentes

- Identification non bloquante: exécution du passage d'encodage/identification dans un thread démon afin de garder le GUI réactif.
- Réduction par défaut de la résolution caméra (configurable) pour améliorer le FPS sur machines modestes.
- Stockage JSON conservé pour sa simplicité, avec journal d'audit en clair pour traçabilité.

## 5. Opérations et logs

- Les opérations sensibles (DEDUCT_SUCCESS / DEDUCT_FAIL / ADD_SUCCESS / ADD_FAIL / BALANCE_CHECK) sont consignées dans `access.log` à la racine.
- Pour raison de simplicité, l'authentification reste basée sur des identifiants simples (usage pédagogique). Pour un déploiement réel, il faudra chiffrer et externaliser les secrets.

## 6. Comment reprendre le projet localement

1. Installer les dépendances listées dans `requirements.txt` (ou via l'environnement fourni).
2. Lancer `python main.py` (ou `python main.py --console` pour mode console si disponible).
3. Se connecter avec un compte admin (ou `StudentX` pour un rôle étudiant restreint).

## 7. Fichiers archivés

Les fichiers suivants ont été déplacés vers `archive/` afin d'alléger la racine du projet :
- `deploy.py`, `install_dependencies.py`, `maintenance.py`, `test_system.py`, `validators.py`.

## 8. Travaux restants (suggestions)

- Remplacer le stockage JSON par SQLite pour la robustesse et la concurrence.
- Ajouter une vraie interface de changement d'utilisateur sans redémarrage.
- Ajouter des tests unitaires/CI dans `tests/` et les exécuter via GitHub Actions.
- Chiffrer les identifiants administrateurs et ajouter gestion des rôles plus fine.

## 9. Conclusion

L'application est en état d'usage pour des démonstrations et un environnement pédagogique. Les éléments non essentiels ont été archivés pour clarifier la structure et réduire la dette technique apparente dans la racine du projet.

---

**Auteur**: [Votre Nom]
**Date**: 24 Octobre 2025
**Version**: 1.1
