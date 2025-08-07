la partie etude de cas en fonctionne pas via la GUI sur le streamlit.

rappel de l'objectif, l'outil dois permettre de comparer la position de notre marque vis a vis de la concurence lorsqu'un utilisateur pose une question sur un llm et fournir des pistes pour des axes d'amelioration.

Je souhaite la simplifier en appliquant le processus suivant (pas beosin d 'un case manager complet):

1/ permettre a l'utilisateur de poser une question

2/ poser la question sur les LLM selectionné par l'utilisateur

3/ afficher les réponses des LLM, les sources extraites et les mots clés trouvés (les mots clés sont des référence au entreprise dont les liens sont cité ou autre entreprises du même secteurs). Regrouper les url et mot clé sous des tags (par exemple le tag meilleurtaux pour le mot clef meilleurtaux, assurea, et les lien vers des page du site meilleurtaux)

4/ permettre a l'utilisateur de modifier les resultats de l'extraction: la liste de mot clés, des liens et de corriger les tags

5/ permettre a l'utilisateur de selectionner les tags sur lequels lancer l'analyse

6/ lorsque l'utilisateur clique sur "lancer l'analyse" : analyser le contenu de chaque tag selectionné avec le module precedant pour les url, inclure dans l'analyse, le sentiment assicé a cette citation dans la réposne du LLM ainsi que le sentiment associé a a chaque mot clé identifié dans la réponse du LLM. la position de la citation dans la réponse du llm, ...( et toute autre information utile)

7/ l'utilisateur selectionne les entité qu'il souhaite comparer parmis celle analysé precedement

8/ il peut cliquer sur un bouton comparer pour réaliser une comparaison de l'ensemble des analyse

9/ permettre a l'utilisateur d'exporter le rapport complet ou chaque analyse independament

Toutes les statistique sont donné par LLM 

N'hesites pas a proposer toute autre idée pour améliorer ce procesus ou la qualité de l'analyse.

Une fois que tout focntionne pour un cas unique envisager la création d'un case manager pour "sauvergarder" les analyses et comparaison precedante