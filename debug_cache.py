#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
debug_cache.py

Utilitaire de debug pour tester le système de cache du dashboard.
"""

from dashboard.utils.data_loader import SEODataLoader

def test_cache_system():
    """Test le système de détection des changements de cache."""
    
    loader = SEODataLoader()
    
    # Test 1: Obtenir l'horodatage
    print("🔍 Test du système de cache")
    print("-" * 40)
    
    last_modified = loader.get_reports_last_modified()
    print(f"📅 Dernier fichier modifié: {last_modified}")
    
    # Test 2: Lister les rapports
    reports = loader.get_available_reports()
    print(f"📊 Nombre de rapports trouvés: {len(reports)}")
    
    # Test 3: Afficher les rapports récents
    if reports:
        print("\n📈 Derniers rapports:")
        sorted_reports = sorted(reports, key=lambda x: x['created_date'], reverse=True)[:5]
        
        for i, report in enumerate(sorted_reports, 1):
            print(f"{i}. {report['domain']} - {report['created_date'].strftime('%d/%m/%Y %H:%M')}")
            print(f"   URL: {report['url'][:60]}...")
            print(f"   Scores: {'✅' if report['has_scores'] else '❌'}")
            print()
    
    print("✅ Test terminé!")

if __name__ == "__main__":
    test_cache_system()