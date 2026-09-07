import json

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


client = OpenAI()


def suggest_tags(
    content: str,
    existing_tags: list[str],
) -> list[str]:
    existing_text = (
        ", ".join(existing_tags)
        if existing_tags
        else "none"
    )

    response = client.responses.create(
        model="gpt-5.6-luna",

        instructions=(
            "You organize short personal journal entries. "
            "Suggest useful concise tags for the entry. "
            "Tags should describe meaningful topics, activities, "
            "places, projects, or themes. "
            "Prefer existing tags when they fit. "
            "Do not include # symbols. "
            "Use lowercase tags. "
            "Return 1 to 4 tags."
        ),

        input=(
            f"Existing tags in this journal:\n"
            f"{existing_text}\n\n"
            f"Journal entry:\n"
            f"{content}"
        ),

        text={
            "format": {
                "type": "json_schema",
                "name": "tag_suggestions",
                "strict": True,

                "schema": {
                    "type": "object",

                    "properties": {
                        "tags": {
                            "type": "array",

                            "items": {
                                "type": "string"
                            },

                            "minItems": 1,
                            "maxItems": 4,
                        }
                    },

                    "required": [
                        "tags"
                    ],

                    "additionalProperties": False,
                },
            }
        },
    )

    result = json.loads(
        response.output_text
    )

    tags = []

    for tag in result["tags"]:
        clean_tag = (
            tag.strip()
            .lstrip("#")
            .lower()
        )

        if (
            clean_tag
            and clean_tag not in tags
        ):
            tags.append(clean_tag)

    return tags[:4]