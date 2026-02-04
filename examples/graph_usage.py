"""
Example usage of the KùzuDB Graph Database Interface.

This script demonstrates how to use the KuzuGraphDB class to create
concepts, relationships, and query the knowledge graph.
"""

from mind_q_agent.graph.kuzu_graph import KuzuGraphDB


def main():
    """Demonstrate KuzuGraphDB usage."""
    
    # Initialize the database
    print("🔧 Initializing KùzuDB...")
    graph = KuzuGraphDB('./data/graph/mindq.db')
    
    # Create concepts
    print("\n📝 Creating concepts...")
    
    # Programming language concepts
    graph.create_concept("Python", [0.1] * 384, "programming_language")
    graph.create_concept("JavaScript", [0.15] * 384, "programming_language")
    
    # Framework concepts
    graph.create_concept("Django", [0.2] * 384, "framework")
    graph.create_concept("Flask", [0.25] * 384, "framework")
    graph.create_concept("React", [0.3] * 384, "framework")
    
    # General concepts
    graph.create_concept("Web Development", [0.4] * 384, "domain")
    graph.create_concept("REST API", [0.45] * 384, "concept")
    
    print(f"✅ Created {graph.get_node_count()} concepts")
    
    # Create relationships
    print("\n🔗 Creating relationships...")
    
    # Language -> Framework relationships
    graph.create_edge("Python", "Django", 0.9)
    graph.create_edge("Python", "Flask", 0.85)
    graph.create_edge("JavaScript", "React", 0.95)
    
    # Framework -> Concept relationships
    graph.create_edge("Django", "REST API", 0.8)
    graph.create_edge("Flask", "REST API", 0.75)
    graph.create_edge("React", "Web Development", 0.9)
    graph.create_edge("Django", "Web Development", 0.85)
    
    print(f"✅ Created {graph.get_edge_count()} relationships")
    
    # Query examples
    print("\n🔍 Running queries...")
    
    # Query 1: Find all frameworks related to Python
    print("\n1️⃣  Frameworks related to Python:")
    result = graph.execute("""
        MATCH (p:Concept {name: 'Python'})-[r:RELATED_TO]->(f:Concept)
        WHERE f.category = 'framework'
        RETURN f.name as framework, r.current_weight as strength
        ORDER BY r.current_weight DESC
    """)
    print(result.to_string(index=False))
    
    # Query 2: Find all concepts related to Web Development
    print("\n2️⃣  Concepts related to Web Development:")
    result = graph.execute("""
        MATCH (c:Concept)-[r:RELATED_TO]->(w:Concept {name: 'Web Development'})
        RETURN c.name as concept, c.category as category, r.current_weight as strength
        ORDER BY r.current_weight DESC
    """)
    print(result.to_string(index=False))
    
    # Query 3: Get a specific concept
    print("\n3️⃣  Details for 'Django':")
    django = graph.get_concept("Django")
    if django:
        print(f"   Name: {django['name']}")
        print(f"   Category: {django['category']}")
        print(f"   Frequency: {django['global_frequency']}")
        print(f"   Is Broad: {django['is_broad']}")
    
    # Statistics
    print("\n📊 Graph Statistics:")
    print(f"   Total Nodes: {graph.get_node_count()}")
    print(f"   Total Edges: {graph.get_edge_count()}")
    
    # Close connection
    print("\n👋 Closing connection...")
    graph.close()
    print("✅ Done!")


if __name__ == "__main__":
    main()
