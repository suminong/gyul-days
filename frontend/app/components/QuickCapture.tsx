"use client";

import {
  ChangeEvent,
  FormEvent,
  KeyboardEvent,
  useRef,
} from "react";


type QuickCaptureProps = {
  content: string;
  saving: boolean;

  onContentChange: (
    value: string
  ) => void;

  onSave: () => Promise<void>;
};


export default function QuickCapture({
  content,
  saving,
  onContentChange,
  onSave,
}: QuickCaptureProps) {
  const textareaRef =
    useRef<HTMLTextAreaElement>(null);


  function resizeTextarea() {
    const textarea =
      textareaRef.current;

    if (!textarea) {
      return;
    }

    textarea.style.height = "auto";

    textarea.style.height =
      `${textarea.scrollHeight}px`;
  }


  function handleChange(
    event: ChangeEvent<HTMLTextAreaElement>
  ) {
    onContentChange(
      event.target.value
    );

    requestAnimationFrame(() => {
      resizeTextarea();
    });
  }


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    await onSave();

    if (textareaRef.current) {
      textareaRef.current.style.height =
        "auto";
    }
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

      onSave();
    }
  }


  return (
    <form
      onSubmit={handleSubmit}
      className="mb-14"
    >
      <div className="rounded-3xl border border-border bg-surface p-1 shadow-sm">

        <textarea
          ref={textareaRef}
          value={content}
          onChange={handleChange}
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
  );
}