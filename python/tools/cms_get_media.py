"""
CMS Get Media Tool
==================
Gets media/images from ColdExperience CMS for a specific page and section.
"""

from python.helpers.tool import Tool, Response
from python.tools.cms_client import CmsClient
import json


class CmsGetMedia(Tool):
    """Tool for getting media/images from CMS sections."""

    async def execute(self, **kwargs):
        page = kwargs.get("page", "").strip()
        section = kwargs.get("section", "").strip()
        show_in_panel = kwargs.get("show", True)  # Whether to show in the view panel
        
        if not page:
            return Response(
                message="❌ 'page' är obligatoriskt. Ange sidan (t.ex. 'home', 'about').",
                break_loop=False
            )
        
        try:
            client = CmsClient()
            
            # Get media from cms_media table
            query = client.client.table("cms_media").select("*")
            
            # First get the page
            page_obj = client.get_page(slug=page)
            if not page_obj:
                return Response(
                    message=f"❌ Sidan '{page}' hittades inte.",
                    break_loop=False
                )
            
            query = query.eq("page_id", page_obj["id"])
            
            if section:
                query = query.eq("section", section)
            
            result = query.order("display_order").execute()
            
            if not result.data:
                # Try to check if section has any media referenced in content
                return Response(
                    message=f"❌ Inga media hittades för page='{page}'" + (f", section='{section}'" if section else ""),
                    break_loop=False
                )
            
            media_items = result.data
            
            # Format for gallery view
            gallery_data = []
            for item in media_items:
                gallery_data.append({
                    "url": item.get("url") or item.get("file_path") or "",
                    "title": item.get("title") or item.get("alt_text") or "",
                    "alt": item.get("alt_text") or "",
                    "type": item.get("type") or "image"
                })
            
            # Build response message
            message = f"📸 Hittade **{len(media_items)} media** på sidan '{page}'"
            if section:
                message += f" i sektionen '{section}'"
            message += ".\n\n"
            
            for i, item in enumerate(gallery_data[:5]):
                message += f"{i+1}. {item['title'] or 'Namnlös'} ({item['type']})\n"
            if len(gallery_data) > 5:
                message += f"... och {len(gallery_data) - 5} till\n"
            
            if show_in_panel and gallery_data:
                message += "\n💡 **Visar i panelen till höger**"
            
            # Return with view data for the panel
            return Response(
                message=message,
                break_loop=False,
                additional={
                    "view": {
                        "type": "gallery",
                        "title": f"Media: {page}" + (f" / {section}" if section else ""),
                        "subtitle": f"{len(gallery_data)} bilder/videos",
                        "data": gallery_data
                    }
                } if show_in_panel else None
            )
            
        except Exception as e:
            return Response(
                message=f"❌ Kunde inte hämta media: {str(e)}",
                break_loop=False
            )
