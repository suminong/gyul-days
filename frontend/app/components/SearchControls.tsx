"use client";


type SearchControlsProps = {
  query: string;

  tags: string[];

  selectedTag: string;

  onQueryChange: (
    value: string
  ) => void;

  onTagChange: (
    tag: string
  ) => void;
};


export default function SearchControls({
  query,
  tags,
  selectedTag,
  onQueryChange,
  onTagChange,
}: SearchControlsProps) {
  return (
    <div className="mb-10">

      {/* Search */}
      <div className="relative">

        <input
          type="search"
          value={query}
          onChange={(event) =>
            onQueryChange(
              event.target.value
            )
          }
          placeholder="search our days..."
          className="
            w-full
            rounded-2xl
            border
            border-border
            bg-surface
            px-4
            py-3
            text-sm
            text-text
            outline-none
            transition
            placeholder:text-text-muted
            focus:border-orange
          "
        />

      </div>


      {/* Tag filters */}
      {tags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">

          <button
            type="button"
            onClick={() =>
              onTagChange("all")
            }
            className={`
              rounded-full
              px-3
              py-1.5
              text-xs
              transition

              ${
                selectedTag === "all"
                  ? "bg-orange text-white"
                  : "border border-border bg-surface text-text-muted hover:text-orange-dark"
              }
            `}
          >
            all
          </button>


          {tags.map(
            (tag) => (
              <button
                key={tag}
                type="button"
                onClick={() =>
                  onTagChange(tag)
                }
                className={`
                  rounded-full
                  px-3
                  py-1.5
                  text-xs
                  transition

                  ${
                    selectedTag === tag
                      ? "bg-orange text-white"
                      : "border border-border bg-surface text-text-muted hover:text-orange-dark"
                  }
                `}
              >
                #{tag}
              </button>
            )
          )}

        </div>
      )}

    </div>
  );
}