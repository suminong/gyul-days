"use client";

import {
  ChangeEvent,
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


type Space = {
  id: number;
  name: string;
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

  const textareaRef =
    useRef<HTMLTextAreaElement>(null);

  const [entries, setEntries] =
    useState<Entry[]>([]);

  const [spaces, setSpaces] =
    useState<Space[]>([]);

  const [
    selectedSpaceId,
    setSelectedSpaceId,
  ] = useState<number | null>(null);

  const [
    currentUser,
    setCurrentUser,
  ] = useState<User | null>(null);

  const [content, setContent] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState("");

  const [message, setMessage] =
    useState("");


  // Rename space
  const [
    editingSpace,
    setEditingSpace,
  ] = useState(false);

  const [spaceName, setSpaceName] =
    useState("");


  // Create space
  const [
    creatingSpace,
    setCreatingSpace,
  ] = useState(false);

  const [
    newSpaceName,
    setNewSpaceName,
  ] = useState("");

  const [
    creatingSpaceLoading,
    setCreatingSpaceLoading,
  ] = useState(false);


  // Invite member
  const [
    invitingMember,
    setInvitingMember,
  ] = useState(false);

  const [
    inviteUsername,
    setInviteUsername,
  ] = useState("");

  const [
    inviteLoading,
    setInviteLoading,
  ] = useState(false);


  const selectedSpace = spaces.find(
    (space) =>
      space.id === selectedSpaceId
  );

  const groupedEntries =
    groupEntriesByDate(entries);


  function getToken() {
    return localStorage.getItem(
      "access_token"
    );
  }


  function clearNotices() {
    setError("");
    setMessage("");
  }


  function handleUnauthorized() {
    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "selected_space_id"
    );

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
      setError(
        "couldn't load your account."
      );
      return;
    }

    const data =
      await response.json();

    setCurrentUser(data);
  }


  async function loadSpaces() {
    const token = getToken();

    if (!token) {
      handleUnauthorized();
      return;
    }

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/spaces`,
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
      setError(
        "couldn't load your spaces."
      );

      setLoading(false);
      return;
    }

    const data: Space[] =
      await response.json();

    setSpaces(data);

    if (data.length > 0) {
      const savedSpaceId =
        localStorage.getItem(
          "selected_space_id"
        );

      const savedSpace =
        data.find(
          (space) =>
            space.id ===
            Number(savedSpaceId)
        );

      if (savedSpace) {
        setSelectedSpaceId(
          savedSpace.id
        );
      } else {
        setSelectedSpaceId(
          data[0].id
        );
      }
    } else {
      setSelectedSpaceId(null);
      setEntries([]);
      setLoading(false);
    }
  }


  async function loadEntries(
    spaceId: number
  ) {
    const token = getToken();

    if (!token) {
      handleUnauthorized();
      return;
    }

    setLoading(true);
    setError("");

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/spaces/${spaceId}/entries`,
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

    if (response.status === 403) {
      setError(
        "you don't have access to this space."
      );

      setLoading(false);
      return;
    }

    if (!response.ok) {
      setError(
        "couldn't load this space."
      );

      setLoading(false);
      return;
    }

    const data =
      await response.json();

    setEntries(data);
    setLoading(false);
  }


  useEffect(() => {
    loadCurrentUser();
    loadSpaces();
  }, []);


  useEffect(() => {
    if (selectedSpaceId !== null) {
      localStorage.setItem(
        "selected_space_id",
        String(selectedSpaceId)
      );

      loadEntries(
        selectedSpaceId
      );

      setEditingSpace(false);
      setInvitingMember(false);
    }
  }, [selectedSpaceId]);


  function resizeTextarea() {
    const textarea =
      textareaRef.current;

    if (!textarea) {
      return;
    }

    textarea.style.height =
      "auto";

    textarea.style.height =
      `${textarea.scrollHeight}px`;
  }


  function handleContentChange(
    event: ChangeEvent<HTMLTextAreaElement>
  ) {
    setContent(
      event.target.value
    );

    requestAnimationFrame(() => {
      resizeTextarea();
    });
  }


  function handleSpaceChange(
    event: ChangeEvent<HTMLSelectElement>
  ) {
    clearNotices();

    setEntries([]);

    setSelectedSpaceId(
      Number(event.target.value)
    );
  }


  async function saveEntry() {
    if (
      !content.trim() ||
      saving ||
      selectedSpaceId === null
    ) {
      return;
    }

    const token = getToken();

    if (!token) {
      handleUnauthorized();
      return;
    }

    setSaving(true);
    clearNotices();

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/spaces/${selectedSpaceId}/entries`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",

            Authorization:
              `Bearer ${token}`,
          },

          body: JSON.stringify({
            content:
              content.trim(),
          }),
        }
      );

      if (
        response.status === 401
      ) {
        handleUnauthorized();
        return;
      }

      if (!response.ok) {
        throw new Error();
      }

      const newEntry =
        await response.json();

      setEntries(
        (currentEntries) => [
          newEntry,
          ...currentEntries,
        ]
      );

      setContent("");

      if (
        textareaRef.current
      ) {
        textareaRef.current.style.height =
          "auto";
      }
    } catch {
      setError(
        "couldn't save this entry."
      );
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
    if (
      (
        event.metaKey ||
        event.ctrlKey
      ) &&
      event.key === "Enter"
    ) {
      event.preventDefault();
      saveEntry();
    }
  }


  async function createSpace(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (!newSpaceName.trim()) {
      return;
    }

    const token = getToken();

    if (!token) {
      handleUnauthorized();
      return;
    }

    setCreatingSpaceLoading(true);
    clearNotices();

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/spaces`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",

            Authorization:
              `Bearer ${token}`,
          },

          body: JSON.stringify({
            name:
              newSpaceName.trim(),
          }),
        }
      );

      if (
        response.status === 401
      ) {
        handleUnauthorized();
        return;
      }

      if (!response.ok) {
        throw new Error();
      }

      const newSpace: Space =
        await response.json();

      setSpaces(
        (currentSpaces) => [
          newSpace,
          ...currentSpaces,
        ]
      );

      setSelectedSpaceId(
        newSpace.id
      );

      setNewSpaceName("");
      setCreatingSpace(false);

      setMessage(
        `"${newSpace.name}" 만들었어 🍊`
      );
    } catch {
      setError(
        "couldn't create the space."
      );
    } finally {
      setCreatingSpaceLoading(false);
    }
  }


  async function renameSpace() {
    if (
      selectedSpaceId === null ||
      !spaceName.trim()
    ) {
      return;
    }

    const token = getToken();

    if (!token) {
      handleUnauthorized();
      return;
    }

    clearNotices();

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/spaces/${selectedSpaceId}`,
      {
        method: "PATCH",

        headers: {
          "Content-Type":
            "application/json",

          Authorization:
            `Bearer ${token}`,
        },

        body: JSON.stringify({
          name:
            spaceName.trim(),
        }),
      }
    );

    if (
      response.status === 401
    ) {
      handleUnauthorized();
      return;
    }

    if (
      response.status === 403
    ) {
      setError(
        "only the space owner can rename this space."
      );
      return;
    }

    if (!response.ok) {
      setError(
        "couldn't rename this space."
      );
      return;
    }

    const updatedSpace =
      await response.json();

    setSpaces(
      (currentSpaces) =>
        currentSpaces.map(
          (space) =>
            space.id ===
            updatedSpace.id
              ? updatedSpace
              : space
        )
    );

    setEditingSpace(false);

    setMessage(
      "space name updated."
    );
  }


  async function inviteMember(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (
      selectedSpaceId === null ||
      !inviteUsername.trim()
    ) {
      return;
    }

    const token = getToken();

    if (!token) {
      handleUnauthorized();
      return;
    }

    setInviteLoading(true);
    clearNotices();

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/spaces/${selectedSpaceId}/members`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",

            Authorization:
              `Bearer ${token}`,
          },

          body: JSON.stringify({
            username:
              inviteUsername.trim(),
          }),
        }
      );

      if (
        response.status === 401
      ) {
        handleUnauthorized();
        return;
      }

      const data =
        await response.json();

      if (
        response.status === 403
      ) {
        setError(
          data.detail ??
            "only the owner can invite members."
        );
        return;
      }

      if (
        response.status === 404
      ) {
        setError(
          "couldn't find that username."
        );
        return;
      }

      if (
        response.status === 409
      ) {
        setError(
          "that person is already in this space."
        );
        return;
      }

      if (!response.ok) {
        throw new Error();
      }

      setMessage(
        `${inviteUsername.trim()} joined this space 🍊`
      );

      setInviteUsername("");
      setInvitingMember(false);

    } catch {
      setError(
        "couldn't add this person."
      );
    } finally {
      setInviteLoading(false);
    }
  }


  function startEditingSpace() {
    if (!selectedSpace) {
      return;
    }

    clearNotices();

    setSpaceName(
      selectedSpace.name
    );

    setEditingSpace(true);
    setCreatingSpace(false);
    setInvitingMember(false);
  }


  function startCreatingSpace() {
    clearNotices();

    setCreatingSpace(true);
    setEditingSpace(false);
    setInvitingMember(false);
  }


  function startInvitingMember() {
    clearNotices();

    setInvitingMember(true);
    setEditingSpace(false);
    setCreatingSpace(false);
  }


  function closeSpaceTools() {
    setEditingSpace(false);
    setCreatingSpace(false);
    setInvitingMember(false);

    setSpaceName("");
    setNewSpaceName("");
    setInviteUsername("");

    clearNotices();
  }


  function logout() {
    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "selected_space_id"
    );

    router.push("/login");
  }


  return (
    <main className="min-h-screen bg-background text-text">

      <div className="mx-auto max-w-2xl px-5 py-10 sm:px-6 sm:py-14">

        {/* Header */}
        <header className="mb-10">

          <div className="mb-6 flex items-start justify-between">

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

          </div>


          {/* Space title + controls */}
          <div className="mb-2 flex items-center justify-between">

            <p className="text-[11px] font-medium uppercase tracking-[0.15em] text-text-muted">
              space
            </p>

            <button
              type="button"
              onClick={startCreatingSpace}
              className="text-xs font-medium text-orange-dark transition hover:text-orange"
            >
              + new space
            </button>

          </div>


          {/* Space selector */}
          {spaces.length > 0 && !editingSpace && (
            <div className="flex gap-2">

              <select
                value={
                  selectedSpaceId ?? ""
                }
                onChange={
                  handleSpaceChange
                }
                className="
                  min-w-0
                  flex-1
                  rounded-2xl
                  border
                  border-border
                  bg-surface
                  px-4
                  py-3
                  text-sm
                  font-medium
                  text-orange-dark
                  outline-none
                  transition
                  focus:border-orange
                "
              >

                {spaces.map(
                  (space) => (
                    <option
                      key={space.id}
                      value={space.id}
                    >
                      {space.name}
                    </option>
                  )
                )}

              </select>


              <button
                type="button"
                onClick={
                  startEditingSpace
                }
                className="
                  rounded-2xl
                  border
                  border-border
                  bg-surface
                  px-4
                  text-sm
                  text-text-muted
                  transition
                  hover:border-orange-light
                  hover:text-orange-dark
                "
              >
                edit
              </button>


              <button
                type="button"
                onClick={
                  startInvitingMember
                }
                className="
                  rounded-2xl
                  border
                  border-border
                  bg-surface
                  px-4
                  text-sm
                  text-text-muted
                  transition
                  hover:border-orange-light
                  hover:text-orange-dark
                "
              >
                invite
              </button>

            </div>
          )}


          {/* Rename space */}
          {editingSpace && (
            <div className="flex gap-2">

              <input
                value={spaceName}
                onChange={(event) =>
                  setSpaceName(
                    event.target.value
                  )
                }
                autoFocus
                className="
                  min-w-0
                  flex-1
                  rounded-2xl
                  border
                  border-orange
                  bg-surface
                  px-4
                  py-3
                  text-sm
                  text-text
                  outline-none
                "
              />

              <button
                type="button"
                onClick={renameSpace}
                className="
                  rounded-2xl
                  bg-orange
                  px-4
                  text-sm
                  text-white
                  hover:bg-orange-dark
                "
              >
                save
              </button>

              <button
                type="button"
                onClick={
                  closeSpaceTools
                }
                className="
                  rounded-2xl
                  border
                  border-border
                  bg-surface
                  px-4
                  text-sm
                  text-text-muted
                "
              >
                cancel
              </button>

            </div>
          )}


          {/* Create new space */}
          {creatingSpace && (
            <form
              onSubmit={createSpace}
              className="mt-3 rounded-3xl border border-border bg-surface p-4"
            >

              <p className="mb-3 text-sm font-medium text-orange-dark">
                새 Space 만들기
              </p>

              <div className="flex gap-2">

                <input
                  value={
                    newSpaceName
                  }
                  onChange={(event) =>
                    setNewSpaceName(
                      event.target.value
                    )
                  }
                  placeholder="space name"
                  autoFocus
                  className="
                    min-w-0
                    flex-1
                    rounded-2xl
                    border
                    border-border
                    bg-background
                    px-4
                    py-3
                    text-sm
                    text-text
                    outline-none
                    focus:border-orange
                  "
                />

                <button
                  type="submit"
                  disabled={
                    creatingSpaceLoading ||
                    !newSpaceName.trim()
                  }
                  className="
                    rounded-2xl
                    bg-orange
                    px-4
                    text-sm
                    text-white
                    hover:bg-orange-dark
                    disabled:opacity-40
                  "
                >
                  {creatingSpaceLoading
                    ? "creating..."
                    : "create"}
                </button>

                <button
                  type="button"
                  onClick={
                    closeSpaceTools
                  }
                  className="
                    rounded-2xl
                    border
                    border-border
                    px-4
                    text-sm
                    text-text-muted
                  "
                >
                  cancel
                </button>

              </div>

            </form>
          )}


          {/* Invite member */}
          {invitingMember &&
            selectedSpaceId !== null && (
              <form
                onSubmit={
                  inviteMember
                }
                className="mt-3 rounded-3xl border border-border bg-surface p-4"
              >

                <p className="text-sm font-medium text-orange-dark">
                  친구 추가하기
                </p>

                <p className="mt-1 text-xs text-text-muted">
                  친구의 Gyul Days username을 입력해.
                </p>

                <div className="mt-3 flex gap-2">

                  <input
                    value={
                      inviteUsername
                    }
                    onChange={(
                      event
                    ) =>
                      setInviteUsername(
                        event.target
                          .value
                      )
                    }
                    placeholder="username"
                    autoFocus
                    className="
                      min-w-0
                      flex-1
                      rounded-2xl
                      border
                      border-border
                      bg-background
                      px-4
                      py-3
                      text-sm
                      text-text
                      outline-none
                      focus:border-orange
                    "
                  />

                  <button
                    type="submit"
                    disabled={
                      inviteLoading ||
                      !inviteUsername.trim()
                    }
                    className="
                      rounded-2xl
                      bg-orange
                      px-4
                      text-sm
                      text-white
                      hover:bg-orange-dark
                      disabled:opacity-40
                    "
                  >
                    {inviteLoading
                      ? "adding..."
                      : "add"}
                  </button>

                  <button
                    type="button"
                    onClick={
                      closeSpaceTools
                    }
                    className="
                      rounded-2xl
                      border
                      border-border
                      px-4
                      text-sm
                      text-text-muted
                    "
                  >
                    cancel
                  </button>

                </div>

              </form>
            )}

        </header>


        {/* Success / Error */}
        {message && (
          <p className="mb-6 rounded-2xl bg-orange-light/20 px-4 py-3 text-sm text-orange-dark">
            {message}
          </p>
        )}

        {error && (
          <p className="mb-6 rounded-2xl bg-orange-light/20 px-4 py-3 text-sm text-orange-dark">
            {error}
          </p>
        )}


        {/* No spaces */}
        {!loading &&
          spaces.length === 0 &&
          !creatingSpace && (
            <div className="mb-12 rounded-3xl border border-border bg-surface p-8 text-center">

              <p className="text-sm font-medium text-orange-dark">
                아직 Space가 없어.
              </p>

              <p className="mt-2 text-xs text-text-muted">
                위의 + new space를 눌러서 하나 만들어봐.
              </p>

            </div>
          )}


        {/* Quick capture */}
        {selectedSpaceId !== null && (
          <form
            onSubmit={createEntry}
            className="mb-14"
          >

            <div className="rounded-3xl border border-border bg-surface p-1 shadow-sm">

              <textarea
                ref={textareaRef}
                value={content}
                onChange={
                  handleContentChange
                }
                onKeyDown={
                  handleKeyDown
                }
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
                  disabled={
                    saving ||
                    !content.trim()
                  }
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
                  {saving
                    ? "saving..."
                    : "save"}
                </button>

              </div>

            </div>

          </form>
        )}


        {/* Feed */}
        <section>

          {loading && (
            <p className="text-sm text-text-muted">
              loading your days...
            </p>
          )}


          {!loading &&
            selectedSpaceId !== null &&
            entries.length === 0 && (
              <div className="py-12 text-center">

                <p className="text-sm text-text-muted">
                  nothing here yet.
                </p>

                <p className="mt-1 text-xs text-text-muted">
                  둘 중 누가 먼저 쓸까?
                </p>

              </div>
            )}


          {!loading &&
            entries.length > 0 && (
              <div className="space-y-12">

                {Object.entries(
                  groupedEntries
                ).map(
                  ([
                    dateLabel,
                    dateEntries,
                  ]) => (
                    <section
                      key={
                        dateLabel
                      }
                    >

                      <div className="mb-5 flex items-center gap-3">

                        <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-orange">
                          {dateLabel}
                        </h2>

                        <div className="h-px flex-1 bg-border" />

                      </div>


                      {dateEntries.map(
                        (entry) => (
                          <article
                            key={
                              entry.id
                            }
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

                            <p className="whitespace-pre-wrap text-[15px] leading-7 text-text">
                              {
                                entry.content
                              }
                            </p>

                          </article>
                        )
                      )}

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