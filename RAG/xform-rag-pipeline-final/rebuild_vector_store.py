#!/usr/bin/env python3
"""
Vector Store Rebuild Script - Fix embedding dimension mismatch
This script rebuilds the vector store with consistent embeddings
"""

import sys
import shutil
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from xform_rag.config import RAGConfig
from xform_rag.vector_store import VectorStoreManager


def rebuild_vector_store():
    """Rebuild vector store with consistent embeddings"""
    
    print("🔧 REBUILDING VECTOR STORE WITH CONSISTENT EMBEDDINGS")
    print("=" * 60)
    
    # Create optimized config
    config = RAGConfig(
        data_dir=Path("."),
        vector_store_dir=Path("./vector_store_fixed"),
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        embedding_type="sentence-transformers",
        model_name="qwen2.5-coder:1.5b"
    )
    
    print(f"📁 Data directory: {config.data_dir}")
    print(f"📊 Vector store: {config.vector_store_dir}")
    print(f"🤖 Embedding model: {config.embedding_model}")
    print(f"📏 Expected dimensions: 384 (all-MiniLM-L6-v2)")
    
    # Remove old vector store if it exists
    if config.vector_store_dir.exists():
        print(f"\\n🗑️  Removing old vector store...")
        shutil.rmtree(config.vector_store_dir)
    
    try:
        print("\\n🔄 Creating new vector store manager...")
        vector_manager = VectorStoreManager(config)
        
        print("📚 Loading documents...")
        vector_manager.load_documents()
        
        print("✅ Vector store rebuilt successfully!")
        
        # Test the vector store
        print("\\n🧪 Testing vector store...")
        docs = vector_manager.search_similar("wire to reg transformation", k=3)
        
        print(f"📊 Retrieved {len(docs)} documents")
        for i, doc in enumerate(docs):
            print(f"   {i+1}. {doc.metadata.get('source', 'Unknown')}")
            print(f"      Content preview: {doc.page_content[:100]}...")
        
        # Replace old vector store
        old_vector_store = Path("./vector_store")
        if old_vector_store.exists():
            print("\\n🔄 Replacing old vector store...")
            shutil.rmtree(old_vector_store)
            shutil.move(str(config.vector_store_dir), str(old_vector_store))
            print("✅ Vector store replacement complete!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error rebuilding vector store: {e}")
        return False


def check_xform_files():
    """Check available xform files for indexing"""
    
    print("\\n📂 CHECKING AVAILABLE XFORM FILES")
    print("=" * 40)
    
    # Check pyverilog_xform_framework directory
    xform_dir = Path("../../pyverilog_xform_framework")
    if xform_dir.exists():
        xform_files = list(xform_dir.glob("xform_*.py"))
        print(f"📁 Found {len(xform_files)} xform files in {xform_dir}")
        
        for file in xform_files[:10]:  # Show first 10
            print(f"   📄 {file.name}")
        
        if len(xform_files) > 10:
            print(f"   ... and {len(xform_files) - 10} more")
    else:
        print("⚠️  Xform framework directory not found")
    
    # Check current directory
    current_xform_files = list(Path(".").glob("**/xform_*.py"))
    print(f"\\n📁 Found {len(current_xform_files)} xform files in current directory tree")
    
    return len(xform_files) if 'xform_files' in locals() else 0


def validate_embedding_consistency():
    """Validate that embeddings are consistent"""
    
    print("\\n🔍 VALIDATING EMBEDDING CONSISTENCY")
    print("=" * 40)
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # Test the embedding model
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        
        # Test embedding dimensions
        test_text = "wire to reg transformation"
        embedding = model.encode([test_text])
        
        print(f"✅ Embedding model loaded successfully")
        print(f"📏 Embedding dimensions: {embedding.shape[1]}")
        print(f"🎯 Expected dimensions: 384")
        
        if embedding.shape[1] == 384:
            print("✅ Embedding dimensions are consistent!")
            return True
        else:
            print("❌ Embedding dimension mismatch!")
            return False
            
    except Exception as e:
        print(f"❌ Error validating embeddings: {e}")
        return False


if __name__ == "__main__":
    print("🚀 VECTOR STORE CONSISTENCY FIX")
    print("=" * 50)
    
    # Step 1: Check available files
    xform_count = check_xform_files()
    
    # Step 2: Validate embedding model
    embedding_valid = validate_embedding_consistency()
    
    if not embedding_valid:
        print("\\n❌ Cannot proceed with inconsistent embedding model")
        sys.exit(1)
    
    # Step 3: Rebuild vector store
    if xform_count > 0:
        success = rebuild_vector_store()
        
        if success:
            print("\\n🎉 VECTOR STORE REBUILD COMPLETE!")
            print("Your vector store now has consistent 384-dimensional embeddings")
            print("matching the sentence-transformers/all-MiniLM-L6-v2 model.")
        else:
            print("\\n❌ Vector store rebuild failed")
            sys.exit(1)
    else:
        print("\\n⚠️  No xform files found to index")
        print("Please ensure xform files are available in the correct directory")
    
    print("\\n🔥 NEXT STEPS:")
    print("1. Test the unbiased system with comprehensive test suite")
    print("2. Compare biased vs unbiased performance")
    print("3. Verify equal treatment across all transformation types")
