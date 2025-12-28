"""
ColdExperience CMS Client for JARVIS
====================================
Provides tools for JARVIS to interact with the ColdExperience CMS.

The CMS uses these tables:
- cms_pages: Page definitions (id, slug, name, description)
- cms_content: Content items (page_id, section, content_key, content_sv, content_en, etc.)
- cms_packages: Package/pricing data
- cms_settings: Site settings
"""

import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

try:
    from supabase import create_client, Client
except ImportError:
    raise ImportError("Please install supabase-py: pip install supabase")


class CmsClient:
    """Client for interacting with ColdExperience CMS Supabase."""
    
    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None
    ):
        self.url = url or os.getenv("CMS_SUPABASE_URL")
        self.key = key or os.getenv("CMS_SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.url or not self.key:
            raise ValueError(
                "CMS Supabase URL and key are required. "
                "Set CMS_SUPABASE_URL and CMS_SUPABASE_SERVICE_ROLE_KEY environment variables."
            )
        
        self.client: Client = create_client(self.url, self.key)
    
    # =========================================
    # PAGE FUNCTIONS
    # =========================================
    
    def get_pages(self) -> List[Dict[str, Any]]:
        """Get all CMS pages."""
        result = self.client.table("cms_pages").select("*").order("display_order").execute()
        return result.data if result.data else []
    
    def get_page(self, page_id: str = None, slug: str = None) -> Optional[Dict[str, Any]]:
        """Get a specific page by ID or slug."""
        query = self.client.table("cms_pages").select("*")
        
        if page_id:
            query = query.eq("id", page_id)
        elif slug:
            query = query.eq("slug", slug)
        else:
            return None
            
        result = query.execute()
        return result.data[0] if result.data else None
    
    # =========================================
    # CONTENT FUNCTIONS
    # =========================================
    
    def get_sections(self, page_slug: str = None) -> List[Dict[str, Any]]:
        """
        Get all unique sections from cms_content.
        
        Args:
            page_slug: Optional page slug to filter sections
            
        Returns:
            List of unique section names for the page
        """
        if page_slug:
            # First get the page ID
            page = self.get_page(slug=page_slug)
            if not page:
                return []
            
            result = self.client.table("cms_content").select(
                "section"
            ).eq("page_id", page["id"]).execute()
        else:
            result = self.client.table("cms_content").select("section").execute()
        
        if not result.data:
            return []
        
        # Get unique sections
        sections = list(set(item["section"] for item in result.data if item.get("section")))
        return [{"key": s, "name": s.replace("_", " ").title()} for s in sorted(sections)]
    
    def get_content(
        self,
        section_key: str = None,
        page_slug: str = None,
        language: str = "sv"
    ) -> Dict[str, Any]:
        """
        Get content for a section or page.
        
        Args:
            section_key: Section name (e.g., "hero", "about")
            page_slug: Page slug (e.g., "home", "about")  
            language: Language code ("sv" or "en")
            
        Returns:
            Content dictionary with field names as keys
        """
        query = self.client.table("cms_content").select("*")
        
        # Filter by page if provided
        if page_slug:
            page = self.get_page(slug=page_slug)
            if page:
                query = query.eq("page_id", page["id"])
        
        # Filter by section if provided
        if section_key:
            query = query.eq("section", section_key)
        
        result = query.order("display_order").execute()
        
        if not result.data:
            return {}
        
        # Build content dictionary
        content = {}
        lang_field = f"content_{language}"
        
        for item in result.data:
            # Extract field name from content_key (format: "section.fieldKey")
            content_key = item.get("content_key", "")
            if "." in content_key:
                field_name = content_key.split(".", 1)[1]
            else:
                field_name = content_key
            
            content[field_name] = item.get(lang_field) or item.get("content_en") or ""
        
        return content
    
    def update_content(
        self,
        section_key: str,
        field: str,
        value: Any,
        language: str = "sv",
        page_slug: str = None
    ) -> Dict[str, Any]:
        """
        Update a specific content field.
        
        Args:
            section_key: Section name
            field: Field name to update
            value: New value
            language: Language code
            page_slug: Page slug (optional, helps narrow down)
            
        Returns:
            Updated content data
        """
        content_key = f"{section_key}.{field}"
        lang_field = f"content_{language}"
        
        # Build query to find the content item
        query = self.client.table("cms_content").select("*").eq(
            "content_key", content_key
        )
        
        if page_slug:
            page = self.get_page(slug=page_slug)
            if page:
                query = query.eq("page_id", page["id"])
        
        existing = query.execute()
        
        if not existing.data:
            raise ValueError(f"Content not found: {content_key}")
        
        # Update the content
        result = self.client.table("cms_content").update({
            lang_field: value
        }).eq("id", existing.data[0]["id"]).execute()
        
        return result.data[0] if result.data else None
    
    def get_all_content(self, language: str = "sv") -> Dict[str, Any]:
        """
        Get all content organized by page and section.
        
        Returns:
            Dictionary with structure: {page_slug: {section_key: {field: value}}}
        """
        pages = self.get_pages()
        
        result = {}
        for page in pages:
            page_slug = page["slug"]
            result[page_slug] = {}
            
            # Get content for this page
            content_result = self.client.table("cms_content").select("*").eq(
                "page_id", page["id"]
            ).order("display_order").execute()
            
            if content_result.data:
                lang_field = f"content_{language}"
                for item in content_result.data:
                    section = item.get("section", "default")
                    if section not in result[page_slug]:
                        result[page_slug][section] = {}
                    
                    content_key = item.get("content_key", "")
                    if "." in content_key:
                        field_name = content_key.split(".", 1)[1]
                    else:
                        field_name = content_key
                    
                    result[page_slug][section][field_name] = item.get(lang_field) or item.get("content_en") or ""
        
        return result
    
    # =========================================
    # PACKAGE FUNCTIONS
    # =========================================
    
    def get_packages(self) -> List[Dict[str, Any]]:
        """Get all packages."""
        result = self.client.table("cms_packages").select("*").order("display_order").execute()
        return result.data if result.data else []
    
    # =========================================
    # SETTINGS FUNCTIONS
    # =========================================
    
    def get_settings(self) -> Dict[str, Any]:
        """Get site settings."""
        result = self.client.table("cms_settings").select("*").execute()
        if result.data:
            # Convert list to dictionary
            return {item["key"]: item["value"] for item in result.data}
        return {}


# Singleton instance
_cms_client: Optional[CmsClient] = None


def get_cms_client() -> CmsClient:
    """Get the singleton CMS client instance."""
    global _cms_client
    if _cms_client is None:
        _cms_client = CmsClient()
    return _cms_client


# =========================================
# CLI TESTING
# =========================================

if __name__ == "__main__":
    print("Testing CMS Client...")
    
    try:
        client = CmsClient()
        print("✅ CMS Client initialized!")
        
        # Get pages
        pages = client.get_pages()
        print(f"\n📄 Pages: {len(pages)}")
        for page in pages:
            print(f"   - {page.get('name', 'No name')} ({page.get('slug', 'no-slug')})")
        
        # Get sections for home page
        sections = client.get_sections(page_slug="home")
        print(f"\n📋 Sections on 'home': {len(sections)}")
        for section in sections[:10]:
            print(f"   - {section['name']} ({section['key']})")
        
        # Get hero content
        hero = client.get_content(section_key="hero", page_slug="home", language="sv")
        print(f"\n🦸 Hero content fields: {len(hero)}")
        for key, value in list(hero.items())[:5]:
            val_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            print(f"   - {key}: {val_str}")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
