You can update content in a CMS section using this tool.

## Usage

### Update Swedish content

~~~json
{
    "thoughts": ["I need to update the hero title"],
    "tool_name": "cms_update_content",
    "tool_args": {
        "section": "hero",
        "field": "title",
        "value": "Välkommen till Cold Experience"
    }
}
~~~

### Update English content

~~~json
{
    "thoughts": ["I need to update the about description in English"],
    "tool_name": "cms_update_content",
    "tool_args": {
        "section": "about",
        "field": "description",
        "value": "We offer unique winter adventures...",
        "language": "en"
    }
}
~~~

## Arguments

- **section** (required): Section key (e.g., "hero", "about")
- **field** (required): Field name to update (e.g., "title", "description", "buttonText")
- **value** (required): New value for the field
- **language** (optional): "sv" (Swedish, default) or "en" (English)

## Common fields

- title - Main heading
- subtitle - Secondary heading
- description - Main text content
- buttonText - Button label
- buttonLink - Button URL

## Important

- Always confirm with the user before making changes
- Use cms_get_content first to see current values
- Changes are immediate and affect the live website
