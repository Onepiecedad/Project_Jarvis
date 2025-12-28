"""
Show View Tool
===============
Displays data in the dashboard's dynamic view panel.
Supports table, card, list, and gallery (for images) views.
"""

from python.helpers.tool import Tool, Response
import json


class ShowView(Tool):
    """Tool for displaying data in the dashboard's dynamic view panel."""

    async def execute(self, **kwargs):
        view_type = kwargs.get("type", "table")
        title = kwargs.get("title", "")
        subtitle = kwargs.get("subtitle", "")
        data = kwargs.get("data", [])
        
        valid_types = ["table", "card", "list", "gallery"]
        if view_type not in valid_types:
            return Response(
                message=f"❌ Ogiltig vy-typ '{view_type}'. Giltiga typer: {', '.join(valid_types)}",
                break_loop=False
            )
        
        if not data:
            return Response(
                message="❌ Ingen data att visa. Ange 'data' som en array.",
                break_loop=False
            )
        
        # Format response message
        data_count = len(data) if isinstance(data, list) else 1
        type_name = {
            "table": "tabell",
            "card": "kort",
            "list": "lista",
            "gallery": "galleri"
        }.get(view_type, view_type)
        
        message = f"✅ Visar {data_count} objekt i {type_name}"
        if title:
            message += f": **{title}**"
        
        # The tool response includes the view data which the dashboard will pick up
        return Response(
            message=message,
            break_loop=False,
            additional={
                "view": {
                    "type": view_type,
                    "title": title,
                    "subtitle": subtitle,
                    "data": data
                }
            }
        )
