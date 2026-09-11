import json
import math
import os
import re

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI()

ANALYSIS_MODEL = os.getenv(
    "OPENAI_ANALYSIS_MODEL",
    "gpt-5.6-luna",
)


def calculate_length_score(
    content: str,
) -> float:
    """
    Language-neutral length score.

    Uses non-whitespace character count instead
    of word count so English, Korean, Chinese,
    Japanese, etc. are treated more consistently.
    """

    character_count = len(
        re.sub(
            r"\s+",
            "",
            content,
        )
    )

    # Gradually approaches 1.0 instead of
    # suddenly maxing out at a fixed length.
    score = (
        1
        - math.exp(
            -character_count / 700
        )
    )

    return round(
        min(max(score, 0.0), 1.0),
        3,
    )


def calculate_gyul_intensity(
    length_score: float,
    emotional_intensity: float,
) -> float:
    """
    Either a long entry OR an emotionally heavy
    entry can make the day's orange deeper.

    Emotional tone has a slightly stronger effect
    than length.
    """

    length_effect = (
        0.60 * length_score
    )

    emotional_effect = (
        0.85 * emotional_intensity
    )

    combined = (
        1
        - (1 - length_effect)
        * (1 - emotional_effect)
    )

    return round(
        min(max(combined, 0.0), 1.0),
        3,
    )


def analyze_entry_text(
    content: str,
) -> dict:
    length_score = (
        calculate_length_score(
            content
        )
    )

    response = client.responses.create(
        model=ANALYSIS_MODEL,

        store=False,

        input=[
            {
                "role": "system",
                "content": (
                    "You analyze personal journal text "
                    "for a journaling application's "
                    "visual design. "
                    "The journal may be written in any "
                    "language or may mix languages. "

                    "Estimate emotional_intensity from "
                    "0.0 to 1.0. This represents how "
                    "emotionally heavy, burdened, "
                    "distressed, overwhelmed, exhausted, "
                    "or difficult the writing feels. "

                    "0.0 means very light, calm, routine, "
                    "or positive writing. "
                    "Around 0.5 means meaningfully "
                    "stressful, mixed, or emotionally "
                    "difficult. "
                    "1.0 means extremely heavy or "
                    "distressed language. "

                    "Do NOT diagnose mental health "
                    "conditions. Do NOT infer anything "
                    "beyond the text. "
                    "Do NOT increase the emotional score "
                    "simply because the entry is long; "
                    "length is calculated separately. "

                    "Choose mood_label from exactly: "
                    "light, calm, reflective, mixed, "
                    "heavy, very_heavy. "

                    "For detected_language, return a "
                    "short language code such as en, ko, "
                    "zh, ja, es, fr, or 'mixed' when "
                    "multiple languages are meaningfully "
                    "used."
                ),
            },
            {
                "role": "user",
                "content": content,
            },
        ],

        text={
            "format": {
                "type": "json_schema",
                "name": "journal_analysis",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "emotional_intensity": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                        },
                        "mood_label": {
                            "type": "string",
                            "enum": [
                                "light",
                                "calm",
                                "reflective",
                                "mixed",
                                "heavy",
                                "very_heavy",
                            ],
                        },
                        "detected_language": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "emotional_intensity",
                        "mood_label",
                        "detected_language",
                    ],
                    "additionalProperties": False,
                },
            },
        },
    )

    ai_result = json.loads(
        response.output_text
    )

    emotional_intensity = float(
        ai_result[
            "emotional_intensity"
        ]
    )

    emotional_intensity = min(
        max(
            emotional_intensity,
            0.0,
        ),
        1.0,
    )

    gyul_intensity = (
        calculate_gyul_intensity(
            length_score,
            emotional_intensity,
        )
    )

    return {
        "emotional_intensity":
            round(
                emotional_intensity,
                3,
            ),

        "length_score":
            length_score,

        "gyul_intensity":
            gyul_intensity,

        "mood_label":
            ai_result[
                "mood_label"
            ],

        "detected_language":
            ai_result[
                "detected_language"
            ],
    }