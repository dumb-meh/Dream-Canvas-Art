"""
🗑️ Automated Media Cleanup Script
Reads test_results_urls.txt and deletes all generated media from Google Cloud Storage
"""

import os
import re
import sys
from datetime import datetime
from typing import List, Dict
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
RESULTS_FILE = "test_results_urls.txt"
GCS_BUCKET_PATTERN = r"https://storage\.googleapis\.com/([^/]+)/(.+)"


class MediaCleanup:
    """Cleanup utility for deleting test media from GCS"""
    
    def __init__(self, results_file: str):
        self.results_file = results_file
        self.urls_to_delete: List[Dict] = []
        self.deleted_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        
        # Initialize GCS client
        try:
            from google.cloud import storage
            
            # Set credentials if specified in .env
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if credentials_path and os.path.exists(credentials_path):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
                self.storage_client = storage.Client()
                print(f"✅ Google Cloud Storage client initialized with credentials: {credentials_path}")
            else:
                print("⚠️  GOOGLE_APPLICATION_CREDENTIALS not found or file doesn't exist")
                print("   Attempting to use default credentials...")
                self.storage_client = storage.Client()
                print("✅ Google Cloud Storage client initialized with default credentials")
        except Exception as e:
            print(f"❌ Failed to initialize GCS client: {e}")
            print("   Make sure GOOGLE_APPLICATION_CREDENTIALS is set in your .env file")
            print("   Or ensure Application Default Credentials are configured")
            sys.exit(1)
    
    def parse_results_file(self):
        """Parse the test results file and extract all GCS URLs"""
        print(f"\n📖 Reading {self.results_file}...")
        
        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"❌ File not found: {self.results_file}")
            print("   Run the test suite first to generate this file")
            sys.exit(1)
        
        # Extract all URLs that match GCS pattern
        for line in content.split('\n'):
            if line.startswith('URL: https://storage.googleapis.com/'):
                url = line.replace('URL: ', '').strip()
                match = re.match(GCS_BUCKET_PATTERN, url)
                
                if match:
                    bucket_name = match.group(1)
                    blob_path = match.group(2)
                    
                    self.urls_to_delete.append({
                        'url': url,
                        'bucket': bucket_name,
                        'path': blob_path
                    })
        
        print(f"✅ Found {len(self.urls_to_delete)} media files to delete")
        
        if len(self.urls_to_delete) == 0:
            print("⚠️  No GCS URLs found in the results file")
            print("   The file may only contain local URLs or no successful tests")
    
    def display_files(self):
        """Display all files that will be deleted"""
        if not self.urls_to_delete:
            return
        
        print("\n" + "=" * 80)
        print("📋 FILES TO BE DELETED")
        print("=" * 80)
        
        # Group by media type
        images = [f for f in self.urls_to_delete if '/image/' in f['path']]
        videos = [f for f in self.urls_to_delete if '/video/' in f['path']]
        audio = [f for f in self.urls_to_delete if '/audio/' in f['path']]
        
        if images:
            print(f"\n🖼️  Images ({len(images)}):")
            for img in images:
                filename = img['path'].split('/')[-1]
                print(f"   - {filename}")
        
        if videos:
            print(f"\n🎬 Videos ({len(videos)}):")
            for vid in videos:
                filename = vid['path'].split('/')[-1]
                print(f"   - {filename}")
        
        if audio:
            print(f"\n🎵 Audio ({len(audio)}):")
            for aud in audio:
                filename = aud['path'].split('/')[-1]
                print(f"   - {filename}")
        
        print("\n" + "=" * 80)
    
    def delete_files(self, dry_run: bool = False):
        """Delete all files from GCS"""
        if not self.urls_to_delete:
            print("\n⚠️  No files to delete")
            return
        
        if dry_run:
            print("\n🔍 DRY RUN MODE - No files will be deleted")
            print("=" * 80)
        else:
            print("\n🗑️  Starting deletion process...")
            print("=" * 80)
        
        for item in self.urls_to_delete:
            bucket_name = item['bucket']
            blob_path = item['path']
            filename = blob_path.split('/')[-1]
            
            try:
                if dry_run:
                    print(f"[DRY RUN] Would delete: {filename}")
                    self.deleted_count += 1
                else:
                    # Get bucket and blob
                    bucket = self.storage_client.bucket(bucket_name)
                    blob = bucket.blob(blob_path)
                    
                    # Check if blob exists
                    if blob.exists():
                        blob.delete()
                        print(f"✅ Deleted: {filename}")
                        self.deleted_count += 1
                    else:
                        print(f"⚠️  Not found (already deleted?): {filename}")
                        self.skipped_count += 1
                        
            except Exception as e:
                print(f"❌ Failed to delete {filename}: {str(e)}")
                self.failed_count += 1
    
    def print_summary(self, dry_run: bool = False):
        """Print deletion summary"""
        print("\n" + "=" * 80)
        print("📊 CLEANUP SUMMARY")
        print("=" * 80)
        
        if dry_run:
            print(f"🔍 DRY RUN MODE")
            print(f"   Files that would be deleted: {self.deleted_count}")
        else:
            print(f"✅ Successfully deleted: {self.deleted_count}")
            print(f"⚠️  Skipped (not found): {self.skipped_count}")
            print(f"❌ Failed: {self.failed_count}")
            print(f"📊 Total processed: {len(self.urls_to_delete)}")
        
        print("=" * 80)
    
    def cleanup(self, dry_run: bool = False, auto_confirm: bool = False):
        """Main cleanup workflow"""
        print("\n" + "=" * 80)
        print("🗑️  MEDIA CLEANUP UTILITY")
        print("=" * 80)
        print(f"Target file: {self.results_file}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Parse file
        self.parse_results_file()
        
        if not self.urls_to_delete:
            return
        
        # Display files
        self.display_files()
        
        # Confirm deletion
        if not auto_confirm and not dry_run:
            print("\n⚠️  WARNING: This action cannot be undone!")
            response = input("Are you sure you want to delete these files? (yes/no): ")
            
            if response.lower() != 'yes':
                print("\n❌ Deletion cancelled by user")
                return
        
        # Delete files
        self.delete_files(dry_run=dry_run)
        
        # Print summary
        self.print_summary(dry_run=dry_run)
        
        if not dry_run:
            print("\n✅ Cleanup completed!")


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Delete test media files from Google Cloud Storage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run - see what would be deleted without actually deleting
  python delete_test_media.py --dry-run
  
  # Delete files with confirmation prompt
  python delete_test_media.py
  
  # Delete files without confirmation (use with caution!)
  python delete_test_media.py --yes
  
  # Use custom results file
  python delete_test_media.py --file custom_results.txt
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        default=RESULTS_FILE,
        help=f'Path to results file (default: {RESULTS_FILE})'
    )
    
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Preview what would be deleted without actually deleting'
    )
    
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Skip confirmation prompt (auto-confirm deletion)'
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    if not Path(args.file).exists():
        print(f"❌ Error: File not found: {args.file}")
        print("   Run the test suite first with: python test_all_endpoints.py")
        sys.exit(1)
    
    # Run cleanup
    cleanup = MediaCleanup(args.file)
    
    try:
        cleanup.cleanup(dry_run=args.dry_run, auto_confirm=args.yes)
    except KeyboardInterrupt:
        print("\n\n⚠️  Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
