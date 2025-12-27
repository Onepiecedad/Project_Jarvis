"""
ColdExperience CMS Client for JARVIS
====================================
Provides tools for JARVIS to interact with the ColdExperience CMS.
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
        result = self.client.table("cms_pages").select("*").order("order_index").execute()
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
            
        result = query.single().execute()
        return result.data if result.data else None
    
    # =========================================
    # SECTION FUNCTIONS
    # =========================================
    
    def get_sections(self, page_id: str = None) -> List[Dict[str, Any]]:
        """Get all sections, optionally filtered by page."""
        query = self.client.table("cms_sections").select("*")
        
        if page_id:
            query = query.eq("page_id", page_id)
            
        result = query.order("order_index").execute()
        return result.data if result.data else []
    
    def get_section(self, section_id: str = None, key: str = None) -> Optional[Dict[str, Any]]:
        """Get a specific section by ID or key."""
        query = self.client.table("cms_sections").select("*")
        
        if section_id:
            query = query.eq("id", section_id)
        elif key:
            query = query.eq("key", key)
        else:
            return None
            
        result = query.single().execute()
        return result.data if result.data else None
    
    # =========================================
    # CONTENT FUNCTIONS
    # =========================================
    
    def get_content(
        self,
        section_id: str = None,
        section_key: str = None,
        language: str = "sv"
    ) -> Dict[str, Any]:
        """
        Get content for a section.
        
        Args:
            section_id: Section UUID
            section_key: Section key (e.g., "hero", "about")
            language: Language code ("sv" or "en")
            
        Returns:
            Content dictionary
        """
        # First get the section
        section = None
        if section_id:
            section = self.get_section(section_id=section_id)
        elif section_key:
            section = self.get_section(key=section_key)
        
        if not section:
            return {}
        
        # Get content from the section
        content_field = f"content_{language}"
        return section.get(content_field, {})
    
    def update_content(
        self,
        section_key: str,
        field: str,
        value: Any,
        language: str = "sv"
    ) -> Dict[str, Any]:
        """
        Update a specific content field in a section.
        
        Args:
            section_key: Section key (e.g., "hero", "about")
            field: Field name to update (e.g., "title", "description")
            value: New value
            language: Language code ("sv" or "en")
            
        Returns:
            Updated section data
        """
        # Get the section
        section = self.get_section(key=section_key)
        if not section:
            raise ValueError(f"Section not found: {section_key}")
        
        # Get current content
        content_field = f"content_{language}"
        current_content = section.get(content_field, {})
        
        # Update the field
        current_content[field] = value
        
        # Save back to database
        result = self.client.table("cms_sections").update({
            content_field: current_content
        }).eq("id", section["id"]).execute()
        
        return result.data[0] if result.data else None
    
    def get_all_content(self, language: str = "sv") -> Dict[str, Any]:
        """
        Get all content organized by page and section.
        
        Returns:
            Dictionary with structure: {page_slug: {section_key: content}}
        """
        pages = self.get_pages()
        sections = self.get_sections()
        
        result = {}
        for page in pages:
            page_slug = page["slug"]
            result[page_slug] = {}
            
            page_sections = [s for s in sections if s.get("page_id") == page["id"]]
            for section in page_sections:
                content_field = f"content_{language}"
                result[page_slug][section["key"]] = section.get(content_field, {})
        
        return result
    
    # =========================================
    # MEDIA FUNCTIONS
    # =========================================
    
    def get_media(self, section_id: str = None, media_type: str = None) -> List[Dict[str, Any]]:
        """
        Get media items.
        
        Args:
            section_id: Filter by section
            media_type: Filter by type (image, video, youtube)
            
        Returns:
            List of media items
        """
        query = self.client.table("cms_media").select("*")
        
        if section_id:
            query = query.eq("section_id", section_id)
        if media_type:
            query = query.eq("type", media_type)
            
        result = query.order("created_at", desc=True).execute()
        return result.data if result.data else []
    
    def upload_media(
        self,
        file_path: str,
        section_id: str,
        media_type: str = "image"
    ) -> Dict[str, Any]:
        """
        Upload a media file to storage and create a record.
        
        Note: This is a placeholder - actual file upload requires more implementation.
        """
        raise NotImplementedError("Media upload requires additional implementation")


# Singleton instance
_cms_client: Optional[CmsClient] = None


def get_cms_client() -> CmsClient:
    """Get the singleton CMS client instance."""
    global _cms_client
    if _cms_client is None:
        _cms_client = CmsClient()
    return _cms_client


# =========================================
# CONVENIENCE FUNCTIONS FOR JARVIS TOOLS
# =========================================

def list_cms_pages() -> List[Dict]:
    """List all CMS pages."""
    return get_cms_client().get_pages()


def list_cms_sections(page_slug: str = None) -> List[Dict]:
    """List CMS sections, optionally for a specific page."""
    client = get_cms_client()
    
    if page_slug:
        page = client.get_page(slug=page_slug)
        if page:
            return client.get_sections(page_id=page["id"])
        return []
    
    return client.get_sections()


def get_cms_content(section_key: str, language: str = "sv") -> Dict:
    """Get content for a specific section."""
    return get_cms_client().get_content(section_key=section_key, language=language)


def update_cms_content(section_key: str, field: str, value: Any, language: str = "sv") -> Dict:
    """Update a content field in a section."""
    return get_cms_client().update_content(section_key, field, value, language)


def get_all_cms_content(language: str = "sv") -> Dict:
    """Get all CMS content organized by page and section."""
    return get_cms_client().get_all_content(language)


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
            print(f"   - {page['name']} ({page['slug']})")
        
        # Get sections
        sections = client.get_sections()
        print(f"\n📋 Sections: {len(sections)}")
        for section in sections[:10]:  # Show first 10
            print(f"   - {section['name']} ({section['key']})")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
