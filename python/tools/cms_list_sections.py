"""
CMS List Sections Tool
======================
Lists all sections in the ColdExperience CMS.
"""

from python.tools.cms_client import list_cms_sections, list_cms_pages


async def execute(page: str = None, **kwargs) -> str:
    """
    List all CMS sections, optionally filtered by page.
    
    Args:
        page: Optional page slug to filter sections (e.g., "home", "about")
    
    Returns:
        Formatted list of sections
    """
    try:
        if page:
            sections = list_cms_sections(page_slug=page)
            result = f"## Sektioner på sidan '{page}':\n\n"
        else:
            sections = list_cms_sections()
            result = "## Alla CMS-sektioner:\n\n"
        
        if not sections:
            return "Inga sektioner hittades."
        
        for section in sections:
            result += f"- **{section['name']}** (key: `{section['key']}`)\n"
            if section.get('description'):
                result += f"  _{section['description']}_\n"
        
        # Also list available pages
        pages = list_cms_pages()
        result += "\n### Tillgängliga sidor:\n"
        for p in pages:
            result += f"- {p['name']} (`{p['slug']}`)\n"
        
        return result
        
    except Exception as e:
        return f"❌ Kunde inte hämta sektioner: {str(e)}"
