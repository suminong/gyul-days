"use client";

import {
  useMemo,
  useState,
} from "react";

import type { Entry } from "../types";


type CategoryOverviewProps = {
  entries: Entry[];

  selectedTag: string;

  onSelectTag: (
    tag: string
  ) => void;
};


export default function CategoryOverview({
  entries,
  selectedTag,
  onSelectTag,
}: CategoryOverviewProps) {

  const [
    expanded,
    setExpanded,
  ] = useState(false);


  const categories =
    useMemo(() => {

      const counts =
        new Map<string, number>();


      entries.forEach(
        (entry) => {

          (
            entry.tag_links ?? []
          ).forEach(
            (link) => {

              const name =
                link.tag.name;

              counts.set(
                name,
                (
                  counts.get(name) ?? 0
                ) + 1
              );

            }
          );

        }
      );


      return Array.from(
        counts.entries()
      )
        .map(
          ([name, count]) => ({
            name,
            count,
          })
        )
        .sort(
          (a, b) =>
            b.count - a.count
        );

    }, [entries]);


  if (
    categories.length === 0
  ) {
    return null;
  }


  const visibleCategories =
    expanded
      ? categories
      : categories.slice(0, 5);


  return (
    <section className="mb-8">

      <div className="mb-3 flex items-center justify-between">

        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-green-dark">
          categories
        </p>


        {categories.length > 5 && (
          <button
            type="button"
            onClick={() =>
              setExpanded(
                (current) =>
                  !current
              )
            }
            className="
              text-xs
              text-text-muted
              transition
              hover:text-green-dark
            "
          >
            {expanded
              ? "show less"
              : "view all"}
          </button>
        )}

      </div>


      <div
        className="
          rounded-3xl
          border
          border-green-light
          bg-white/35
          p-4
          backdrop-blur-md
        "
      >

        <div className="flex flex-wrap gap-2">

          <button
            type="button"
            onClick={() =>
              onSelectTag("all")
            }
            className={`
              rounded-full
              border
              px-3
              py-1.5
              text-xs
              transition

              ${
                selectedTag === "all"
                  ? `
                    border-green
                    bg-green
                    text-white
                  `
                  : `
                    border-green-light
                    bg-white/40
                    text-green-dark
                    hover:bg-green-light/30
                  `
              }
            `}
          >
            all

            <span className="ml-1 opacity-60">
              {entries.length}
            </span>
          </button>


          {visibleCategories.map(
            (category) => {

              const selected =
                selectedTag ===
                category.name;

              return (
                <button
                  key={
                    category.name
                  }
                  type="button"
                  onClick={() =>
                    onSelectTag(
                      category.name
                    )
                  }
                  className={`
                    rounded-full
                    border
                    px-3
                    py-1.5
                    text-xs
                    transition

                    ${
                      selected
                        ? `
                          border-orange
                          bg-orange-light/40
                          text-orange-dark
                        `
                        : `
                          border-green-light
                          bg-white/40
                          text-green-dark
                          hover:border-orange-light
                          hover:text-orange-dark
                        `
                    }
                  `}
                >
                  #{category.name}

                  <span className="ml-1 opacity-50">
                    {category.count}
                  </span>

                </button>
              );
            }
          )}

        </div>

      </div>

    </section>
  );
}