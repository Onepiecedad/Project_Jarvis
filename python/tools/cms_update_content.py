"""
CMS Update Content Tool
=======================
Updates content in a CMS section.
"""

from python.tools.cms_client import update_cms_content


async def execute(
    section: str,
    field: str,
    value: str,
    language: str = "sv",
    **kwargs
) -> str:
    """
    Update a content field in a CMS section.
    
    Args:
        section: Section key (e.g., "hero", "about")
        field: Field name to update (e.g., "title", "description", "buttonText")
        value: New value for the field
        language: Language code - "sv" for Swedish, "en" for English
    
    Returns:
        Confirmation message
    """
    try:
        result = update_cms_content(
            section_key=section,
            field=field,
            value=value,
            language=language
        )
        
        if result:
            return f"✅ Uppdaterat! Sektionen '{section}' har fältet '{field}' ändrat till: {value}"
        else:
            return f"❌ Kunde inte uppdatera '{section}.{field}'"
            
    except ValueError as e:
        return f"❌ Fel: {str(e)}"
    except Exception as e:
        return f"❌ Kunde inte uppdatera innehåll: {str(e)}"
