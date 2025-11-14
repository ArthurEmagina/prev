# Application Cloud - Calcul des délais et coûts

Version en ligne accessible depuis n'importe quel appareil via Streamlit Cloud.

## 🚀 Déploiement sur Streamlit Cloud

### Prérequis
- Un compte GitHub (gratuit)
- Un compte Streamlit Cloud (gratuit) : https://share.streamlit.io/

### Étapes de déploiement

1. **Créer un dépôt GitHub**
   - Allez sur https://github.com/new
   - Créez un nouveau dépôt (public ou privé)
   - Nommez-le par exemple : `calcul-delais-cout-cloud`

2. **Uploader les fichiers**
   - Clonez le dépôt sur votre PC
   - Copiez tous les fichiers du dossier `app_cloud` dans le dépôt
   - Structure attendue :
     ```
     votre-repo/
     ├── streamlit_app.py
     ├── requirements.txt
     ├── config.yaml
     ├── calculator/
     │   ├── __init__.py
     │   ├── data_loader.py
     │   ├── logic.py
     │   └── tiered_columns.py
     └── .streamlit/
         └── config.toml
     ```
   - Committez et poussez les fichiers :
     ```bash
     git add .
     git commit -m "Initial commit"
     git push
     ```

3. **Déployer sur Streamlit Cloud**
   - Allez sur https://share.streamlit.io/
   - Cliquez sur "New app"
   - Connectez votre compte GitHub si nécessaire
   - Sélectionnez votre dépôt
   - Sélectionnez la branche (généralement `main` ou `master`)
   - Le fichier principal doit être : `streamlit_app.py`
   - Cliquez sur "Deploy"

4. **Accéder à votre application**
   - Une fois déployée, vous recevrez une URL du type :
     `https://votre-app.streamlit.app`
   - Partagez cette URL avec qui vous voulez !
   - L'application sera accessible depuis n'importe quel appareil

## 📝 Utilisation

1. Ouvrez l'URL de votre application dans un navigateur
2. Dans la barre latérale, cliquez sur "Browse files"
3. Sélectionnez votre fichier `InputDélais.xlsm`
4. L'application chargera automatiquement les données
5. Utilisez les onglets pour planifier ou suivre vos commandes

## 🔄 Mises à jour

Pour mettre à jour l'application :
1. Modifiez les fichiers localement
2. Committez et poussez les changements sur GitHub
3. Streamlit Cloud redéploiera automatiquement l'application

## ⚙️ Configuration

Le fichier `config.yaml` contient la configuration de l'application. Vous pouvez le modifier selon vos besoins.

## 📦 Fichiers nécessaires

- `streamlit_app.py` : Application principale
- `requirements.txt` : Dépendances Python
- `config.yaml` : Configuration
- `calculator/` : Modules de calcul
- `.streamlit/config.toml` : Configuration Streamlit

## 🌐 Avantages de la version cloud

- ✅ Accessible depuis n'importe où (PC, Mac, tablette, téléphone)
- ✅ Pas d'installation nécessaire
- ✅ Mises à jour automatiques
- ✅ Partage facile via un simple lien
- ✅ Pas de problèmes de compatibilité OS
- ✅ Gratuit (plan gratuit de Streamlit Cloud)

## 🔒 Sécurité

- Les fichiers uploadés sont stockés temporairement sur le serveur
- Les données ne sont pas conservées entre les sessions
- Chaque utilisateur upload son propre fichier Excel

## 💡 Notes

- La première fois que vous ouvrez l'application, elle peut prendre quelques secondes à démarrer
- Si vous modifiez le fichier Excel, rechargez-le dans l'application
- L'application fonctionne uniquement avec des fichiers uploadés (pas de fichiers locaux)

