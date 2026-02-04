"""
Example usage of the ChromaDB Vector Database Interface.

This script demonstrates how to use the ChromaVectorDB class to add documents,
generate embeddings, and perform semantic search.
"""

from mind_q_agent.vector.chroma_vector import ChromaVectorDB


def main():
    """Demonstrate ChromaVectorDB usage."""
    
    # Initialize the database
    print("🔧 Initializing ChromaDB with embedding model...")
    # stored in data/vectors/mindq_chroma
    vector_db = ChromaVectorDB(
        './data/vectors/mindq_chroma', 
        model_name="all-MiniLM-L6-v2"
    )
    
    # Clean up previous runs
    try:
        if vector_db.count() > 0:
            print("Cleaning up previous collection...")
            vector_db.delete_collection()
            # Re-initialize collection
            vector_db = ChromaVectorDB(
                './data/vectors/mindq_chroma', 
                model_name="all-MiniLM-L6-v2"
            )
    except Exception as e:
        print(f"Cleanup note: {e}")
    
    # Add documents
    print("\n📝 Adding documents...")
    documents = [
        "Python is a high-level, interpreted programming language.",
        "Machine learning focuses on the use of data and algorithms to imitate the way that humans learn.",
        "Chroma is the open-source embedding database.",
        "Natural Language Processing (NLP) is a subfield of linguistics, computer science, and AI.",
        "Django is a high-level Python web framework that encourages rapid development."
    ]
    
    metadatas = [
        {"category": "programming", "source": "wiki"},
        {"category": "ai", "source": "wiki"},
        {"category": "database", "source": "docs"},
        {"category": "ai", "source": "wiki"},
        {"category": "programming", "source": "docs"}
    ]
    
    ids = [f"doc_{i}" for i in range(len(documents))]
    
    vector_db.add_documents(documents, metadatas, ids)
    print(f"✅ Added {vector_db.count()} documents")
    
    # Semantic Search Examples
    print("\n🔍 Running semantic searches...")
    
    queries = [
        "What is a web framework?",
        "Tell me about artificial intelligence",
        "How do I store embeddings?"
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        results = vector_db.query_similar(query, n_results=2)
        
        for i, res in enumerate(results):
            print(f"   {i+1}. [Dist: {res['distance']:.4f}] {res['document'][:100]}...")
            print(f"      Metadata: {res['metadata']}")
            
    # Metadata Filtering
    print("\n🔍 Query with metadata filter (category='programming')...")
    results = vector_db.query_similar(
        "web", 
        n_results=5, 
        where={"category": "programming"}
    )
    
    for i, res in enumerate(results):
        print(f"   {i+1}. {res['document'][:100]}...")
        print(f"      Metadata: {res['metadata']}")
        
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
