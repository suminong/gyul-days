"use client";

import { useEffect, useState } from "react";

import { Entry, EntryImage } from "../types";


type JournalFeedProps = {
  entries: Entry[];
  loading: boolean;

  currentUserId:
    number | null;

  onEditEntry: (
    entryId: number,
    content: string
  ) => Promise<boolean>;

  onDeleteEntry: (
    entryId: number
  ) => Promise<boolean>;

  onDeleteImage: (
    entryId: number,
    imageId: number
  ) => Promise<boolean>;
};


function getDateLabel(
  dateString: string
) {
  const date =
    new Date(dateString);

  const today =
    new Date();

  const yesterday =
    new Date();

  yesterday.setDate(
    today.getDate() - 1
  );


  function isSameDay(
    first: Date,
    second: Date
  ) {
    return (
      first.getFullYear() ===
        second.getFullYear() &&
      first.getMonth() ===
        second.getMonth() &&
      first.getDate() ===
        second.getDate()
    );
  }


  if (
    isSameDay(
      date,
      today
    )
  ) {
    return "today";
  }


  if (
    isSameDay(
      date,
      yesterday
    )
  ) {
    return "yesterday";
  }


  return date.toLocaleDateString(
    undefined,
    {
      month: "short",
      day: "numeric",
    }
  );
}


function groupEntriesByDate(
  entries: Entry[]
) {
  return entries.reduce<
    Record<string, Entry[]>
  >(
    (
      groups,
      entry
    ) => {
      const label =
        getDateLabel(
          entry.created_at
        );

      if (!groups[label]) {
        groups[label] = [];
      }

      groups[label].push(
        entry
      );

      return groups;
    },
    {}
  );
}


