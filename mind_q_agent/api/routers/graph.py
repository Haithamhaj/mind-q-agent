from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import logging

from mind_q_agent.graph.kuzu_graph import KuzuGraphDB
from mind_q_agent.api.settings import settings

router = APIRouter(
    prefix="/graph",
    tags=["graph"]
)

logger = logging.getLogger(__name__)

# Singleton wrapper
try:
    graph_db = KuzuGraphDB(settings.KUZU_DB_PATH)
except Exception as e:
    logger.error(f"Failed to initialize Graph DB: {e}")
    graph_db = None

@router.get("/analytics")
def get_analytics():
    """
    Get detailed breakdown of system statistics.
    """
    if not graph_db:
        raise HTTPException(status_code=500, detail="Graph DB not initialized")
    
    try:
        node_count = graph_db.get_node_count()
        edge_count = graph_db.get_edge_count()
        top_concepts = graph_db.get_top_concepts(limit=10)
        recent_docs = graph_db.get_recent_documents(limit=5)
        
        return {
            "summary": {
                "total_nodes": node_count,
                "total_edges": edge_count,
            },
            "top_concepts": top_concepts,
            "recent_documents": recent_docs
        }
    except Exception as e:
        logger.error(f"Analytics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
def get_graph_stats():
    """
    Get detailed statistics about the knowledge graph.
    """
    if not graph_db:
        raise HTTPException(status_code=500, detail="Graph DB not initialized")
    
    try:
        node_count = graph_db.get_node_count()
        edge_count = graph_db.get_edge_count()
        
        # Get counts per label if possible (custom query)
        # Kuzu doesn't have a simple "show all labels" meta query like Neo4j's db.labels() easily accessible via SQL yet?
        # We'll stick to basic counts for now.
        
        return {
            "nodes": node_count,
            "edges": edge_count,
            "status": "healthy"
        }
    except Exception as e:
        logger.error(f"Graph stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/visualize")
def get_graph_visualization(limit: int = 100):
    """
    Get graph data in Cytoscape JSON format for visualization.
    """
    if not graph_db:
        raise HTTPException(status_code=500, detail="Graph DB not initialized")

    try:
        # Fetch nodes (Documents and Concepts)
        # Limiting to most recent Documents and most connected Concepts/Entities
        
        elements = []
        
        # 1. Get recent Documents
        doc_query = f"""
            MATCH (d:Document)
            RETURN d.hash as id, d.title as label, 'Document' as type
            LIMIT {limit // 2}
        """
        docs_df = graph_db.execute(doc_query)
        
        doc_ids = set()
        for _, row in docs_df.iterrows():
            doc_ids.add(row['id'])
            elements.append({
                "data": {
                    "id": row['id'],
                    "label": row['label'],
                    "type": "Document"
                }
            })
            
        # 2. Get Concepts connected to these documents or generally popular
        # For simplicity, let's get concepts connected to the fetched documents
        # OR just top concepts if no documents found
        
        if not doc_ids:
             concept_query = f"""
                MATCH (c:Concept)
                RETURN c.name as id, c.name as label, c.category as category
                LIMIT {limit}
            """
             concepts_df = graph_db.execute(concept_query)
             for _, row in concepts_df.iterrows():
                 elements.append({
                     "data": {
                         "id": row['id'],
                         "label": row['label'],
                         "type": "Concept",
                         "category": row['category']
                     }
                 })
             return elements

        # Get edges and connected concepts for the retrieved documents
        # Kuzu support for "IN" list param might be tricky, so we limit query complexity
        # We'll just get *some* DISCUSSES edges
        
        edge_query = f"""
            MATCH (d:Document)-[r:DISCUSSES]->(c:Concept)
            RETURN d.hash as source, c.name as target
            LIMIT {limit}
        """
        # Note: We should filter to only include source d in doc_ids, but for now simple query is safer
        
        edges_df = graph_db.execute(edge_query)
        
        added_nodes = doc_ids.copy()
        
        for _, row in edges_df.iterrows():
            source = row['source']
            target = row['target']
            
            # If we haven't added the concept node yet, add it
            if target not in added_nodes:
                elements.append({
                    "data": {
                        "id": target,
                        "label": target, # Concept name is ID and Label
                        "type": "Concept"
                    }
                })
                added_nodes.add(target)
            
            # Add Edge
            elements.append({
                "data": {
                    "source": source,
                    "target": target,
                    "label": "DISCUSSES"
                }
            })
            
        return elements

    except Exception as e:
        logger.error(f"Graph viz failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
