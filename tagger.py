#!/usr/bin/env python3

"""
WordPress Image Alt Text Generator

This script connects to a WordPress site's API, retrieves media items,
and generates alt text for images missing it using OpenAI's API.
It can operate in dry-run mode (default) or update mode.

Usage:
    python tagger.py <wordpress_url> [model] [mode] [limit]
    
Arguments:
    wordpress_url : Required - The base URL of the WordPress site
    model        : Optional - OpenAI model to use (default: gpt-4-vision-preview)
    mode         : Optional - 'dry-run' or 'update' (default: dry-run)
    limit        : Optional - Number of images to process (default: 10, 0 for all)
"""

import os
import sys
import csv
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI
import json
from urllib.parse import urljoin

# Load environment variables
load_dotenv()

def display_usage():
    """Display script usage information."""
    print("""
Usage: python tagger.py <wordpress_url> [model] [mode] [limit]

Arguments:
    wordpress_url : Required - The base URL of the WordPress site
    model        : Optional - OpenAI model to use (default: gpt-4o-mini)
    mode         : Optional - 'dry-run' or 'update' (default: dry-run)
    limit        : Optional - Number of images to process (default: 10, 0 for all)

Example:
    python tagger.py https://example.com gpt-4 update 20
    """)
    sys.exit(1)

def validate_arguments(args: List[str]) -> tuple:
    """
    Validate and process command line arguments.
    
    Args:
        args: List of command line arguments
        
    Returns:
        tuple: (wordpress_url, model, mode, limit)
    """
    if len(args) < 2:
        display_usage()
        
    wordpress_url = args[1]
    model = args[2] if len(args) > 2 else "gpt-4o-mini"
    mode = args[3] if len(args) > 3 else "dry-run"
    limit = int(args[4]) if len(args) > 4 else 10
    
    if mode not in ["dry-run", "update"]:
        print("Error: mode must be either 'dry-run' or 'update'")
        sys.exit(1)
        
    return wordpress_url, model, mode, limit

def get_wordpress_media(base_url: str, limit: int) -> List[Dict]:
    """
    Retrieve media items from WordPress API with pagination support.
    
    Args:
        base_url: WordPress site URL
        limit: Maximum number of items to retrieve (0 for all)
        
    Returns:
        List of media items
    """
    api_url = urljoin(base_url, "wp-json/wp/v2/media")
    media_items = []
    page = 1
    per_page = 100  # Maximum allowed by WordPress
    
    while True:
        params = {
            "page": page,
            "per_page": per_page
        }
        
        response = requests.get(api_url, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching media items: {response.status_code}")
            break
            
        items = response.json()
        if not items:
            break
            
        media_items.extend(items)
        
        # Check if we've reached the limit
        if limit > 0 and len(media_items) >= limit:
            media_items = media_items[:limit]
            break
            
        page += 1
    
    return media_items

def generate_alt_text(client: OpenAI, image_url: str, model: str) -> str:
    """
    Generate alt text for an image using OpenAI's Vision API.
    
    Args:
        client: OpenAI client instance
        image_url: URL of the image
        model: OpenAI model to use
        
    Returns:
        Generated alt text
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at writing descriptive, concise alt text for images. "
                              "Provide only the alt text, without any additional explanation or context."
                              "If the image is decorative, return 'Decorative image ' with a brief description of the image."
                              "Be concise. You don't need to write complete sentences. The output should be a single line of text."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Please write appropriate alt text for this image:"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                            },
                        },
                    ],
                }
            ],
            max_tokens=100  # Limiting tokens for concise alt text
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating alt text: {e}")
        return ""

def main():
    """Main execution function."""
    # Validate environment variables
    if not os.getenv("API_KEY_OPENAI"):
        print("Error: API_KEY_OPENAI not found in .env file")
        sys.exit(1)

    # Process command line arguments
    wordpress_url, model, mode, limit = validate_arguments(sys.argv)
    
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("API_KEY_OPENAI"))
    
    # Fetch media items
    print(f"Fetching media items from {wordpress_url}...")
    media_items = get_wordpress_media(wordpress_url, limit)
    
    # Filter for images missing alt text
    images_missing_alt = [
        item for item in media_items
        if item["media_type"] == "image" and not item.get("alt_text")
    ]
    
    print(f"Found {len(images_missing_alt)} images missing alt text")
    
    # Prepare CSV output
    output_file = "image_alt_text_results.csv"
    fieldnames = ["id", "title", "original_alt", "generated_alt", "url"]
    
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in images_missing_alt:
            print(f"Processing image ID {item['id']}...")
            
            # Generate alt text
            generated_alt = generate_alt_text(
                client,
                item["source_url"],
                model
            )
            
            # Write to CSV
            writer.writerow({
                "id": item["id"],
                "title": item["title"]["rendered"],
                "original_alt": item.get("alt_text", ""),
                "generated_alt": generated_alt,
                "url": item["source_url"]
            })
            
            if mode == "update":
                # TODO: Implement WordPress update functionality
                print("Update mode not yet implemented")
    
    print(f"Results written to {output_file}")

if __name__ == "__main__":
    main()