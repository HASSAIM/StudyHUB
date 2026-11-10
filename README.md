# StudyHUB · Cours ISC

Un espace personnel pour transformer les enregistrements et les supports du professeur en cours expliqués, puis réviser avec des quiz personnalisés. L’interface utilise une navigation simple et une palette vert forêt, sauge et crème. Les fichiers et les modèles d’IA restent sur le Mac ; la recherche optionnelle transmet des mots clés généraux à Wikipédia.

## Utiliser l’application

Ouvrir **Cours ISC.app** sur le Bureau, ou lancer `Lancer.command`. Le lanceur installé pointe vers ce dossier : ne pas le déplacer sans le mettre à jour.

- **Accueil** : cours récents, minutes enregistrées, cartes à revoir et récupération des séances interrompues.
- **Mes cours** : recherche et filtre par matière.
- **Enregistrer** : nom du cours, langue, Teams ou salle, puis un seul bouton pour démarrer. Les réglages audio et les supports restent facultatifs et repliés.
- **Réviser** : résultats des quiz, erreurs et cartes à revoir.
- **Sauvegardes** : export ZIP des données.

## Enregistrer un cours Teams

1. Dans Safari sur Mac, StudyHUB utilise désormais un composant local « StudyHUB Audio » pour capter directement le son du Mac. Autoriser ce composant dans Réglages Système → Confidentialité et sécurité → Enregistrement de l’écran et des sons du système. La permission est nécessaire avant chaque première utilisation du composant. Dans Chrome ou Edge, le partage audio d’un onglet reste disponible.
2. Ouvrir de préférence Teams dans un onglet de ce navigateur.
3. Choisir **Teams / cours en ligne · son partagé uniquement**.
4. Cliquer sur **Enregistrer**. Dans Safari sur Mac, le composant natif capture directement le son du Mac. Dans Chrome ou Edge, sélectionner l’onglet du cours et activer **Partager le son**.
5. L’enregistrement démarre directement. Le niveau sonore reste visible pendant le cours ; un test de six secondes reste disponible dans **Options audio**, sans être obligatoire.

Ce mode n’ouvre pas le microphone. Le partage de son d’une application native, d’une fenêtre ou de tout le Mac dépend des possibilités du navigateur et de macOS : la présence d’un écran partagé ne prouve pas que son audio est disponible. Aucun contournement par le micro n’est appliqué si la source audio manque.

Une source coupée arrête la capture et déclenche la sauvegarde. Une source silencieuse pendant quinze secondes affiche un avertissement. Une demande de maintien de l’écran éveillé est faite lorsque le navigateur le permet ; garder la fenêtre ouverte et le Mac éveillé reste nécessaire. Fermer le navigateur ou le Mac interrompt l’enregistrement.

En salle, utiliser le microphone. Le mode mixte ajoute le micro au son partagé ; un casque réduit les échos. Les deux sources sont atténuées avant mélange pour limiter la saturation.

## Du cours du professeur au cours approfondi

Le parcours est : **audio et supports → base du professeur → recherches et explications approfondies → cours lisible → exercices et quiz**.

« Mon cours » présente une leçon avec des paragraphes, des définitions expliquées, le pourquoi des méthodes, des exemples pédagogiques résolus et des pièges fréquents. L’IA peut apporter des connaissances qui ne sont pas dans la transcription. Les exemples ajoutés sont pédagogiques, pas des événements ni des consignes attribués au professeur. Le cours et l’essentiel se lisent sans repères minute. Les références, recherches et paroles originales restent consultables dans **Sources et recherches** et **Transcription**.

La base du professeur reste conservée séparément. Sans titre saisi, l’IA propose un titre. Un titre manuel est conservé. Les quiz ciblent un niveau, une notion et les erreurs récentes, avec 4, 6 ou 8 questions demandées ; le nombre validé peut être inférieur. Ils peuvent porter sur les explications et exemples du cours enrichi, tout en distinguant leur provenance.

### Recherches en ligne

