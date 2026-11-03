# StudyHUB 5 — bilan de la version du 3 novembre 2026

## Parcours disponible

1. Enregistrer le son direct du cours, le microphone ou leur mélange.
2. Joindre les documents du professeur avant ou pendant l’audio : PDF textuels, PowerPoint, Word ou texte.
3. Terminer la séance : les morceaux et les supports doivent être envoyés avant le traitement.
4. Obtenir un cours approfondi : explications, méthodes et exemples pédagogiques ajoutés par l’IA, avec des recherches encyclopédiques optionnelles. Le cours se lit sans minutes ; les références sont rangées à part.
5. Réviser avec les points importants, la fiche, les questions ouvertes, les QCM et les cartes mémoire.

Sans titre saisi, l’IA propose un titre à partir du contenu. Un titre manuel est conservé. Les quiz peuvent cibler un niveau, une notion et les erreurs récentes. Ajouter ou retirer un support après rédaction demande de recréer le cours.

Le logo original associe un livre et une onde sonore. Il est intégré dans l’accueil, la navigation, le favicon et l’application « Cours ISC.app » du Bureau. Son image et son prompt de création sont dans `assets/`.

## Ce qui a été vérifié

- Sauvegarde des morceaux, retransmissions sans doublons, récupération, lecture audio partielle et export ZIP sur données temporaires.
- Ajout simultané de supports, renvoi sans doublon, suppression, refus des fichiers invalides et des quiz fondés sur un cours devenu périmé.
- Extraction Word et avertissement sur un PDF contenant des pages sans texte.
- Interface sur ordinateur et mobile, navigation, recherche, logo et consultation des références.
- Capture artificielle du son partagé sans ouverture du microphone ; pause/reprise ; absence de piste audio et coupure de source.
- Support conservé dans le navigateur avant la capture, puis envoyé ; ajout d’un second support pendant la capture et reprise après un échec d’envoi simulé.
- Titre automatique, conservation du titre manuel, lecture de la fin d’un support long, rejet des références inconnues et de chiffres absents des preuves, maintien d’un chapitre déjà rédigé après interruption.
- Quiz, mots clés et cartes d’un cours en anglais validés avec conservation des citations originales.
- Génération avec le véritable modèle local sur des sources fictives courtes : un titre, deux chapitres, références orales et écrites, quatre QCM validés et cartes mémoire.

Le premier essai libre avait inventé des exemples chiffrés et des méthodes. La rédaction utilise désormais des extraits identifiés, un filtre des chiffres et une vérification séparée par l’IA, avec tentative de correction d’une partie refusée.

## Limites concrètes

### L’IA locale peut encore se tromper

Qwen3 4B est un petit modèle. Il peut reformuler de façon maladroite, répéter une idée, tirer un lien insuffisamment justifié ou manquer une nuance. Le même modèle rédige et vérifie : les contrôles réduisent certains ajouts, sans constituer une preuve de justesse. Les références permettent de revenir au contenu original. Une vérification stricte peut aussi refuser une bonne reformulation ou produire moins de questions que demandé.

Le professeur fournit la base et le niveau. L’IA peut désormais apporter ses connaissances générales et des exemples fictifs clairement pédagogiques. Ces ajouts ne doivent pas être présentés comme des propos ou des consignes du professeur. Les connaissances générales du modèle ne sont pas une recherche fraîchement vérifiée. La rédaction complète prend plusieurs minutes. Les longs cours et les supports sont découpés puis condensés : toutes les parties sont lues, mais une nuance peut disparaître de la synthèse. Un vrai cours long n’a pas été validé de bout en bout dans ces tests.

### L’audio et Teams doivent être essayés en conditions réelles

Les tests utilisent un signal et des voix artificiels. Ils ne valident pas les autorisations macOS ni la capture d’une vraie réunion Teams. Le partage d’un onglet avec son activé est le parcours à essayer dans un navigateur compatible. Le partage d’une application native ou du son de tout le Mac dépend du navigateur et du système. Une piste audio présente peut malgré tout être silencieuse : la réécoute du test est essentielle.

Whisper Small peut confondre des noms, chiffres, accents ou voix superposées. Le marquage des passages incertains ne détecte pas toutes les erreurs. « Zéro erreur » n’est pas garanti.

### Certains documents restent partiellement lisibles

Les images, scans, photos de tableau et équations sous forme d’image ne sont pas interprétés. Un PDF peut contenir à la fois du texte exploitable et des pages scannées : les pages sans texte sont signalées. Les textes et tableaux simples d’un PowerPoint sont extraits, pas sa mise en page ni le sens de ses graphiques. Les pages d’un Word ne sont pas reconstituées fidèlement.

### La sauvegarde dépend encore de l’ordinateur et du navigateur

Le navigateur doit rester ouvert et le Mac éveillé. Une fermeture ou une panne peut perdre les dernières secondes non encore produites. Les supports et morceaux en attente se récupèrent dans le même navigateur et le même profil ; effacer ses données peut supprimer ce secours. Une sauvegarde sur le même disque ne protège pas d’une panne du Mac. Une erreur d’envoi d’un support bloque la création automatique jusqu’à son renvoi ou son retrait.

### Ce n’est pas encore un service public hébergé

L’application actuelle est locale, destinée à macOS Apple Silicon. Elle n’a ni comptes utilisateurs, ni synchronisation entre appareils, ni hébergement multiutilisateur. L’archive de sources est préparée pour GitHub et exclut les cours, audios, modèles et données privées. Aucun dépôt distant n’a été publié. La restauration automatique d’un ZIP de cours reste à construire.

## Recherche encyclopédique : limites

Cette intégration lit des articles de Wikipédia après une recherche de notions générales. Ce n’est pas une recherche exhaustive du web, ni une validation par un expert ou par toutes les sources primaires. Les requêtes peuvent retourner une page trop générale. Les sources consultées et les échecs restent visibles. Les connaissances utilisées sans recherche ne sont pas présentées comme vérifiées en ligne.

## Exemples chiffrés

L’application calcule les opérations élémentaires des exemples structurés à partir des données et expressions fournies. Un résultat numérique annoncé à la main par le modèle n’est pas utilisé. Les expressions ne peuvent exécuter aucun programme. Cela réduit les erreurs de calcul, mais ne garantit pas que la formule, les hypothèses ou l’interprétation proposées sont adaptées à la question.
