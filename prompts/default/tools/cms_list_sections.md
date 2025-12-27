You can list all sections in the ColdExperience CMS using this tool.

## Usage

### List all sections

~~~json
{
    "thoughts": ["I need to see what sections are available in the CMS"],
    "tool_name": "cms_list_sections",
    "tool_args": {}
}
~~~

### List sections for a specific page

~~~json
{
    "thoughts": ["I need to see the sections on the home page"],
    "tool_name": "cms_list_sections",
    "tool_args": {
        "page": "home"
    }
}
~~~

## Available pages

- home - Startsidan
- about - Om oss
- packages - Paket
- book - Boka

## Returns

A list of sections with their names and keys.

Example response:

- **Hero Section** (key: `hero`)
- **About Section** (key: `about`)
- **Packages** (key: `packages`)
