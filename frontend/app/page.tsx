"use client";

import {
  FormEvent,
  KeyboardEvent,
  useEffect,
  useRef,
  useState,
} from "react";
import { useRouter } from "next/navigation";


type Author = {
  id: number;
  username: string;
};


type Entry = {
  id: number;
  content: string;
  created_at: string;
  author: Author;
};


type User = {
  id: number;
  username: string;
  email: string;
  created_at: string;
};


function getDateLabel(dateString: string) {
  const date = new Date(dateString);

  const today = new Date();

  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);

  const isSameDay = (
    first: Date,
    second: Date
  ) =>
    first.getFullYear() === second.getFullYear() &&
    first.getMonth() === second.getMonth() &&
    first.getDate() === second.getDate();

  if (isSameDay(date, today)) {
    return "today";
  }

  if (isSameDay(date, yesterday)) {
    return "yesterday";
  }

  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
}


function groupEntriesByDate(entries: Entry[]) {
  return entries.reduce<Record<string, Entry[]>>(
    (groups, entry) => {
      const label = getDateLabel(entry.created_at);

      if (!groups[label]) {
        groups[label] = [];
      }

      groups[label].push(entry);

      return groups;
    },
    {}
  );
}


export default function Home() {
  const router = useRouter();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const [entries, setEntries] = useState<Entry[]>([]);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [content, setContent] = useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");


  function getToken() {
    return localStorage.getItem("access_token");
  }


  function handleUnauthorized() {
    localStorage.removeItem("access_token");
    router.push("/login");
  }


  async function loadCurrentUser() {
    const token = getToken();

    if (!token) {
      handleUnauthorized();
      return;
    }

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/auth/me`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (response.status === 401) {
      handleUnauthorized();
      return;
    }

    if (!response.ok) {
      setError("couldn't load your account.");
      return;
    }

    const data = await response.json();
    setCurrentUser(data);
  }


  async function loadEntries() {
    const token = getToken();

    if (!token) {
      handleUnauthorized();
      return;
    }

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/entries`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (response.status === 401) {
      handleUnauthorized();
      return;
    }

    if (!response.ok) {
      setError("couldn't load your entries.");
      setLoading(false);
      return;
    }

    const data = await response.json();

    setEntries(data);
    setLoading(false);
  }


  useEffect(() => {
    loadCurrentUser();
    loadEntries();
  }, []);


  function resizeTextarea() {
    const textarea = textareaRef.current;

    if (!textarea) {
      return;
    }

    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;
  }


  function handleContentChange(
    event: React.ChangeEvent<HTMLTextAreaElement>
  ) {
    setContent(event.target.value);

    requestAnimationFrame(() => {
      resizeTextarea();
    });
  }


  async function saveEntry() {
    if (!content.trim() || saving) {
      return;
    }

    const token = getToken();

    if (!token) {
      handleUnauthorized();
      return;
    }

    setSaving(true);
    setError("");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/entries`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            content: content.trim(),
          }),
        }
      );

      if (response.status === 401) {
        handleUnauthorized();
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to create entry");
      }

      const newEntry = await response.json();

      setEntries((currentEntries) => [
        newEntry,
        ...currentEntries,
      ]);

      setContent("");

      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    } catch {
      setError("couldn't save this entry. try again.");
    } finally {
      setSaving(false);
    }
  }


  async function createEntry(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();
    await saveEntry();
  }


  function handleKeyDown(
    event: KeyboardEvent<HTMLTextAreaElement>
  ) {
    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
      event.preventDefault();
      saveEntry();
    }
  }


  function logout() {
    localStorage.removeItem("access_token");
    router.push("/login");
  }


  const groupedEntries = groupEntriesByDate(entries);


  return (
    <main className="min-h-screen bg-background text-text">
      <div className="mx-auto max-w-2xl px-5 py-10 sm:px-6 sm:py-14">

        {/* Header */}
        <header className="mb-12 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-orange-dark">
              귤 데이즈
            </h1>

            <p className="mt-1 text-xs text-text-muted">
              메이반빠!
            </p>
          </div>

          <div className="flex items-center gap-4">
            {currentUser && (
              <span className="text-sm text-text-muted">
                {currentUser.username}
              </span>
            )}

            <button
              onClick={logout}
              className="text-xs text-text-muted transition hover:text-orange-dark"
            >
              log out
            </button>
          </div>
        </header>


        {/* Quick capture */}
        <form
          onSubmit={createEntry}
          className="mb-14"
        >
          <div className="rounded-3xl border border-border bg-surface p-1 shadow-sm">
            <textarea
              ref={textareaRef}
              value={content}
              onChange={handleContentChange}
              onKeyDown={handleKeyDown}
              placeholder="뭐야?"
              rows={3}
              className="
                max-h-80
                min-h-28
                w-full
                resize-none
                overflow-y-auto
                bg-transparent
                px-5
                pt-5
                pb-3
                text-base
                leading-7
                text-text
                outline-none
                placeholder:text-text-muted
              "
            />

            <div className="flex items-center justify-between px-4 pb-3">
              <span className="text-xs text-text-muted">
                ⌘ + enter to save
              </span>

              <button
                type="submit"
                disabled={saving || !content.trim()}
                className="
                  rounded-full
                  bg-orange
                  px-5
                  py-2
                  text-sm
                  font-medium
                  text-white
                  transition
                  hover:bg-orange-dark
                  disabled:cursor-not-allowed
                  disabled:opacity-40
                "
              >
                {saving ? "saving..." : "save"}
              </button>
            </div>
          </div>

          {error && (
            <p className="mt-3 text-sm text-orange-dark">
              {error}
            </p>
          )}
        </form>


        {/* Feed */}
        <section>

          {loading && (
            <p className="text-sm text-text-muted">
              loading your days...
            </p>
          )}


          {!loading && entries.length === 0 && (
            <div className="py-12 text-center">
              <p className="text-sm text-text-muted">
                nothing here yet.
              </p>

              <p className="mt-1 text-xs text-text-muted">
                write down something small.
              </p>
            </div>
          )}


          {!loading && entries.length > 0 && (
            <div className="space-y-12">
              {Object.entries(groupedEntries).map(
                ([dateLabel, dateEntries]) => (
                  <section key={dateLabel}>

                    <div className="mb-5 flex items-center gap-3">
                      <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-orange">
                        {dateLabel}
                      </h2>

                      <div className="h-px flex-1 bg-border" />
                    </div>


                    <div>
                      {dateEntries.map((entry) => (
                        <article
                          key={entry.id}
                          className="border-b border-border py-6 first:pt-0"
                        >
                          <div className="mb-3 flex items-center justify-between gap-4">

                            <span className="text-sm font-medium text-orange-dark">
                              {entry.author.username}
                            </span>

                            <time className="text-xs text-text-muted">
                              {new Date(
                                entry.created_at
                              ).toLocaleTimeString(
                                undefined,
                                {
                                  hour: "numeric",
                                  minute: "2-digit",
                                }
                              )}
                            </time>

                          </div>

                          <p className="whitespace-pre-wrap text-[15px] leading-7 text-text">
                            {entry.content}
                          </p>
                        </article>
                      ))}
                    </div>

                  </section>
                )
              )}
            </div>
          )}

        </section>

      </div>
    </main>
  );
}