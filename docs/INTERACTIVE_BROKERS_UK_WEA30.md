# Interactive Brokers (UK) — API et ordres autonomes (WEA-30)

Document d’ancrage pour le ticket [WEA-30](https://linear.app/weadu/issue/WEA-30/interactive-brokers-uk-api-et-ordres-autonomes). Il complète le socle secrets ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)) et la cartographie secrets ([WEA-14](https://linear.app/weadu/issue/WEA-14/secrets-cartographie-1password-github-cursor-regle-chercher-avant-de)) : **aucun identifiant IBKR ne doit figurer dans un dépôt** ; variables sensibles uniquement dans coffres / secrets isolés **finance-RH** ou équivalent.

---

## 1. Chemins API (à choisir selon le besoin)

### 1.1 Client Portal Web API (HTTPS)

- **Usage** : API REST orientée navigateur / applications qui passent par la **Client Portal Gateway** (locale ou hébergée selon votre déploiement).
- **Documentation officielle** : portail développeur IBKR — [Web API](https://www.interactivebrokers.com/campus/ibkr-api-page/web-api-trading/) et guides « Getting started » associés (connexion, gateway, premiers appels).
- **UK** : les comptes UK utilisent les mêmes APIs globales IBKR ; vérifiez les conditions du **compte paper / live** et la disponibilité des produits sur votre profil.

### 1.2 TWS / IB Gateway — socket API (programs « classiques »)

- **Usage** : connexion TCP locale (typiquement **IB Gateway** ou **Trader Workstation**) avec la lib officielle **Python `ibapi`** ou autres langages supportés.
- **Documentation** : [TWS API](https://interactivebrokers.github.io/tws-api/) (contrats, ordres, sessions).
- **Ports usuels** : paper souvent **7497**, live souvent **7496** (à confirmer dans votre installation ; ne pas coder ces valeurs comme secrets).

### 1.3 Portail client / gestion du compte

- **Accès humain** : [Client Portal](https://www.interactivebrokers.co.uk/) (UK) pour validation des paramètres compte, permissions API, lecture des risques produits.

---

## 2. Cadre « ordres autonomes » (sans validation à chaque fois)

Les points suivants sont **à valider côté IBKR et conformité interne** avant toute automatisation sur compte réel :

1. **Compte dédié** : privilégier un sous-compte ou un compte **paper** pour les agents jusqu’à validation procédurale.
2. **Permissions API** : dans la configuration TWS / Gateway, autoriser l’API et définir qui peut placer des ordres (adresses IP autorisées si applicable).
3. **Paper trading** : même pile logicielle que le réel avec données simulées — idéal pour « test minimal » sans risque de marché.
4. **Pas de secrets dans Git** : identifiants, jetons et certificats dans un gestionnaire / secrets runner alignés [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh) ; repos **finance** avec équipes et environnements GitHub dédiés ([WEA-13](https://linear.app/weadu/issue/WEA-13/github-modele-dacces-interne-partage-perso-finance-rh-isole)).

---

## 3. Test minimal (automatisé dans ce dépôt)

Le script [`scripts/ibkr_smoke_wea30.py`](../scripts/ibkr_smoke_wea30.py) fournit :

- **`--dry-run`** (utilisé en CI) : vérifie que l’interpréteur exécute le script et rappelle les variables attendues — **aucune** connexion réseau.
- **Connexion optionnelle** : avec `ibapi` installé (`pip install ibapi`) et variables `IBKR_HOST`, `IBKR_PORT`, `IBKR_CLIENT_ID`, lance une tentative de connexion au socket Gateway/TWS (échoue proprement si aucun listener local).

Commandes :

```bash
python3 scripts/ibkr_smoke_wea30.py --dry-run
python3 scripts/ibkr_smoke_wea30.py   # nécessite Gateway/TWS + ibapi
```

---

## 4. Rappel risque (courtage)

**Les ordres passés via API ont les mêmes risques financiers que les ordres manuels : perte en capital, effet de levier, contrepartie, risque de marché et de liquidité, erreurs de paramétrage (prix, quantité, instrument), et risque opérationnel (bugs, coupures réseau).** Interactive Brokers fournit des documents réglementaires et fiches produits ; les résidents UK sont soumis aux informations données lors de l’ouverture de compte. **Rien dans ce dépôt ne constitue un conseil en investissement.** Toute automatisation doit être validée par les responsables internes et respecter les obligations légales et contractuelles applicables à WeAdU.

---

_Document statique ; mise à jour lorsque le socle secrets (WEA-15) ou les choix d’API (Web vs TWS) sont figés._
