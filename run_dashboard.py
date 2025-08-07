# -*- coding: utf-8 -*-
"""
run_dashboard.py

Script de lancement du dashboard SEO.
Lance le serveur Streamlit avec la configuration appropriée.
"""

import subprocess
import sys
from pathlib import Path
import os

def main():
    """Lance le dashboard SEO."""
    
    # S'assurer qu'on est dans le bon répertoire
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Chemin vers l'application dashboard
    dashboard_app = script_dir / "dashboard" / "app.py"
    
    if not dashboard_app.exists():
        print("❌ Erreur: L'application dashboard est introuvable.")
        print(f"Cherché dans: {dashboard_app}")
        sys.exit(1)
    
    print("🚀 Lancement du Dashboard SEO...")
    print(f"📁 Répertoire de travail: {script_dir}")
    print(f"🎯 Application: {dashboard_app}")
    print("\n" + "="*50)
    print("📊 SEO Analyzer Dashboard")
    print("="*50)
    print("🌐 URL: http://localhost:8501")
    print("⏹️  Arrêter: Ctrl+C")
    print("="*50 + "\n")
    
    try:
        # Commande pour lancer Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_app),
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false",
            "--server.headless=false"
        ]
        
        # Lancer le processus
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard arrêté par l'utilisateur.")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erreur lors du lancement: {e}")
        print("💡 Vérifiez que Streamlit est installé: uv add streamlit")
        sys.exit(1)
        
    except FileNotFoundError:
        print("\n❌ Erreur: Python ou Streamlit introuvable.")
        print("💡 Vérifiez votre installation Python et les dépendances.")
        sys.exit(1)


if __name__ == "__main__":
    main()