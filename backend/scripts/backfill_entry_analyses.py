import argparse

from sqlalchemy import select

from app import models
from app.database import SessionLocal
from app.entry_analysis import analyze_entry_text


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually analyze and save entries",
    )

    args = parser.parse_args()

    db = SessionLocal()

    analyzed = 0
    failed = 0

    try:
        statement = (
            select(models.Entry)
            .outerjoin(
                models.EntryAnalysis,
                models.Entry.id
                == models.EntryAnalysis.entry_id,
            )
            .where(
                models.EntryAnalysis.id.is_(None)
            )
            .order_by(
                models.Entry.id
            )
        )

        entries = list(
            db.scalars(statement).all()
        )

        print(
            f"Found {len(entries)} entries "
            "without analysis"
        )

        print(
            "MODE:",
            "APPLY"
            if args.apply
            else "DRY RUN",
        )

        print()

        for entry in entries:
            preview = (
                entry.content[:60]
                .replace("\n", " ")
            )

            print(
                f"[ENTRY {entry.id}] "
                f"{preview}"
            )

            if not args.apply:
                continue

            try:
                result = analyze_entry_text(
                    entry.content
                )

                analysis = (
                    models.EntryAnalysis(
                        entry_id=entry.id,

                        emotional_intensity=
                            result[
                                "emotional_intensity"
                            ],

                        length_score=
                            result[
                                "length_score"
                            ],

                        gyul_intensity=
                            result[
                                "gyul_intensity"
                            ],

                        mood_label=
                            result[
                                "mood_label"
                            ],

                        detected_language=
                            result[
                                "detected_language"
                            ],

                        analysis_source="ai",
                    )
                )

                db.add(analysis)
                db.commit()

                analyzed += 1

                print(
                    "  ->",
                    result[
                        "gyul_intensity"
                    ],
                    result[
                        "mood_label"
                    ],
                    result[
                        "detected_language"
                    ],
                )

            except Exception as error:
                db.rollback()

                failed += 1

                print(
                    f"[FAILED] entry "
                    f"{entry.id}: {error}"
                )

        print()
        print("----- SUMMARY -----")
        print(
            f"Candidates: {len(entries)}"
        )
        print(
            f"Analyzed:   {analyzed}"
        )
        print(
            f"Failed:     {failed}"
        )

        if not args.apply:
            print()
            print(
                "Dry run only. "
                "Nothing was analyzed."
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()