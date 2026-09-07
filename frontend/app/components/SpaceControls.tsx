"use client";

import {
  ChangeEvent,
  FormEvent,
  useState,
} from "react";

import { Space } from "../types";


type SpaceControlsProps = {
  spaces: Space[];

  selectedSpaceId:
    number | null;

  onSelectSpace: (
    spaceId: number
  ) => void;

  onCreateSpace: (
    name: string
  ) => Promise<boolean>;

  onRenameSpace: (
    name: string
  ) => Promise<boolean>;

  onInviteMember: (
    username: string
  ) => Promise<boolean>;
};


export default function SpaceControls({
  spaces,
  selectedSpaceId,
  onSelectSpace,
  onCreateSpace,
  onRenameSpace,
  onInviteMember,
}: SpaceControlsProps) {
  const [
    mode,
    setMode,
  ] = useState<
    | "none"
    | "create"
    | "rename"
    | "invite"
  >("none");


  const [
    value,
    setValue,
  ] = useState("");

  const [
    submitting,
    setSubmitting,
  ] = useState(false);


  const selectedSpace =
    spaces.find(
      (space) =>
        space.id ===
        selectedSpaceId
    );


  function closeTool() {
    setMode("none");
    setValue("");
  }


  function handleSpaceChange(
    event:
      ChangeEvent<HTMLSelectElement>
  ) {
    onSelectSpace(
      Number(
        event.target.value
      )
    );
  }


  function startCreate() {
    setValue("");
    setMode("create");
  }


  function startRename() {
    if (!selectedSpace) {
      return;
    }

    setValue(
      selectedSpace.name
    );

    setMode("rename");
  }


  function startInvite() {
    setValue("");
    setMode("invite");
  }


  async function handleSubmit(
    event:
      FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (!value.trim()) {
      return;
    }

    setSubmitting(true);

    let success = false;


    if (mode === "create") {
      success =
        await onCreateSpace(
          value.trim()
        );
    }


    if (mode === "rename") {
      success =
        await onRenameSpace(
          value.trim()
        );
    }


    if (mode === "invite") {
      success =
        await onInviteMember(
          value.trim()
        );
    }


    setSubmitting(false);

    if (success) {
      closeTool();
    }
  }


  return (
    <div>

      <div className="mb-2 flex items-center justify-between">

        <p className="text-[11px] font-medium uppercase tracking-[0.15em] text-text-muted">
          space
        </p>

        <button
          type="button"
          onClick={startCreate}
          className="text-xs font-medium text-orange-dark transition hover:text-orange"
        >
          + new space
        </button>

      </div>


      {spaces.length > 0 &&
        mode === "none" && (
          <div className="flex gap-2">

            <div className="relative min-w-0 flex-1">
              <select
                value={
                  selectedSpaceId ??
                  ""
                }
                onChange={
                  handleSpaceChange
                }
                className="
                  w-full
                  appearance-none
                  rounded-2xl
                  border
                  border-border
                  bg-surface
                  py-3
                  pl-4
                  pr-12
                  text-sm
                  font-medium
                  text-orange-dark
                  outline-none
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

              <span
                className="
                  pointer-events-none
                  absolute
                  right-6
                  top-1/2
                  -translate-y-1/2
                  text-xl
                  text-orange-dark
                "
              >
                ▾
              </span>
            </div> 


            <button
              type="button"
              onClick={
                startRename
              }
              className="rounded-2xl border border-border bg-surface px-4 text-sm text-text-muted hover:text-orange-dark"
            >
              edit
            </button>


            <button
              type="button"
              onClick={
                startInvite
              }
              className="rounded-2xl border border-border bg-surface px-4 text-sm text-text-muted hover:text-orange-dark"
            >
              invite
            </button>

          </div>
        )}


      {mode !== "none" && (
        <form
          onSubmit={
            handleSubmit
          }
          className="rounded-3xl border border-border bg-surface p-4"
        >

          <p className="mb-3 text-sm font-medium text-orange-dark">

            {mode === "create" &&
              "새 Space 만들기"}

            {mode === "rename" &&
              "Space 이름 바꾸기"}

            {mode === "invite" &&
              "친구 추가하기"}

          </p>


          {mode === "invite" && (
            <p className="mb-3 text-xs text-text-muted">
              친구의 Gyul Days
              username을 입력해.
            </p>
          )}


          <div className="flex gap-2">

            <input
              value={value}
              onChange={(
                event
              ) =>
                setValue(
                  event.target
                    .value
                )
              }
              placeholder={
                mode === "invite"
                  ? "username"
                  : "space name"
              }
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
                outline-none
                focus:border-orange
              "
            />


            <button
              type="submit"
              disabled={
                submitting ||
                !value.trim()
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
              {submitting
                ? "..."
                : mode ===
                    "invite"
                  ? "add"
                  : mode ===
                      "create"
                    ? "create"
                    : "save"}
            </button>


            <button
              type="button"
              onClick={
                closeTool
              }
              className="rounded-2xl border border-border px-4 text-sm text-text-muted"
            >
              cancel
            </button>

          </div>

        </form>
      )}

    </div>
  );
}