import json
import math
import os
import re

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError

load_dotenv()

client = OpenAI()

ANALYSIS_MODEL = os.getenv(
    "OPENAI_ANALYSIS_MODEL",
    "gpt-5.6-luna",
)

def split_into_segments(
    content: str,
) -> list[dict]:
    pattern = re.compile(
        r".+?(?:[.!?。！？]+|\n+|$)",
        re.DOTALL,
    )

    segments = []

    for match in pattern.finditer(content):
        raw_text = match.group()

        leading_spaces = (
            len(raw_text)
            - len(raw_text.lstrip())
        )

        trailing_spaces = (
            len(raw_text)
            - len(raw_text.rstrip())
        )

        text = raw_text.strip()

        if not text:
            continue

        segments.append(
            {
                "text": text,
                "start_offset":
                    match.start()
                    + leading_spaces,

                "end_offset":
                    match.end()
                    - trailing_spaces,
            }
        )

    return segments
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
    # 1. 글 길이 계산
    length_score = calculate_length_score(
        content
    )

    # 2. Python에서 문장 분리 + 정확한 위치 계산
    raw_segments = split_into_segments(
        content
    )

    segment_input = [
        {
            "segment_index": index,
            "text": segment["text"],
        }
        for index, segment
        in enumerate(raw_segments)
    ]

    # 3. 가능하면 OpenAI 분석
    try:
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
                        "0.0 to 1.0 for the journal as a whole. "
                        "This represents how emotionally heavy, "
                        "burdened, distressed, overwhelmed, "
                        "exhausted, or difficult the writing feels. "

                        "0.0 means very light, calm, routine, "
                        "or positive writing. "
                        "Around 0.5 means meaningfully stressful, "
                        "mixed, or emotionally difficult. "
                        "1.0 means extremely heavy or distressed. "

                        "Do NOT diagnose mental health conditions. "
                        "Do NOT infer anything beyond the text. "
                        "Do NOT increase emotional intensity simply "
                        "because the entry is long. "

                        "Choose mood_label from exactly: "
                        "light, calm, reflective, mixed, "
                        "heavy, very_heavy. "

                        "For detected_language, return a short "
                        "language code such as en, ko, zh, ja, "
                        "es, fr, or mixed. "

                        "You will receive pre-segmented pieces. "
                        "Return exactly one analysis for each "
                        "segment_index. "
                        "Do not merge, split, remove, or reorder "
                        "the segments. "

                        "For every segment, estimate intensity "
                        "from 0.0 to 1.0 based only on the "
                        "emotional heaviness of that passage. "

                        "Choose segment tone from exactly: "
                        "light, calm, reflective, mixed, "
                        "stressed, heavy, very_heavy."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "journal": content,
                            "segments": segment_input,
                        },
                        ensure_ascii=False,
                    ),
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

                            "segment_analyses": {
                                "type": "array",
                                "items": {
                                    "type": "object",

                                    "properties": {
                                        "segment_index": {
                                            "type": "integer",
                                        },

                                        "intensity": {
                                            "type": "number",
                                            "minimum": 0,
                                            "maximum": 1,
                                        },

                                        "tone": {
                                            "type": "string",
                                            "enum": [
                                                "light",
                                                "calm",
                                                "reflective",
                                                "mixed",
                                                "stressed",
                                                "heavy",
                                                "very_heavy",
                                            ],
                                        },
                                    },

                                    "required": [
                                        "segment_index",
                                        "intensity",
                                        "tone",
                                    ],

                                    "additionalProperties":
                                        False,
                                },
                            },
                        },

                        "required": [
                            "emotional_intensity",
                            "mood_label",
                            "detected_language",
                            "segment_analyses",
                        ],

                        "additionalProperties":
                            False,
                    },
                },
            },
        )

        ai_result = json.loads(
            response.output_text
        )

    # 4. API credit 없으면 local fallback
    except RateLimitError:
        analyzed_segments = []

        for index, segment in enumerate(
            raw_segments
        ):
            result = analyze_segment_fallback(
                segment["text"]
            )

            analyzed_segments.append(
                {
                    "segment_index": index,
                    "text": segment["text"],
                    "start_offset":
                        segment["start_offset"],
                    "end_offset":
                        segment["end_offset"],
                    "intensity":
                        result["intensity"],
                    "tone":
                        result["tone"],
                }
            )

        intensities = [
            segment["intensity"]
            for segment in analyzed_segments
        ]

        emotional_intensity = (
            max(intensities)
            if intensities
            else 0.0
        )

        gyul_intensity = (
            calculate_gyul_intensity(
                length_score,
                emotional_intensity,
            )
        )

        if emotional_intensity >= 0.85:
            mood_label = "very_heavy"

        elif emotional_intensity >= 0.60:
            mood_label = "heavy"

        elif emotional_intensity >= 0.35:
            mood_label = "mixed"

        elif emotional_intensity >= 0.15:
            mood_label = "reflective"

        else:
            mood_label = "calm"

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
                mood_label,

            "detected_language":
                "unknown",

            "analysis_source":
                "heuristic_fallback",

            "segments":
                analyzed_segments,
        }

    # 5. 여기부터는 OpenAI 성공했을 때 실행됨
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

    ai_segments_by_index = {
        segment["segment_index"]:
            segment
        for segment
        in ai_result[
            "segment_analyses"
        ]
    }

    analyzed_segments = []

    for index, segment in enumerate(
        raw_segments
    ):
        ai_segment = (
            ai_segments_by_index.get(
                index
            )
        )

        if ai_segment is None:
            intensity = 0.0
            tone = "calm"

        else:
            intensity = float(
                ai_segment[
                    "intensity"
                ]
            )

            intensity = min(
                max(
                    intensity,
                    0.0,
                ),
                1.0,
            )

            tone = ai_segment[
                "tone"
            ]

        analyzed_segments.append(
            {
                "segment_index":
                    index,

                "text":
                    segment["text"],

                "start_offset":
                    segment[
                        "start_offset"
                    ],

                "end_offset":
                    segment[
                        "end_offset"
                    ],

                "intensity":
                    round(
                        intensity,
                        3,
                    ),

                "tone":
                    tone,
            }
        )

    # 6. OpenAI 성공 결과
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

        "analysis_source":
            "ai",

        "segments":
            analyzed_segments,
    }

