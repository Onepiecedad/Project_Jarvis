## Show View Tool

You can display data in the dashboard's dynamic view panel using this tool.

### View Types

- **table**: Data displayed in a table format
- **card**: Data displayed as cards in a grid
- **list**: Data displayed as a simple list
- **gallery**: Images/media displayed in a gallery grid

### Usage

Show tasks in a table:

~~~json
{
    "thoughts": ["I will display the tasks in a table view"],
    "tool_name": "show_view",
    "tool_args": {
        "type": "table",
        "title": "Mina Tasks",
        "data": [
            {"Namn": "Research X", "Status": "Pågående", "Prioritet": 8},
            {"Namn": "Rapport", "Status": "Klar", "Prioritet": 5}
        ]
    }
}
~~~

Show entities as cards:

~~~json
{
    "thoughts": ["I will show the companies as cards"],
    "tool_name": "show_view",
    "tool_args": {
        "type": "card",
        "title": "Företag",
        "subtitle": "Våra leads",
        "data": [
            {"name": "Stigbergets", "type": "Bryggeri", "status": "Lead"},
            {"name": "Dugges", "type": "Bryggeri", "status": "Kvalificerad"}
        ]
    }
}
~~~

Show images in a gallery:

~~~json
{
    "thoughts": ["I will display the images in a gallery"],
    "tool_name": "show_view",
    "tool_args": {
        "type": "gallery",
        "title": "Bilder från hero-sektionen",
        "data": [
            {"url": "https://example.com/image1.jpg", "title": "Ishav", "alt": "Vy över ishav"},
            {"url": "https://example.com/image2.jpg", "title": "Äventyr", "alt": "Vinterlandskap"}
        ]
    }
}
~~~

### Arguments

- **type** (required): View type - "table", "card", "list", or "gallery"
- **title** (optional): Title shown above the view
- **subtitle** (optional): Subtitle shown under the title
- **data** (required): Array of objects to display

### Gallery data format

For gallery views, each item should have:

- url: URL to the image
- title: Title/name of the image
- alt: Alt text for accessibility
- type: "image" or "video"
