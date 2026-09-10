import os

from dotenv import load_dotenv
from supabase import Client, create_client


load_dotenv()


SUPABASE_URL = os.getenv(
    "SUPABASE_URL"
)

SUPABASE_SECRET_KEY = os.getenv(
    "SUPABASE_SECRET_KEY"
)


if not SUPABASE_URL:
    raise RuntimeError(
        "SUPABASE_URL is not set"
    )

if not SUPABASE_SECRET_KEY:
    raise RuntimeError(
        "SUPABASE_SECRET_KEY is not set"
    )


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY,
)


IMAGE_BUCKET = "journal-images"


def upload_image(
    storage_key: str,
    data: bytes,
    content_type: str,
):
    return (
        supabase.storage
        .from_(IMAGE_BUCKET)
        .upload(
            path=storage_key,
            file=data,
            file_options={
                "content-type":
                    content_type,
                "upsert":
                    "false",
            },
        )
    )


def create_signed_image_url(
    storage_key: str,
    expires_in: int = 3600,
) -> str:
    response = (
        supabase.storage
        .from_(IMAGE_BUCKET)
        .create_signed_url(
            storage_key,
            expires_in,
        )
    )

    if isinstance(
        response,
        dict,
    ):
        url = (
            response.get(
                "signedURL"
            )
            or response.get(
                "signedUrl"
            )
            or response.get(
                "signed_url"
            )
        )
    else:
        url = (
            getattr(
                response,
                "signed_url",
                None,
            )
            or getattr(
                response,
                "signedURL",
                None,
            )
        )

    if not url:
        raise RuntimeError(
            "Could not create signed URL"
        )

    return url


def delete_image_from_storage(
    storage_key: str,
):
    return (
        supabase.storage
        .from_(IMAGE_BUCKET)
        .remove([
            storage_key
        ])
    )