def analyze_segment_fallback(
    text: str,
) -> dict:
    normalized = text.lower()

    patterns = {
        # Korean
        "힘들": 0.45,
        "지치": 0.45,
        "불안": 0.50,
        "우울": 0.55,
        "슬프": 0.45,
        "외롭": 0.50,
        "막막": 0.45,
        "스트레스": 0.45,
        "짜증": 0.35,
        "속상": 0.40,
        "무기력": 0.55,
        "혼자인": 0.40,

        # English
        "tired": 0.40,
        "exhausted": 0.55,
        "anxious": 0.50,
        "sad": 0.40,
        "lonely": 0.50,
        "overwhelmed": 0.55,
        "stressed": 0.45,
        "hopeless": 0.60,
    }

    matched_weights = []

    for pattern, weight in patterns.items():
        if pattern in normalized:
            matched_weights.append(
                weight
            )

    # 여러 감정 단어를 단순 덧셈하지 않고
    # 점점 완만하게 증가시킨다.
    if matched_weights:
        remaining_lightness = 1.0

        for weight in matched_weights:
            remaining_lightness *= (
                1.0 - weight
            )

        score = (
            1.0
            - remaining_lightness
        )

    else:
        score = 0.05

    # 강조 표현은 작은 bonus만 추가
    if "너무" in text:
        score += 0.06

    if "ㅠㅠ" in text or "ㅜㅜ" in text:
        score += 0.10

    if "..." in text:
        score += 0.04

    if "really" in normalized:
        score += 0.05

    # 1.0 근처까지 너무 쉽게 가지 않도록 제한
    score = min(
        max(score, 0.0),
        0.95,
    )

    if score >= 0.85:
        tone = "very_heavy"

    elif score >= 0.60:
        tone = "heavy"

    elif score >= 0.35:
        tone = "stressed"

    elif score >= 0.15:
        tone = "reflective"

    else:
        tone = "calm"

    return {
        "intensity": round(
            score,
            3,
        ),
        "tone": tone,
    }