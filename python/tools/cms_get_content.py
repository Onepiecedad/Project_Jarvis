"""
CMS Get Content Tool
====================
Gets content from a specific CMS section.
"""

from python.tools.cms_client import get_cms_content
import json


async def execute(section: str, language: str = "sv", **kwargs) -> str:
    """
    Get content from a CMS section.
    
    Args:
        section: Section key (e.g., "hero", "about", "packages")
        language: Language code - "sv" for Swedish, "en" for English
    
    Returns:
        Section content as formatted text
    """
    try:
        content = get_cms_content(section_key=section, language=language)
        
        if not content:
            return f"❌ Ingen innehåll hittades för sektionen '{section}' ({language})"
        
        # Format the content nicely
        result = f"## Innehåll för '{section}' ({language}):\n\n"
        
        for key, value in content.items():
            if isinstance(value, dict):
                result += f"**{key}:**\n"
                result += f"```json\n{json.dumps(value, indent=2, ensure_ascii=False)}\n```\n"
            elif isinstance(value, list):
                result += f"**{key}:** (lista med {len(value)} objekt)\n"
                for i, item in enumerate(value[:5]):  # Show first 5
                    if isinstance(item, dict):
                        result += f"  {i+1}. {item.get('title', item.get('name', str(item)[:50]))}\n"
                    else:
                        result += f"  {i+1}. {str(item)[:50]}\n"
                if len(value) > 5:
                    result += f"  ... och {len(value) - 5} till\n"
            else:
                # Truncate long strings
                str_value = str(value)
                if len(str_value) > 200:
                    str_value = str_value[:200] + "..."
                result += f"**{key}:** {str_value}\n"
        
        return result
        
    except Exception as e:
        return f"❌ Kunde inte hämta innehåll: {str(e)}"