L’option est activée par défaut et peut être désactivée avant la capture ou pour la prochaine rédaction dans **Sources et recherches**. Cette première intégration utilise l’[API REST MediaWiki](https://www.mediawiki.org/wiki/API:REST_API/Reference) pour effectuer une recherche encyclopédique sur Wikipédia, sur trois notions générales au maximum, puis lit les articles réellement retournés. Elle ne constitue pas une recherche exhaustive du web ni une vérification systématique par des sources primaires.

Seuls des mots clés conceptuels sont transmis au service de recherche ; les fichiers, l’audio et la transcription ne sont pas téléversés. Les modèles de transcription et de rédaction fonctionnent sur le Mac. Une recherche nécessite Internet. Si elle échoue, l’application le signale et ne crée pas de fausse source : les compléments éventuels reposent alors sur les connaissances du modèle. Les liens, dates de consultation et attribution des articles sont conservés. Les connaissances du modèle ne remplacent pas une vérification actuelle des lois, taux ou statistiques.

### Documents pendant la capture

Joindre un ou plusieurs PDF textuels, PowerPoint .pptx, Word .docx ou textes .txt avant ou pendant l’audio. Les fichiers en attente sont conservés dans le navigateur, puis envoyés au Mac. La finalisation attend leur envoi. Une erreur bloque la création automatique jusqu’au renvoi ou au retrait du document, pour ne pas prétendre l’avoir intégré. Limite : 50 Mo et 500 000 caractères extraits par support. Les documents trop longs sont refusés, pas silencieusement tronqués.

Ajouter ou retirer un support après rédaction marque le cours comme à recréer. La rédaction approfondie est plus lente et reste limitée par Qwen3 4B : une relecture par le même modèle ne garantit pas toute la justesse. La base sourcée, les compléments pédagogiques et les recherches gardent des provenances différentes.

## Transcription

La reconnaissance utilise **faster-whisper Small**, sur CPU, sans clé d’API. Les réglages de cette version utilisent la détection des silences avec marge autour de la voix, un décodage déterministe, des horodatages par mot et la désactivation du conditionnement sur les segments précédents afin de limiter les boucles de texte. Un vocabulaire facultatif aide à reconnaître les noms et les sigles.

Les segments de faible confiance sont marqués **À vérifier**. Cet indicateur est heuristique : il ne détecte pas toutes les erreurs. Un son propre ne garantit pas une transcription parfaite, notamment pour les chiffres, noms propres ou voix qui se chevauchent.

L’analyse pédagogique utilise **Qwen3 4B via MLX**. Les quiz et cartes utilisent la base du professeur, les recherches consultées et le cours enrichi, avec une provenance explicite. Un contrôle des citations et une vérification pédagogique sont appliqués, sans garantie d’absence d’erreurs. Les traitements sont sérialisés pour limiter la mémoire.

L’assistant utilise le cours sélectionné et ses supports textuels PDF, .pptx, .docx ou .txt. Les scans et images ne sont pas reconnus. Aucune connexion Moodle n’est proposée.

## Sauvegarde et récupération

Les morceaux audio sont produits environ toutes les cinq secondes, enregistrés dans IndexedDB, puis envoyés au serveur local. L’écriture de secours n’attend pas la réponse réseau du morceau précédent. Les morceaux sont numérotés ; leur retransmission ne duplique pas l’audio.

Après une interruption, ouvrir l’application dans **le même navigateur et le même profil**, puis choisir **Récupérer mon cours** sur l’accueil ou **Récupérer les morceaux** dans la bibliothèque. Ne pas effacer les données du navigateur avant récupération. Les secondes non encore produites par le navigateur peuvent être perdues.

Les données se trouvent dans `sessions/`. Exporter une archive ZIP après les traitements et la copier sur un disque externe. L’archive contient les cours, pas les modèles ou l’environnement logiciel. La restauration automatique d’un ZIP n’est pas encore disponible.

## Installation depuis les sources

Cible actuelle : macOS Apple Silicon, Python 3.12. MLX n’est pas un moteur multiplateforme. Les modèles nécessitent plusieurs gigaoctets et une connexion lors du premier téléchargement.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python prepare_model.py
.venv/bin/python prepare_notes_model.py
.venv/bin/python launch.py
```

Après téléchargement des modèles, les traitements IA sont locaux. Les recherches optionnelles utilisent Internet. Le serveur écoute uniquement sur `127.0.0.1:8765`, avec jeton et vérification de l’origine pour les modifications.

## Vérifications

```sh
.venv/bin/python test_v2.py
.venv/bin/python test_learning.py
.venv/bin/python test_research.py
.venv/bin/python test_teaching.py
.venv/bin/python test_enrichment.py
.venv/bin/python test_english_structure.py
# Test plus long avec le véritable modèle local et des sources fictives :
.venv/bin/python test_course_local.py
.venv/bin/python test_enrichment_local.py
# Créer une voix synthétique de test sur macOS avant le test WebM :
say -v Samantha -o /private/tmp/isc-audio-test.aiff 'The project budget is fifteen thousand euros.'
.venv/bin/python test_audio_v2.py
```

Les tests du serveur utilisent des données temporaires : sauvegarde, retransmissions, récupération, lecture partielle, protection locale, quiz, cartes, supports et ZIP.

Pour l’interface, installer les dépendances de développement, puis le navigateur de test :

```sh
npm install
npx playwright install chromium
npm run test:ui
```

Le test d’interface utilise des cours fictifs et un son artificiel. Il vérifie l’affichage ordinateur/mobile, la navigation, la recherche, la capture sans micro, la pause/reprise, les morceaux sauvegardés, l’absence de piste audio et la coupure de la source. Il couvre aussi les supports joints avant et pendant la capture, la reprise d’envoi, la personnalisation des quiz, le logo et la lecture des références. Il ne valide pas les permissions macOS ni une réunion Teams réelle.

## Dépôt GitHub et données privées

Créer le dépôt **à partir du dossier `cours-local/` uniquement**. Ne pas publier le dossier parent du projet ISC, ses références ou sa bibliothèque de cours.

Le `.gitignore` exclut les cours et audios (`sessions/`), modèles, environnement Python, applications compilées, journaux, fichiers `.env`, sauvegardes de développement, résultats et captures de test. Le code du lanceur compilé contient un ancien chemin absolu : l’installation portable utilise `launch.py` ou `Lancer.command`.

Dépôt public : https://github.com/HASSAIM/StudyHUB. Les données de cours ne font pas partie du dépôt. Aucune licence de réutilisation du code n’a encore été choisie. Publier le code ne fournit pas un site hébergé : l’application se lance localement.

Après un téléchargement des sources, si macOS refuse l’ouverture du lanceur faute de droit d’exécution, utiliser `chmod +x Lancer.command`, puis le lancer, ou exécuter `python3 launch.py` après installation des dépendances.

## Identité visuelle

Le logo est disponible dans `assets/studyhub-logo.png`, avec son favicon et son icône macOS. Sa direction et son prompt de création sont décrits dans `assets/creation-logo.md`. L’application installée sur le Bureau utilise cette icône.

Un bilan détaillé des vérifications et limites est disponible dans `BILAN_VERSION.md`. Une archive propre peut être créée avec `python scripts/package_sources.py /chemin/StudyHUB-sources.zip` : le script utilise une liste explicite de fichiers et exclut les données de cours.

La rédaction approfondie et sa relecture sont structurées en sections pédagogiques : le rapport interne de correction n’est pas présenté comme un chapitre. La matière et le niveau universitaire doivent être conservés ; la simplicité de lecture ne signifie pas remplacer le sujet par des conseils quotidiens.

Les exemples numériques structurés séparent les données, les formules et l’interprétation. L’application évalue les opérations arithmétiques autorisées et calcule les résultats au lieu de reprendre un total rédigé par le modèle. Cela vérifie l’arithmétique, pas la pertinence du modèle choisi ni toutes les hypothèses de l’exemple. Un exemple numérique mal structuré est écarté.

## Capture directe du son dans Safari

Le code `native/SystemAudio.swift` utilise ScreenCaptureKit et n’enregistre que la sortie audio : aucune sortie vidéo ou microphone n’est enregistrée. La permission macOS reste plus large et doit être autorisée par l’utilisateur. Tous les sons du Mac sont inclus, y compris ceux d’autres applications ; ce n’est pas un filtre réservé à Teams.

Le composant est compilé localement à partir des sources, avec les outils de développement Apple, et placé dans `native-build/`, exclu de Git. Le son est écrit sur le disque en WAV mono 48 kHz, avec mise à jour et synchronisation de l’en-tête chaque seconde. Pause/reprise et arrêt passent par le serveur local protégé. Une absence de nouvelles du navigateur pendant trois minutes demande l’arrêt. Les données déjà écrites restent récupérables.

Les tests automatisés vérifient le parcours Safari simulé, les commandes, les sauvegardes et l’unicité de la capture. La compilation a été vérifiée sur ce Mac. Un test réel avec voix synthétique sur ce Mac a confirmé la présence du son et la sauvegarde. Une longue séance Teams reste à valider.


Validation locale du 4 novembre : le tampon audio CoreMedia utilise maintenant la taille demandee par le systeme. Le test reel enregistre une voix synthetique jouee par le Mac, avec des echantillons non nuls en WAV mono 48 kHz. La sauvegarde apres arret est verifiee. Un cours Teams long reste a valider. La distribution du composant reste experimentale : les reconstructions avec signature ad hoc peuvent exiger de retirer puis reajouter StudyHUB Audio dans les autorisations macOS. Une signature et une notarisation Apple stables restent necessaires avant une distribution simple.
