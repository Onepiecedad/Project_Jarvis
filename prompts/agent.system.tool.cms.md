## ColdExperience CMS Tools

You have access to tools for managing the ColdExperience website CMS:

### cms_list_sections

Lists all sections in the CMS, optionally filtered by page.

~~~json
{
    "thoughts": ["I need to see what sections are available in the CMS"],
    "tool_name": "cms_list_sections",
    "tool_args": {}
}
~~~

With page filter:

~~~json
{
    "thoughts": ["I need to see the sections on the home page"],
    "tool_name": "cms_list_sections",
    "tool_args": {
        "page": "home"
    }
}
~~~

### cms_get_content

Gets content from a specific CMS section.

~~~json
{
    "thoughts": ["I need to see the hero section content"],
    "tool_name": "cms_get_content",
    "tool_args": {
        "section": "hero",
        "language": "sv"
    }
}
~~~

Arguments:

- section: Section key (e.g., "hero", "about", "packages")
- language: "sv" (Swedish) or "en" (English)

### cms_update_content

Updates content in a CMS section.

~~~json
{
    "thoughts": ["I will update the hero title"],
    "tool_name": "cms_update_content",
    "tool_args": {
        "section": "hero",
        "field": "title",
        "value": "New Title Here",
        "language": "sv"
    }
}
~~~

Arguments:

- section: Section key
- field: Field name (title, description, buttonText, etc.)
- value: New value
- language: "sv" or "en"

**Important**: Always use cms_get_content first to see current values before updating.

### cms_get_media

Gets media/images from a CMS page and section, displays them in the gallery panel.

~~~json
{
    "thoughts": ["I will show the images from the hero section"],
    "tool_name": "cms_get_media",
    "tool_args": {
        "page": "home",
        "section": "hero"
    }
}
~~~

Arguments:

- page (required): Page slug (e.g., "home", "about")
- section (optional): Section key to filter by
- show (optional): Whether to show in the gallery panel (default: true)
