"""
CMS List Sections Tool
======================
Lists all pages and sections in the ColdExperience CMS.
"""

from python.helpers.tool import Tool, Response
from python.tools.cms_client import CmsClient


class CmsListSections(Tool):
    """Tool for listing CMS pages and sections."""

    async def execute(self, **kwargs):
        page = kwargs.get("page", None)
        
        try:
            client = CmsClient()
            
            # Get all pages first
            pages = client.get_pages()
            
            if not pages:
                return Response(
                    message="❌ Inga sidor hittades i CMS-databasen.",
                    break_loop=False
                )
            
            result = "## ColdExperience CMS\n\n"
            
            # List pages
            result += "### 📄 Sidor:\n"
            for p in pages:
                name = p.get('name', p.get('slug', 'Namnlös'))
                slug = p.get('slug', '-')
                result += f"- **{name}** (`{slug}`)\n"
            
            result += "\n"
            
            # If a specific page is requested, show its sections
            if page:
                sections = client.get_sections(page_slug=page)
                if sections:
                    result += f"### 📋 Sektioner på '{page}':\n"
                    for section in sections:
                        result += f"- **{section['name']}** (key: `{section['key']}`)\n"
                else:
                    result += f"⚠️ Inga sektioner hittades för sidan '{page}'.\n"
            else:
                # Show sections for first page as example
                if pages:
                    first_page = pages[0].get('slug', 'home')
                    sections = client.get_sections(page_slug=first_page)
                    if sections:
                        result += f"### 📋 Exempel - Sektioner på '{first_page}':\n"
                        for section in sections[:10]:
                            result += f"- **{section['name']}** (key: `{section['key']}`)\n"
                        if len(sections) > 10:
                            result += f"_... och {len(sections) - 10} till_\n"
            
            result += "\n💡 **Tips:** Använd `cms_get_content` för att se innehållet i en sektion."
            
            return Response(
                message=result,
                break_loop=False
            )
            
        except Exception as e:
            return Response(
                message=f"❌ Kunde inte hämta CMS-data: {str(e)}",
                break_loop=False
            )