export default function JournalFeed({
  entries,
  loading,
  currentUserId,
  onEditEntry,
  onDeleteEntry,
  onDeleteImage,
}: JournalFeedProps) {
  const [
    editingEntryId,
    setEditingEntryId,
  ] = useState<number | null>(
    null
  );

  const [
    editContent,
    setEditContent,
  ] = useState("");

  const [
    editingLoading,
    setEditingLoading,
  ] = useState(false);

  const [
    deletingEntryId,
    setDeletingEntryId,
  ] = useState<number | null>(
    null
  );

  const [
    deletingImageId,
    setDeletingImageId,
  ] = useState<number | null>(
    null
  );


  // Lightbox
  const [
    lightboxImage,
    setLightboxImage,
  ] = useState<EntryImage | null>(
    null
  );


  const groupedEntries =
    groupEntriesByDate(entries);


  // ESC key closes photo
  useEffect(() => {
    function handleEscape(
      event: KeyboardEvent
    ) {
      if (
        event.key === "Escape"
      ) {
        setLightboxImage(
          null
        );
      }
    }

    window.addEventListener(
      "keydown",
      handleEscape
    );

    return () => {
      window.removeEventListener(
        "keydown",
        handleEscape
      );
    };
  }, []);


  function startEditing(
    entry: Entry
  ) {
    setEditingEntryId(
      entry.id
    );

    setEditContent(
      entry.content
    );
  }


  function cancelEditing() {
    setEditingEntryId(
      null
    );

    setEditContent("");
  }


  async function saveEdit() {
    if (
      editingEntryId ===
        null ||
      !editContent.trim()
    ) {
      return;
    }

    setEditingLoading(
      true
    );

    const success =
      await onEditEntry(
        editingEntryId,
        editContent.trim()
      );

    setEditingLoading(
      false
    );

    if (success) {
      cancelEditing();
    }
  }


  async function deleteEntry(
    entryId: number
  ) {
    const confirmed =
      window.confirm(
        "이 기록을 삭제할까?"
      );

    if (!confirmed) {
      return;
    }

    setDeletingEntryId(
      entryId
    );

    await onDeleteEntry(
      entryId
    );

    setDeletingEntryId(
      null
    );
  }


  async function deleteImage(
    entryId: number,
    imageId: number
  ) {
    const confirmed =
      window.confirm(
        "이 사진을 삭제할까?"
      );

    if (!confirmed) {
      return;
    }

    setDeletingImageId(
      imageId
    );

    const success =
      await onDeleteImage(
        entryId,
        imageId
      );

    if (
      success &&
      lightboxImage?.id ===
        imageId
    ) {
      setLightboxImage(
        null
      );
    }

    setDeletingImageId(
      null
    );
  }


  if (loading) {
    return (
      <p className="text-sm text-text-muted">
        loading your days...
      </p>
    );
  }


  if (
    entries.length === 0
  ) {
    return (
      <div className="py-12 text-center">

        <p className="text-sm text-text-muted">
          nothing here yet.
        </p>

        <p className="mt-1 text-xs text-text-muted">
          둘 중 누가 먼저 쓸까?
        </p>

      </div>
    );
  }


  return (
    <>
      <div className="space-y-12">

        {Object.entries(
          groupedEntries
        ).map(
          ([
            dateLabel,
            dateEntries,
          ]) => (
            <section
              key={dateLabel}
            >

              <div className="mb-5 flex items-center gap-3">

                <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-orange">
                  {dateLabel}
                </h2>

                <div className="h-px flex-1 bg-border" />

              </div>


              {dateEntries.map(
                (entry) => {
                  const isMine =
                    entry.author.id ===
                    currentUserId;

                  const isEditing =
                    editingEntryId ===
                    entry.id;


                  return (
                    <article
                      key={entry.id}
                      className="border-b border-border py-6 first:pt-0"
                    >

                      <div className="mb-3 flex items-center justify-between gap-4">

                        <span className="text-sm font-medium text-orange-dark">
                          {
                            entry
                              .author
                              .username
                          }
                        </span>

                        <time className="text-xs text-text-muted">
                          {new Date(
                            entry.created_at
                          ).toLocaleTimeString(
                            undefined,
                            {
                              hour:
                                "numeric",

                              minute:
                                "2-digit",
                            }
                          )}
                        </time>

                      </div>


                      {isEditing ? (
                        <div>

                          <textarea
                            value={
                              editContent
                            }
                            onChange={(
                              event
                            ) =>
                              setEditContent(
                                event
                                  .target
                                  .value
                              )
                            }
                            autoFocus
                            rows={3}
                            className="
                              w-full
                              resize-none
                              rounded-2xl
                              border
                              border-orange-light
                              bg-surface
                              px-4
                              py-3
                              text-[15px]
                              leading-7
                              text-text
                              outline-none
                              focus:border-orange
                            "
                          />


                          <div className="mt-3 flex justify-end gap-3">

                            <button
                              type="button"
                              onClick={
                                cancelEditing
                              }
                              className="text-xs text-text-muted transition hover:text-orange-dark"
                            >
                              cancel
                            </button>


                            <button
                              type="button"
                              onClick={
                                saveEdit
                              }
                              disabled={
                                editingLoading ||
                                !editContent.trim()
                              }
                              className="
                                rounded-full
                                bg-orange
                                px-4
                                py-2
                                text-xs
                                font-medium
                                text-white
                                transition
                                hover:bg-orange-dark
                                disabled:opacity-40
                              "
                            >
                              {editingLoading
                                ? "saving..."
                                : "save"}
                            </button>

                          </div>

                        </div>
                      ) : (
                        <>

                          <p className="whitespace-pre-wrap text-[15px] leading-7 text-text">
                            {
                              entry.content
                            }
                          </p>


                          {/* Images */}
                          {entry.images &&
                            entry.images
                              .length >
                              0 && (
                              <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">

                                {entry.images.map(
                                  (
                                    image
                                  ) => (
                                    <div
                                      key={
                                        image.id
                                      }
                                      className="
                                        group
                                        relative
                                        overflow-hidden
                                        rounded-2xl
                                        bg-surface
                                      "
                                    >

                                      <button
                                        type="button"
                                        onClick={() =>
                                          setLightboxImage(
                                            image
                                          )
                                        }
                                        className="block w-full cursor-zoom-in"
                                      >
                                        <img
                                          src={`${process.env.NEXT_PUBLIC_API_URL}${image.file_path}`}
                                          alt={
                                            image.original_filename ??
                                            "journal image"
                                          }
                                          className="
                                            h-72
                                            w-full
                                            object-cover
                                            transition
                                            duration-200
                                            group-hover:scale-[1.01]
                                          "
                                        />
                                      </button>


                                      {isMine && (
                                        <button
                                          type="button"
                                          onClick={() =>
                                            deleteImage(
                                              entry.id,
                                              image.id
                                            )
                                          }
                                          disabled={
                                            deletingImageId ===
                                            image.id
                                          }
                                          className="
                                            absolute
                                            right-2
                                            top-2
                                            z-10
                                            flex
                                            h-7
                                            w-7
                                            items-center
                                            justify-center
                                            rounded-full
                                            bg-black/55
                                            text-sm
                                            text-white
                                            transition
                                            hover:bg-black/75
                                            disabled:opacity-40
                                          "
                                          aria-label="Delete image"
                                        >
                                          {deletingImageId ===
                                          image.id
                                            ? "…"
                                            : "×"}
                                        </button>
                                      )}

                                    </div>
                                  )
                                )}

                              </div>
                            )}


                          {isMine && (
                            <div className="mt-3 flex justify-end gap-3">

                              <button
                                type="button"
                                onClick={() =>
                                  startEditing(
                                    entry
                                  )
                                }
                                className="text-xs text-text-muted transition hover:text-orange-dark"
                              >
                                edit
                              </button>


                              <button
                                type="button"
                                onClick={() =>
                                  deleteEntry(
                                    entry.id
                                  )
                                }
                                disabled={
                                  deletingEntryId ===
                                  entry.id
                                }
                                className="text-xs text-text-muted transition hover:text-orange-dark disabled:opacity-40"
                              >
                                {deletingEntryId ===
                                entry.id
                                  ? "deleting..."
                                  : "delete"}
                              </button>

                            </div>
                          )}

                        </>
                      )}

                    </article>
                  );
                }
              )}

            </section>
          )
        )}

      </div>


      {/* Lightbox */}
      {lightboxImage && (
        <div
          className="
            fixed
            inset-0
            z-50
            flex
            items-center
            justify-center
            bg-black/80
            p-4
            sm:p-8
          "
          onClick={() =>
            setLightboxImage(
              null
            )
          }
        >

          <button
            type="button"
            onClick={() =>
              setLightboxImage(
                null
              )
            }
            className="
              absolute
              right-5
              top-5
              flex
              h-10
              w-10
              items-center
              justify-center
              rounded-full
              bg-white/15
              text-2xl
              text-white
              transition
              hover:bg-white/25
            "
            aria-label="Close image"
          >
            ×
          </button>


          <img
            src={`${process.env.NEXT_PUBLIC_API_URL}${lightboxImage.file_path}`}
            alt={
              lightboxImage.original_filename ??
              "journal image"
            }
            onClick={(
              event
            ) =>
              event.stopPropagation()
            }
            className="
              max-h-[90vh]
              max-w-[95vw]
              rounded-2xl
              object-contain
              shadow-2xl
            "
          />

        </div>
      )}

    </>
  );
}