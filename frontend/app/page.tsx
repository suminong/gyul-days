"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import { useRouter } from "next/navigation";

import JournalFeed from "./components/JournalFeed";
import QuickCapture from "./components/QuickCapture";
import SearchControls from "./components/SearchControls";
import SpaceControls from "./components/SpaceControls";

import {
  Entry,
  Space,
  User,
} from "./types";

import StreakCard from "./components/StreakCard";


export default function Home() {
  const router = useRouter();

  const [entries, setEntries] =
    useState<Entry[]>([]);
  
  const [
    streakRefreshKey,
    setStreakRefreshKey,
  ] = useState(0);

  const [spaces, setSpaces] =
    useState<Space[]>([]);

  const [
    selectedSpaceId,
    setSelectedSpaceId,
  ] = useState<
    number | "all" | null
  >(
    null
  );

  const [
    currentUser,
    setCurrentUser,
  ] = useState<User | null>(
    null
  );

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
  
  const [
    searchQuery,
    setSearchQuery,
  ] = useState("");

  const [
    selectedTag,
    setSelectedTag,
  ] = useState("all");

  const availableTags =
    useMemo(() => {
      const tagNames =
        entries.flatMap(
          (entry) =>
            (
              entry.tag_links ??
              []
            ).map(
              (link) =>
                link.tag.name
            )
        );


      return Array.from(
        new Set(tagNames)
      ).sort();

    }, [entries]);
  
  const filteredEntries =
    useMemo(() => {
      const normalizedQuery =
        searchQuery
          .trim()
          .toLowerCase();


      return entries.filter(
        (entry) => {

          // Tag filter
          const matchesTag =
            selectedTag === "all" ||
            (
              entry.tag_links ??
              []
            ).some(
              (link) =>
                link.tag.name ===
                selectedTag
            );


          // Search text
          const searchableText = [
            entry.content,

            entry.author.username,

            ...(
              entry.tag_links ??
              []
            ).map(
              (link) =>
                link.tag.name
            ),
          ]
            .join(" ")
            .toLowerCase();


          const matchesQuery =
            normalizedQuery === "" ||
            searchableText.includes(
              normalizedQuery
            );


          return (
            matchesTag &&
            matchesQuery
          );
        }
      );

    }, [
      entries,
      searchQuery,
      selectedTag,
    ]);

  useEffect(() => {
    if (
      selectedTag !== "all" &&
      !availableTags.includes(
        selectedTag
      )
    ) {
      setSelectedTag("all");
    }
  }, [
    availableTags,
    selectedTag,
  ]);


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
          Authorization:
            `Bearer ${token}`,
        },
      }
    );


    if (
      response.status === 401
    ) {
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
          Authorization:
            `Bearer ${token}`,
        },
      }
    );


    if (
      response.status === 401
    ) {
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


    if (data.length === 0) {
      setSelectedSpaceId(
        null
      );

      setLoading(false);

      return;
    }


    const savedSpaceId =
      localStorage.getItem(
        "selected_space_id"
      );


    if (savedSpaceId === "all") {
      setSelectedSpaceId("all");
      return;
    }


    const savedSpace =
      data.find(
        (space) =>
          space.id ===
          Number(savedSpaceId)
      );


    setSelectedSpaceId(
      savedSpace
        ? savedSpace.id
        : data[0].id
    );
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


    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/spaces/${spaceId}/entries`,
      {
        headers: {
          Authorization:
            `Bearer ${token}`,
        },
      }
    );


    if (
      response.status === 401
    ) {
      handleUnauthorized();
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
    if (
      selectedSpaceId === null
    ) {
      return;
    }

    setSearchQuery("");
    setSelectedTag("all");


    if (
      selectedSpaceId === "all"
    ) {
      localStorage.setItem(
        "selected_space_id",
        "all"
      );

      loadAllEntries();

      return;
    }


    localStorage.setItem(
      "selected_space_id",
      String(selectedSpaceId)
    );


    loadEntries(
      selectedSpaceId
    );

  }, [
    selectedSpaceId,
    spaces,
  ]);



  async function loadAllEntries() {
    const token = getToken();

    if (!token) {
      handleUnauthorized();
      return;
    }

    setLoading(true);

    try {
      const responses =
        await Promise.all(
          spaces.map(
            (space) =>
              fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/spaces/${space.id}/entries`,
                {
                  headers: {
                    Authorization:
                      `Bearer ${token}`,
                  },
                }
              )
          )
        );


      if (
        responses.some(
          (response) =>
            !response.ok
        )
      ) {
        setError(
          "couldn't load all spaces."
        );

        setLoading(false);
        return;
      }


      const entryGroups =
        await Promise.all(
          responses.map(
            (response) =>
              response.json()
          )
        );


      const allEntries: Entry[] =
        entryGroups
          .flat()
          .sort(
            (a, b) =>
              new Date(
                b.created_at
              ).getTime() -
              new Date(
                a.created_at
              ).getTime()
          );


      setEntries(allEntries);

    } finally {
      setLoading(false);
    }
  }


  function getEntrySpaceId(
    entryId: number
  ): number | null {
    const entry = entries.find(
      (entry) =>
        entry.id === entryId
    );

    if (
      typeof entry?.space_id ===
      "number"
    ) {
      return entry.space_id;
    }

    if (
      typeof selectedSpaceId ===
      "number"
    ) {
      return selectedSpaceId;
    }

    return null;
  }

  async function saveEntry(
    files: File[]
  ): Promise<boolean> {
    if (
      !content.trim() ||
      saving ||
      selectedSpaceId === null
    ) {
      return false;
    }


    const token = getToken();

    if (!token) {
      handleUnauthorized();
      return false;
    }


    setSaving(true);
    clearNotices();


    try {
      // 1. First create the text entry
      const entryResponse =
        await fetch(
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
        entryResponse.status ===
        401
      ) {
        handleUnauthorized();
        return false;
      }


      if (
        !entryResponse.ok
      ) {
        throw new Error(
          "Failed to create entry"
        );
      }


      const newEntry: Entry =
        await entryResponse.json();


      // 2. Upload each selected image
      let imageUploadFailed =
        false;


      for (const file of files) {
        const formData =
          new FormData();

        formData.append(
          "file",
          file
        );


        const imageResponse =
          await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/spaces/${selectedSpaceId}/entries/${newEntry.id}/images`,
            {
              method: "POST",

              headers: {
                Authorization:
                  `Bearer ${token}`,
              },

              body: formData,
            }
          );


        if (
          imageResponse.status ===
          401
        ) {
          handleUnauthorized();
          return false;
        }


        if (
          !imageResponse.ok
        ) {
          imageUploadFailed =
            true;
        }
      }


      // 3. Clear text
      setContent("");


      // 4. Reload feed so uploaded
      // images appear immediately
      await loadEntries(
        selectedSpaceId
      );

      setStreakRefreshKey(
        (current) => current + 1
      );


      if (
        imageUploadFailed
      ) {
        setError(
          "the entry was saved, but one or more photos couldn't upload."
        );
      }


      return true;

    } catch {
      setError(
        "couldn't save this entry."
      );

      return false;

    } finally {
      setSaving(false);
    }
  }


  async function createSpace(
    name: string
  ): Promise<boolean> {
    const token = getToken();

    if (!token) {
      handleUnauthorized();
      return false;
    }


    clearNotices();


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
          name,
        }),
      }
    );


    if (!response.ok) {
      setError(
        "couldn't create the space."
      );

      return false;
    }


    const newSpace: Space =
      await response.json();


    setSpaces(
      (current) => [
        newSpace,
        ...current,
      ]
    );


    setSelectedSpaceId(
      newSpace.id
    );


    setMessage(
      `"${newSpace.name}" 만들었어 🍊`
    );


    return true;
  }


  async function renameSpace(
    name: string
  ): Promise<boolean> {
    if (
      selectedSpaceId === null
    ) {
      return false;
    }


    const token = getToken();

    if (!token) {
      handleUnauthorized();
      return false;
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
          name,
        }),
      }
    );


    const data =
      await response.json();


    if (
      response.status === 403
    ) {
      setError(
        "only the owner can rename this space."
      );

      return false;
    }


    if (!response.ok) {
      setError(
        "couldn't rename this space."
      );

      return false;
    }


    setSpaces(
      (current) =>
        current.map(
          (space) =>
            space.id ===
            data.id
              ? data
              : space
        )
    );


    setMessage(
      "space name updated."
    );


    return true;
  }


  async function inviteMember(
    username: string
  ): Promise<boolean> {
    if (
      selectedSpaceId === null
    ) {
      return false;
    }


    const token = getToken();

    if (!token) {
      handleUnauthorized();
      return false;
    }


    clearNotices();


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

        body:
          JSON.stringify({
            username,
          }),
      }
    );


    const data =
      await response.json();


    if (
      response.status === 404
    ) {
      setError(
        "couldn't find that username."
      );

      return false;
    }


    if (
      response.status === 409
    ) {
      setError(
        "that person is already in this space."
      );

      return false;
    }


    if (
      response.status === 403
    ) {
      setError(
        data.detail ??
          "only the owner can invite people."
      );

      return false;
    }


    if (!response.ok) {
      setError(
        "couldn't add this person."
      );

      return false;
    }


    setMessage(
      `${username} joined this space 🍊`
    );


    return true;
  }

  
  async function editEntry(
    entryId: number,
    newContent: string
  ): Promise<boolean> {
    const spaceId =
      getEntrySpaceId(entryId);

    if (spaceId === null) {
      return false;
    }

    const token = getToken();

    if (!token) {
      handleUnauthorized();
      return false;
    }

    clearNotices();


    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/spaces/${spaceId}/entries/${entryId}`,
      {
        method: "PATCH",

        headers: {
          "Content-Type":
            "application/json",

          Authorization:
            `Bearer ${token}`,
        },

        body: JSON.stringify({
          content: newContent,
        }),
      }
    );


    if (
      response.status === 401
    ) {
      handleUnauthorized();
      return false;
    }


    if (
      response.status === 403
    ) {
      setError(
        "you can only edit your own entries."
      );

      return false;
    }


    if (!response.ok) {
      setError(
        "couldn't edit this entry."
      );

      return false;
    }


    const updatedEntry: Entry =
      await response.json();


    setEntries(
      (currentEntries) =>
        currentEntries.map(
          (entry) =>
            entry.id ===
            updatedEntry.id
              ? updatedEntry
              : entry
        )
    );


    return true;
  }


  async function deleteEntry(
    entryId: number
  ): Promise<boolean> {
    const spaceId =
      getEntrySpaceId(entryId);

    if (spaceId === null) {
      return false;
    }

    const token = getToken();

    if (!token) {
      handleUnauthorized();
      return false;
    }

    clearNotices();


    const response = await fetch( 
      `${process.env.NEXT_PUBLIC_API_URL}/spaces/${spaceId}/entries/${entryId}`,
      {
        method: "DELETE",

        headers: {
          Authorization:
            `Bearer ${token}`,
        },
      }
    );


    if (
      response.status === 401
    ) {
      handleUnauthorized();
      return false;
    }


    if (
      response.status === 403
    ) {
      setError(
        "you can only delete your own entries."
      );

      return false;
    }


    if (!response.ok) {
      setError(
        "couldn't delete this entry."
      );

      return false;
    }


    setEntries(
      (currentEntries) =>
        currentEntries.filter(
          (entry) =>
            entry.id !== entryId
        )
    );

    setStreakRefreshKey(
      (current) => current + 1
    );

    return true;
  }
  async function addTag(
    entryId: number,
    name: string
  ): Promise<boolean> {
    const spaceId =
      getEntrySpaceId(entryId);

    if (spaceId === null) {
      return false;
    }

    const token = getToken();

    if (!token) {
      handleUnauthorized();
      return false;
    }

    clearNotices();

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/spaces/${spaceId}/entries/${entryId}/tags`,
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },

        body: JSON.stringify({
          name,
        }),
      }
    );

    if (response.status === 401) {
      handleUnauthorized();
      return false;
    }

    if (response.status === 409) {
      setError(
        "this tag is already attached."
      );
      return false;
    }

    if (response.status === 403) {
      setError(
        "you can only tag your own entries."
      );
      return false;
    }

    if (!response.ok) {
      setError(
        "couldn't add this tag."
      );
      return false;
    }

    const newTagLink =
      await response.json();

    setEntries(
      (currentEntries) =>
        currentEntries.map(
          (entry) =>
            entry.id === entryId
              ? {
                  ...entry,
                  tag_links: [
                    ...entry.tag_links,
                    newTagLink,
                  ],
                }
              : entry
        )
    );

    return true;
  }
  async function addAiTag(
    entryId: number,
    name: string
  ): Promise<boolean> {
    const spaceId =
      getEntrySpaceId(entryId);

    if (spaceId === null) {
      return false;
    }

    const token = getToken();

    if (!token) {
      handleUnauthorized();
      return false;
    }

    clearNotices();


    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/spaces/${spaceId}/entries/${entryId}/ai-tags`,
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },

        body: JSON.stringify({
          name,
        }),
      }
    );


    if (response.status === 401) {
      handleUnauthorized();
      return false;
    }


    if (response.status === 409) {
      setError(
        "this tag is already attached."
      );

      return false;
    }


    if (!response.ok) {
      setError(
        "couldn't add this AI tag."
      );

      return false;
    }


    const newTagLink =
      await response.json();


    setEntries(
      (currentEntries) =>
        currentEntries.map(
          (entry) =>
            entry.id === entryId
              ? {
                  ...entry,

                  tag_links: [
                    ...entry.tag_links,
                    newTagLink,
                  ],
                }
              : entry
        )
    );


    return true;
  }

  async function removeTag(
    entryId: number,
    tagId: number
  ): Promise<boolean> {
    const spaceId =
      getEntrySpaceId(entryId);

    if (spaceId === null) {
      return false;
    }

    const token = getToken();

    if (!token) {
      handleUnauthorized();
      return false;
    }

    clearNotices();

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/spaces/${spaceId}/entries/${entryId}/tags/${tagId}`,
      {
        method: "DELETE",

        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (response.status === 401) {
      handleUnauthorized();
      return false;
    }

    if (response.status === 403) {
      setError(
        "you can only modify tags on your own entries."
      );
      return false;
    }

    if (!response.ok) {
      setError(
        "couldn't remove this tag."
      );
      return false;
    }

    setEntries(
      (currentEntries) =>
        currentEntries.map(
          (entry) =>
            entry.id === entryId
              ? {
                  ...entry,
                  tag_links:
                    entry.tag_links.filter(
                      (link) =>
                        link.tag.id !==
                        tagId
                    ),
                }
              : entry
        )
    );

    return true;
  }
  async function deleteImage(
    entryId: number,
    imageId: number
  ): Promise<boolean> {
    const spaceId =
      getEntrySpaceId(entryId);

    if (spaceId === null) {
      return false;
    }


    const token =
      getToken();

    if (!token) {
      handleUnauthorized();
      return false;
    }


    clearNotices();


    const response =
      await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/spaces/${spaceId}/entries/${entryId}/images/${imageId}`,
        {
          method: "DELETE",

          headers: {
            Authorization:
              `Bearer ${token}`,
          },
        }
      );


    if (
      response.status ===
      401
    ) {
      handleUnauthorized();
      return false;
    }


    if (
      response.status ===
      403
    ) {
      setError(
        "you can only delete photos from your own entries."
      );

      return false;
    }


    if (!response.ok) {
      setError(
        "couldn't delete this photo."
      );

      return false;
    }


    // without refresh delete that photo
    setEntries(
      (currentEntries) =>
        currentEntries.map(
          (entry) => {
            if (
              entry.id !==
              entryId
            ) {
              return entry;
            }

            return {
              ...entry,

              images:
                entry.images.filter(
                  (image) =>
                    image.id !==
                    imageId
                ),
            };
          }
        )
    );


    return true;
  }
  async function suggestTags(
    entryId: number
  ): Promise<string[] | null> {
    const spaceId =
      getEntrySpaceId(entryId);

    if (spaceId === null) {
      return null;
    }

    const token = getToken();

    if (!token) {
      handleUnauthorized();
      return null;
    }

    clearNotices();

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/spaces/${spaceId}/entries/${entryId}/tag-suggestions`,
      {
        method: "POST",

        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (response.status === 401) {
      handleUnauthorized();
      return null;
    }

    if (!response.ok) {
      setError(
        "couldn't generate AI tag suggestions."
      );

      return null;
    }

    const data = await response.json();

    return data.tags;
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
    <main className="min-h-screen bg-transparent text-text">

      <div className="mx-auto max-w-2xl px-5 py-10 sm:px-6 sm:py-14">


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
                  {
                    currentUser.username
                  }
                </span>
              )}


              <button
                onClick={logout}
                className="text-xs text-text-muted hover:text-orange-dark"
              >
                log out
              </button>

            </div>

          </div>


          <SpaceControls
            spaces={spaces}

            selectedSpaceId={
              selectedSpaceId
            }

            onSelectSpace={
              setSelectedSpaceId
            }

            onCreateSpace={
              createSpace
            }

            onRenameSpace={
              renameSpace
            }

            onInviteMember={
              inviteMember
            }
          />
          {typeof selectedSpaceId === "number" && (
            <StreakCard
              spaceId={selectedSpaceId}
              refreshKey={streakRefreshKey}
            />
          )}

        </header>


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


        {!loading &&
          spaces.length === 0 && (
            <div className="mb-12 rounded-3xl border border-border bg-surface p-8 text-center">

              <p className="text-sm text-text-muted">
                No space yet..
              </p>

              <p className="mt-2 text-xs text-text-muted">
                Try clicking + new space..
              </p>

            </div>
          )}

        {selectedSpaceId !== null &&
          selectedSpaceId !== "all" && (
            <QuickCapture
        
            content={content}
            saving={saving}
            onContentChange={setContent}
            onSave={saveEntry}
          />
        )}

        <SearchControls
          query={searchQuery}
          tags={availableTags}
          selectedTag={selectedTag}
          onQueryChange={setSearchQuery}
          onTagChange={setSelectedTag}
        />
  
        {!loading &&
        entries.length > 0 &&
        filteredEntries.length === 0 ? (
          <div className="py-12 text-center">
            <p className="text-sm text-text-muted">
              no matches.
            </p>

            <p className="mt-1 text-xs text-text-muted">
              Try searching something else..
            </p>
          </div>
        ) : (
          <JournalFeed
            entries={filteredEntries}
            loading={loading}
            currentUserId={
              currentUser?.id ?? null
            }

            spaces={spaces}
            showSpaceName={
              selectedSpaceId === "all"
            }

            onEditEntry={editEntry}
            onDeleteEntry={deleteEntry}
            onDeleteImage={deleteImage}
            onAddTag={addTag}
            onAddAiTag={addAiTag}
            onRemoveTag={removeTag}
            onSuggestTags={suggestTags}
          />
        )}
      </div>
    </main>
  );
}