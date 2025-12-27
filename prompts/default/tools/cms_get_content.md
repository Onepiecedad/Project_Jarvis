You can get content from a specific CMS section using this tool.

## Usage

### Get Swedish content

~~~json
{
    "thoughts": ["I need to see the hero section content"],
    "tool_name": "cms_get_content",
    "tool_args": {
        "section": "hero"
    }
}
~~~

### Get English content

~~~json
{
    "thoughts": ["I need to see the about section in English"],
    "tool_name": "cms_get_content",
    "tool_args": {
        "section": "about",
        "language": "en"
    }
}
~~~

## Arguments

- **section** (required): Section key (e.g., "hero", "about", "packages")
- **language** (optional): "sv" (Swedish, default) or "en" (English)

## Common section keys

- hero - Main hero section
- about - About section
- packages - Packages/pricing
- testimonials - Customer reviews
- instagram - Instagram feed
- footer - Footer content

## Returns

The content fields for that section, including:

- title, subtitle, description
- buttonText, buttonLink
- images, videos
- and more depending on the section
