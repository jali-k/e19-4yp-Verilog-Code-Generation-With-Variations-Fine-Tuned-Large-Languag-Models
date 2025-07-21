#!/usr/bin/env python3
"""
Context Data Viewer - View what information is being sent to the LLM
"""

import os
import json
import argparse
from datetime import datetime


def view_context_data(context_file=None):
    """View the context data from a specific file or the latest one"""

    context_dir = "generated/context_data"

    if not os.path.exists(context_dir):
        print("❌ No context data directory found. Run some generations first.")
        return

    # If no specific file provided, get the latest one
    if not context_file:
        context_files = [f for f in os.listdir(context_dir) if f.endswith(".json")]
        if not context_files:
            print("❌ No context files found.")
            return
        context_files.sort(reverse=True)  # Latest first
        context_file = os.path.join(context_dir, context_files[0])
        print(f"📁 Using latest context file: {context_files[0]}")
    else:
        context_file = os.path.join(context_dir, context_file)

    # Load and display context data
    try:
        with open(context_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"\n{'='*80}")
        print(f"CONTEXT DATA ANALYSIS")
        print("=" * 80)

        # Basic info
        print(f"🕒 Timestamp: {data.get('timestamp', 'N/A')}")
        print(f"❓ User Request: {data.get('user_request', 'N/A')}")
        print(f"🔍 Search Results: {data.get('search_results_count', 0)} total")

        # Focused context analysis
        focused = data.get("focused_context", {})
        print(f"\n📊 FOCUSED CONTEXT BREAKDOWN:")
        print(f"🎯 Best Xform File: {focused.get('best_xform_file', 'N/A')}")

        # Primary xform
        primary = focused.get("primary_xform")
        if primary:
            print(f"✅ Primary Xform Found: {primary.get('source', 'N/A')}")
            print(f"   Content Length: {len(primary.get('content', ''))} chars")
        else:
            print("❌ No primary xform identified")

        # Supporting docs
        docs = focused.get("supporting_docs", [])
        print(f"📚 Supporting Docs: {len(docs)} documents")
        for i, doc in enumerate(docs):
            print(
                f"   {i+1}. {doc.get('source', 'N/A')} ({len(doc.get('content', ''))} chars)"
            )

        # Other xforms
        other_xforms = focused.get("other_xforms", [])
        print(f"🔧 Other Xforms: {len(other_xforms)} files")
        for i, xform in enumerate(other_xforms):
            print(
                f"   {i+1}. {xform.get('source', 'N/A')} ({len(xform.get('content', ''))} chars)"
            )

        print(f"\n{'='*80}")
        print("WHAT WAS SENT TO LLM:")
        print("=" * 80)

        # Show what would be sent to LLM
        if primary:
            print("🎯 PRIMARY REFERENCE XFORM (HIGHEST PRIORITY):")
            print(f"File: {primary.get('source', 'N/A')}")
            print(f"Content: {primary.get('content', '')[:200]}...")
            print()

        if docs:
            print("📚 SUPPORTING DOCUMENTATION:")
            for doc in docs[:2]:  # Show first 2 docs
                print(f"Source: {doc.get('source', 'N/A')}")
                print(f"Content: {doc.get('content', '')[:200]}...")
                print()

        if other_xforms:
            print("🔧 SECONDARY REFERENCE XFORMS:")
            for xform in other_xforms[:2]:  # Show first 2 xforms
                print(f"File: {xform.get('source', 'N/A')}")
                print(f"Content: {xform.get('content', '')[:200]}...")
                print()

        # Raw search results summary
        print(f"{'='*80}")
        print("RAW SEARCH RESULTS SUMMARY:")
        print("=" * 80)

        raw_results = data.get("raw_search_results", [])
        for i, result in enumerate(raw_results):
            source = result.get("source", "N/A")
            content_len = len(result.get("content", ""))
            print(f"{i+1:2d}. {source} ({content_len} chars)")

    except Exception as e:
        print(f"❌ Error reading context file: {e}")


def list_context_files():
    """List all available context files"""
    context_dir = "generated/context_data"

    if not os.path.exists(context_dir):
        print("❌ No context data directory found.")
        return

    context_files = [f for f in os.listdir(context_dir) if f.endswith(".json")]
    if not context_files:
        print("❌ No context files found.")
        return

    context_files.sort(reverse=True)  # Latest first

    print(f"\n📁 Available Context Files ({len(context_files)} total):")
    print("=" * 80)

    for i, filename in enumerate(context_files):
        # Extract timestamp and request from filename
        parts = filename.replace("context_", "").replace(".json", "").split("_", 1)
        if len(parts) >= 2:
            timestamp = parts[0]
            request = parts[1].replace("_", " ")[:50]
            print(f"{i+1:2d}. {filename}")
            print(f"    🕒 {timestamp} | ❓ {request}...")
        else:
            print(f"{i+1:2d}. {filename}")
        print()


def main():
    parser = argparse.ArgumentParser(description="View context data sent to LLM")
    parser.add_argument("--file", "-f", help="Specific context file to view")
    parser.add_argument(
        "--list", "-l", action="store_true", help="List all context files"
    )

    args = parser.parse_args()

    if args.list:
        list_context_files()
    else:
        view_context_data(args.file)


if __name__ == "__main__":
    main()
