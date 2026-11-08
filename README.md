# Présidentielle 2027 — carte interactive

Carte web statique des projections départementales disponibles dans le jeu Repère 2027 / data.gouv.fr.

## Déploiement sur Vercel avec GitHub

1. Créer un dépôt GitHub public, par exemple `presidentielle-2027`.
2. Ajouter le fichier `index.html` à la racine du dépôt.
3. Dans Vercel, choisir **Add New Project**.
4. Sélectionner le dépôt GitHub.
5. Laisser les réglages par défaut et cliquer sur **Deploy**.

Aucun build n'est nécessaire : c'est une page HTML autonome.

## Contenu

- Premier tour : Marine Le Pen, Édouard Philippe, Jean-Luc Mélenchon.
- Second tour : Le Pen / Philippe, Le Pen / Glucksmann, Le Pen / Mélenchon.
- Données intégrées dans la page : la carte fonctionne sans dépendance extérieure à l'ouverture.

## Limite méthodologique

La carte affiche les projections départementales effectivement présentes dans la source. Les autres candidats peuvent apparaître dans les intentions nationales sans disposer d'une projection départementale.

Source : [data.gouv.fr — Présidentielle 2027](https://www.data.gouv.fr/datasets/presidentielle-2027-sondages-candidatures-et-projection-departementale)
