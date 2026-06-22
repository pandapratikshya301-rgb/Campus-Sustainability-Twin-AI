"""
Reinitialize Knowledge Base with New Guidelines
This script deletes the old collection and creates a new one with all guidelines
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import chromadb
from modules.rag_knowledge_base import RAGKnowledgeBase

def reinitialize_knowledge_base():
    """Delete old collection and create new one with all guidelines"""
    
    print("=" * 80)
    print("REINITIALIZING KNOWLEDGE BASE")
    print("=" * 80)
    
    try:
        # Connect to ChromaDB
        print("\n[1/3] Connecting to ChromaDB...")
        client = chromadb.PersistentClient(path="./chroma_db")
        
        # Try to delete existing collection
        print("[2/3] Deleting old collection...")
        try:
            client.delete_collection("campus_knowledge")
            print("✓ Old collection deleted")
        except Exception as e:
            print(f"ℹ No existing collection to delete: {e}")
        
        # Create new knowledge base (will initialize with all guidelines)
        print("[3/3] Creating new knowledge base with enhanced guidelines...")
        rag_kb = RAGKnowledgeBase()
        
        # Test search
        print("\n" + "=" * 80)
        print("TESTING KNOWLEDGE BASE")
        print("=" * 80)
        
        test_queries = [
            "SDG 6",
            "how to report complaint",
            "resolution time",
            "track complaint"
        ]
        
        for query in test_queries:
            print(f"\nSearching: '{query}'")
            results = rag_kb.search(query, top_k=3)
            if results:
                print(f"✓ Found {len(results)} results")
                print(f"  Top result: {results[0]['metadata'].get('title', 'N/A')}")
                print(f"  Distance: {results[0].get('distance', 'N/A'):.4f}")
            else:
                print("✗ No results found")
        
        print("\n" + "=" * 80)
        print("✓ KNOWLEDGE BASE REINITIALIZED SUCCESSFULLY")
        print("=" * 80)
        print("\nThe chatbot should now work properly with all new guidelines!")
        print("You can now test it by running: python test_chatbot_enhanced.py")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reinitialize_knowledge_base()

# Made with Bob
