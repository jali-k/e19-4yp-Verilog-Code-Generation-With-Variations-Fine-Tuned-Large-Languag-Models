#!/usr/bin/env python3
"""
Simple CLI for the Organized Xform RAG Pipeline
"""

import argparse
import logging
import sys
from pathlib import Path

from xform_rag import create_pipeline, RAGConfig


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Organized Xform RAG Pipeline - Generate Verilog transformations"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Setup the vector store")
    setup_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate a transformation")
    gen_parser.add_argument(
        "request", help="Description of the transformation to generate"
    )
    gen_parser.add_argument(
        "--save", "-s", action="store_true", help="Save generated code to file"
    )
    gen_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for similar examples")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--count", "-n", type=int, default=5, help="Number of results"
    )
    search_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show system statistics")
    stats_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    # Test command
    test_parser = subparsers.add_parser("test", help="Test system components")
    test_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    setup_logging(getattr(args, "verbose", False))

    try:
        # Create pipeline
        pipeline = create_pipeline()

        if args.command == "setup":
            print("🔧 Setting up vector store...")
            if pipeline.setup_vector_store():
                print("✅ Vector store setup completed successfully!")
            else:
                print("❌ Vector store setup failed!")
                return 1

        elif args.command == "generate":
            print(f"🚀 Generating transformation for: {args.request}")
            result = pipeline.generate_transformation(args.request)

            if result.get("success"):
                print("✅ Generation successful!")
                print(f"📝 Generated {len(result['code'])} characters of code")

                if args.save:
                    if pipeline.save_generated_code(result):
                        print(f"💾 Saved to: {result['filename']}")
                    else:
                        print("❌ Failed to save generated code")
                else:
                    print("\n--- Generated Code ---")
                    print(result["code"])
            else:
                print(f"❌ Generation failed: {result.get('error')}")
                return 1

        elif args.command == "search":
            print(f"🔍 Searching for: {args.query}")
            examples = pipeline.search_examples(args.query, args.count)

            if examples:
                print(f"Found {len(examples)} examples:")
                for i, example in enumerate(examples, 1):
                    print(f"\n{i}. {example['source']}")
                    print(f"   {example['content'][:200]}...")
            else:
                print("No examples found")

        elif args.command == "stats":
            print("📊 System Statistics:")
            stats = pipeline.get_system_stats()

            if "error" not in stats:
                doc_stats = stats.get("document_processor", {})
                vector_stats = stats.get("vector_store", {})
                config_stats = stats.get("config", {})

                print(f"  Xform files: {doc_stats.get('xform_files', 0)}")
                print(
                    f"  Documentation files: {doc_stats.get('documentation_files', 0)}"
                )
                print(
                    f"  Vector store documents: {vector_stats.get('total_documents', 0)}"
                )
                print(
                    f"  Embedding model: {config_stats.get('embedding_model', 'N/A')}"
                )
            else:
                print(f"❌ Error getting stats: {stats['error']}")

        elif args.command == "test":
            print("🧪 Testing system components...")
            results = pipeline.test_system()

            all_passed = True
            for component, passed in results.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {component}")
                if not passed:
                    all_passed = False

            if all_passed:
                print("🎉 All tests passed!")
            else:
                print("⚠️ Some tests failed")
                return 1

        return 0

    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
