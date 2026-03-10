# Installation

Plusieurs méthodes sont disponibles pour installer Git IA Assistant selon vos besoins.

## 📦 Méthode rapide (curl / wget)

Vous pouvez installer l'assistant directement avec cette commande :

```bash
curl -fsSL https://raw.githubusercontent.com/stef38-code/git-ia-assistant/main/install.sh | bash
```

ou via wget :

```bash
wget -qO- https://raw.githubusercontent.com/stef38-code/git-ia-assistant/main/install.sh | bash
```

## 🛠️ Méthode manuelle

1. **Cloner le projet** :
```bash
git clone https://github.com/stef38-code/git-ia-assistant.git
cd git-ia-assistant
```

2. **Installer** :
Utilisez le script d'installation fourni. Il s'occupera de mettre à jour les sous-modules, de créer un environnement virtuel dans `${HOME}/.local/share/git-ia-assistant` et de créer des liens symboliques dans `${HOME}/.local/bin`.

```bash
chmod +x install.sh
./install.sh
```

## 💻 Environnement de développement

Si vous souhaitez développer ou tester le projet localement après un `git clone` :

1. **Initialiser l'environnement local** :
```bash
chmod +x dev-setup.sh
./dev-setup.sh
```

2. **Activer l'environnement virtuel** :
```bash
source .venv/bin/activate
```

Les commandes (`git-ia-commit`, etc.) seront alors disponibles dans votre terminal tant que l'environnement est actif.
