"""
CMS Get Content Tool
====================
Gets content from a specific CMS section or page.
"""

from python.helpers.tool import Tool, Response
from python.tools.cms_client import CmsClient
import json


class CmsGetContent(Tool):
    """Tool for getting CMS section content."""

    async def execute(self, **kwargs):
        section = kwargs.get("section", "").strip()
        page = kwargs.get("page", "").strip()
        language = kwargs.get("language", "sv")
        
        if not section and not page:
            return Response(
                message="❌ Ange 'section' eller 'page'. Använd cms_list_sections för att se tillgängliga alternativ.",
                break_loop=False
            )
        
        try:
            client = CmsClient()
            
            # Get content
            content = client.get_content(
                section_key=section if section else None,
                page_slug=page if page else None,
                language=language
            )
            
            if not content:
                return Response(
                    message=f"❌ Inget innehåll hittades för section='{section}', page='{page}' ({language})",
                    break_loop=False
                )
            
            # Format the content nicely
            if section:
                result = f"## Innehåll för sektion '{section}'"
            else:
                result = f"## Innehåll för sida '{page}'"
            result += f" ({language}):\n\n"
            
            for key, value in content.items():
                if isinstance(value, dict):
                    result += f"**{key}:**\n```json\n{json.dumps(value, indent=2, ensure_ascii=False)}\n```\n"
                elif isinstance(value, list):
                    result += f"**{key}:** (lista med {len(value)} objekt)\n"
                    for i, item in enumerate(value[:5]):
                        if isinstance(item, dict):
                            result += f"  {i+1}. {item.get('title', item.get('name', str(item)[:50]))}\n"
                        else:
                            result += f"  {i+1}. {str(item)[:50]}\n"
                    if len(value) > 5:
                        result += f"  ... och {len(value) - 5} till\n"
                else:
                    str_value = str(value)
                    if len(str_value) > 200:
                        str_value = str_value[:200] + "..."
                    result += f"**{key}:** {str_value}\n"
            
            return Response(
                message=result,
                break_loop=False
            )
            
        except Exception as e:
            return Response(
                message=f"❌ Kunde inte hämta innehåll: {str(e)}",
                break_loop=False
            )
