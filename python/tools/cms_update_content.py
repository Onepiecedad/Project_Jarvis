"""
CMS Update Content Tool
=======================
Updates content in a CMS section.
"""

from python.helpers.tool import Tool, Response
from python.tools.cms_client import CmsClient


class CmsUpdateContent(Tool):
    """Tool for updating CMS section content."""

    async def execute(self, **kwargs):
        section = kwargs.get("section", "").strip()
        field = kwargs.get("field", "").strip()
        value = kwargs.get("value", "")
        language = kwargs.get("language", "sv")
        page = kwargs.get("page", "").strip()
        
        if not section:
            return Response(
                message="❌ 'section' är obligatoriskt.",
                break_loop=False
            )
        
        if not field:
            return Response(
                message="❌ 'field' är obligatoriskt. Ange vilket fält som ska uppdateras (t.ex. 'title', 'description').",
                break_loop=False
            )
        
        try:
            client = CmsClient()
            result = client.update_content(
                section_key=section,
                field=field,
                value=value,
                language=language,
                page_slug=page if page else None
            )
            
            if result:
                preview = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                return Response(
                    message=f"✅ **Uppdaterat!**\n\nSektion: `{section}`\nFält: `{field}`\nSpråk: `{language}`\nNytt värde: {preview}",
                    break_loop=False
                )
            else:
                return Response(
                    message=f"❌ Kunde inte uppdatera '{section}.{field}'",
                    break_loop=False
                )
                
        except ValueError as e:
            return Response(
                message=f"❌ Fel: {str(e)}",
                break_loop=False
            )
        except Exception as e:
            return Response(
                message=f"❌ Kunde inte uppdatera innehåll: {str(e)}",
                break_loop=False
            )
