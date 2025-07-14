#!/usr/bin/env python3
"""
Command Line Interface for the Xform RAG Pipeline
"""

import argparse
import sys
import json
from pathlib import Path

from .config import RAGConfig
from .pipeline import XformRAGPipeline


class CLI:
    """Command line interface for the RAG pipeline"""

    def __init__(self):
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser"""
        parser = argparse.ArgumentParser(
            description="Xform RAG Pipeline - Generate Verilog transformations using AI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s generate "Add debug output ports to a module"
  %(prog)s list
  %(prog)s update
  %(prog)s stats
  %(prog)s --model-type ollama --model-name codellama generate "Convert register to wire"
            """,
        )

        # Global options
        parser.add_argument(
            "--data-dir",
            default=".",
            help="Directory containing xform files (default: current directory)",
        )
        parser.add_argument(
            "--vector-store-dir",
            default="./vector_store",
            help="Vector store directory (default: ./vector_store)",
        )
        parser.add_argument(
            "--output-dir",
            default="./generated",
            help="Output directory for generated xforms (default: ./generated)",
        )
        parser.add_argument(
            "--model-type",
            choices=["ollama", "ec2"],
            default="ollama",
            help="Model type (default: ollama)",
        )
        parser.add_argument(
            "--model-name", default="codellama", help="Model name (default: codellama)"
        )
        parser.add_argument(
            "--ec2-endpoint", help="EC2 endpoint URL (required for ec2 model type)"
        )
        parser.add_argument("--config-file", help="Load configuration from JSON file")
        parser.add_argument(
            "--verbose", "-v", action="store_true", help="Enable verbose logging"
        )

        # Subcommands
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Generate command
        gen_parser = subparsers.add_parser(
            "generate", help="Generate new xform transformation"
        )
        gen_parser.add_argument(
            "request", help="Description of the transformation needed"
        )
        gen_parser.add_argument(
            "--validate", action="store_true", help="Validate generated code"
        )
        gen_parser.add_argument(
            "--dry-run", action="store_true", help="Generate but don't save the file"
        )

        # Update command
        update_parser = subparsers.add_parser(
            "update", help="Update vector store with new documents"
        )
        update_parser.add_argument(
            "--force",
            action="store_true",
            help="Force update even if vector store exists",
        )

        # List command
        list_parser = subparsers.add_parser("list", help="List known transformations")
        list_parser.add_argument(
            "--format",
            choices=["simple", "detailed", "json"],
            default="simple",
            help="Output format",
        )

        # Stats command
        stats_parser = subparsers.add_parser("stats", help="Show system statistics")
        stats_parser.add_argument(
            "--format", choices=["text", "json"], default="text", help="Output format"
        )

        # Validate command
        validate_parser = subparsers.add_parser(
            "validate", help="Validate generated files"
        )
        validate_parser.add_argument(
            "filename", nargs="?", help="Specific file to validate (optional)"
        )

        # Test command
        test_parser = subparsers.add_parser("test", help="Test system connectivity")

        # Cleanup command
        cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old files")
        cleanup_parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Remove files older than N days (default: 30)",
        )
        cleanup_parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be removed without actually removing",
        )

        return parser

    def run(self, args=None):
        """Run the CLI with given arguments"""
        parsed_args = self.parser.parse_args(args)

        try:
            # Load configuration
            config = self._load_config(parsed_args)

            # Setup logging
            self._setup_logging(parsed_args.verbose)

            # Execute command
            return self._execute_command(config, parsed_args)

        except KeyboardInterrupt:
            print("\n🛑 Operation cancelled by user")
            return 1
        except Exception as e:
            print(f"❌ Error: {e}")
            if parsed_args.verbose:
                import traceback

                traceback.print_exc()
            return 1

    def _load_config(self, args) -> RAGConfig:
        """Load configuration from arguments and config file"""
        config_dict = {}

        # Load from config file if specified
        if args.config_file:
            config_path = Path(args.config_file)
            if not config_path.exists():
                raise FileNotFoundError(f"Config file not found: {args.config_file}")

            with open(config_path) as f:
                config_dict = json.load(f)

        # Override with command line arguments
        arg_dict = {
            "data_dir": args.data_dir,
            "vector_store_dir": args.vector_store_dir,
            "output_dir": args.output_dir,
            "model_type": args.model_type,
            "model_name": args.model_name,
        }

        if args.ec2_endpoint:
            arg_dict["ec2_endpoint"] = args.ec2_endpoint

        # Merge configurations (command line takes precedence)
        config_dict.update(arg_dict)

        config = RAGConfig.from_dict(config_dict)
        config.validate()

        return config

    def _setup_logging(self, verbose: bool):
        """Setup logging configuration"""
        import logging

        level = logging.DEBUG if verbose else logging.INFO
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        logging.basicConfig(level=level, format=format_str)

        # Suppress some noisy loggers
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("chromadb").setLevel(logging.WARNING)

    def _execute_command(self, config: RAGConfig, args) -> int:
        """Execute the specified command"""
        if not args.command:
            self.parser.print_help()
            return 1

        # Initialize pipeline
        pipeline = XformRAGPipeline(config)

        # Route to appropriate handler
        handlers = {
            "generate": self._handle_generate,
            "update": self._handle_update,
            "list": self._handle_list,
            "stats": self._handle_stats,
            "validate": self._handle_validate,
            "test": self._handle_test,
            "cleanup": self._handle_cleanup,
        }

        handler = handlers.get(args.command)
        if handler:
            return handler(pipeline, args)
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1

    def _handle_generate(self, pipeline: XformRAGPipeline, args) -> int:
        """Handle generate command"""
        print(f"🚀 Generating transformation for: {args.request}")

        result = pipeline.generate_xform(args.request)

        if "error" in result:
            print(f"❌ Generation failed: {result['error']}")
            return 1

        # Validate if requested
        if args.validate:
            validation = pipeline.code_generator.validate_generated_code(result["code"])
            if not validation["is_valid"]:
                print(f"⚠️ Generated code has issues:")
                for error in validation["syntax_errors"]:
                    print(f"  - {error}")
                for warning in validation["warnings"]:
                    print(f"  - Warning: {warning}")

        # Save unless dry run
        if not args.dry_run:
            if pipeline.file_manager.save_generated_xform(result):
                print(f"✅ Successfully generated: {result['filename']}")
                if result.get("registry_entry"):
                    print(f"📝 Registry entry:\n{result['registry_entry']}")
            else:
                print("❌ Failed to save generated xform")
                return 1
        else:
            print(f"🔍 Dry run - would generate: {result['filename']}")
            print(f"📊 Code length: {len(result['code'])} characters")

        return 0

    def _handle_update(self, pipeline: XformRAGPipeline, args) -> int:
        """Handle update command"""
        print("🔄 Updating vector store...")

        if pipeline.vector_store_manager.update_vector_store():
            print("✅ Vector store updated successfully!")
            return 0
        else:
            print("❌ Vector store update failed!")
            return 1

    def _handle_list(self, pipeline: XformRAGPipeline, args) -> int:
        """Handle list command"""
        transformations = pipeline.vector_store_manager.list_transformations()

        if args.format == "json":
            print(json.dumps(transformations, indent=2))
        elif args.format == "detailed":
            print(f"📋 Found {len(transformations)} transformations:")
            for xform in transformations:
                print(f"  • {xform}")
        else:  # simple
            print("Known transformations:")
            for xform in transformations:
                print(f"  {xform}")

        return 0

    def _handle_stats(self, pipeline: XformRAGPipeline, args) -> int:
        """Handle stats command"""
        vs_stats = pipeline.vector_store_manager.get_stats()
        file_stats = pipeline.file_manager.get_generation_stats()

        stats = {"vector_store": vs_stats, "generated_files": file_stats}

        if args.format == "json":
            print(json.dumps(stats, indent=2))
        else:
            print("📊 System Statistics")
            print("=" * 50)
            print(
                f"Vector Store Documents: {vs_stats.get('vector_store_documents', 'N/A')}"
            )
            print(f"Source Files: {vs_stats.get('xform_files', 'N/A')}")
            print(f"Generated Files: {file_stats.get('total_files', 0)}")
            print(
                f"Total Generated Size: {file_stats.get('total_size_bytes', 0)} bytes"
            )

        return 0

    def _handle_validate(self, pipeline: XformRAGPipeline, args) -> int:
        """Handle validate command"""
        if args.filename:
            # Validate specific file
            result = pipeline.file_manager.validate_generated_file(args.filename)
            if "error" in result:
                print(f"❌ {result['error']}")
                return 1

            print(f"📁 File: {result['filename']}")
            print(f"✅ Exists: {result['exists']}")
            print(f"📏 Size: {result['size']} bytes")
            print(f"🔧 Executable: {result['is_executable']}")
            print(f"✅ Valid Syntax: {result['syntax_valid']}")

            if not result["syntax_valid"] and "syntax_error" in result:
                print(f"❌ Syntax Error: {result['syntax_error']}")
        else:
            # Validate all files
            files = pipeline.file_manager.list_generated_files()
            valid_count = 0

            for file_info in files:
                result = pipeline.file_manager.validate_generated_file(
                    file_info["filename"]
                )
                if result.get("syntax_valid", False):
                    valid_count += 1
                    print(f"✅ {file_info['filename']}")
                else:
                    print(f"❌ {file_info['filename']}")

            print(f"\n📊 {valid_count}/{len(files)} files are valid")

        return 0

    def _handle_test(self, pipeline: XformRAGPipeline, args) -> int:
        """Handle test command"""
        print("🧪 Testing system connectivity...")

        if pipeline.code_generator.test_connection():
            print("✅ All systems operational!")
            return 0
        else:
            print("❌ System test failed!")
            return 1

    def _handle_cleanup(self, pipeline: XformRAGPipeline, args) -> int:
        """Handle cleanup command"""
        if args.dry_run:
            print(f"🔍 Dry run - would remove files older than {args.days} days")
            # TODO: Implement dry run logic
            return 0

        removed = pipeline.file_manager.cleanup_old_files(args.days)
        print(f"🧹 Removed {removed} old files")
        return 0


def main():
    """Main entry point for CLI"""
    cli = CLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
