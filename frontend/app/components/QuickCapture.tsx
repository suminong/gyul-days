"use client";

import {
  ChangeEvent,
  FormEvent,
  KeyboardEvent,
  useRef,
  useState,
} from "react";


type QuickCaptureProps = {
  content: string;
  saving: boolean;

  onContentChange: (
    value: string
  ) => void;

  onSave: (
    files: File[]
  ) => Promise<boolean>;
};


export default function QuickCapture({
  content,
  saving,
  onContentChange,
  onSave,
}: QuickCaptureProps) {
  const textareaRef =
    useRef<HTMLTextAreaElement>(null);

  const fileInputRef =
    useRef<HTMLInputElement>(null);

  const [
    selectedFiles,
    setSelectedFiles,
  ] = useState<File[]>([]);


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


  function handleChange(
    event:
      ChangeEvent<HTMLTextAreaElement>
  ) {
    onContentChange(
      event.target.value
    );

    requestAnimationFrame(() => {
      resizeTextarea();
    });
  }


  function handleFileChange(
    event:
      ChangeEvent<HTMLInputElement>
  ) {
    const files =
      Array.from(
        event.target.files ?? []
      );

    setSelectedFiles(files);
  }


  function removeFile(
    indexToRemove: number
  ) {
    setSelectedFiles(
      (currentFiles) =>
        currentFiles.filter(
          (_, index) =>
            index !==
            indexToRemove
        )
    );
  }


  function clearFiles() {
    setSelectedFiles([]);

    if (
      fileInputRef.current
    ) {
      fileInputRef.current.value =
        "";
    }
  }


  async function save() {
    const success =
      await onSave(
        selectedFiles
      );

    if (!success) {
      return;
    }

    clearFiles();

    if (
      textareaRef.current
    ) {
      textareaRef.current.style.height =
        "auto";
    }
  }


  async function handleSubmit(
    event:
      FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    await save();
  }


  function handleKeyDown(
    event:
      KeyboardEvent<HTMLTextAreaElement>
  ) {
    if (
      (
        event.metaKey ||
        event.ctrlKey
      ) &&
      event.key === "Enter"
    ) {
      event.preventDefault();

      save();
    }
  }


  return (
    <form
      onSubmit={handleSubmit}
      className="mb-14"
    >

      <div className="rounded-3xl border border-border bg-surface p-2 shadow-sm backdrop-blur-sm">

        <textarea
          ref={textareaRef}
          value={content}
          onChange={handleChange}
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


        {/* Selected photos */}
        {selectedFiles.length >
          0 && (
          <div className="px-4 pb-3">

            <div className="flex flex-wrap gap-2">

              {selectedFiles.map(
                (
                  file,
                  index
                ) => (
                  <div
                    key={`${file.name}-${index}`}
                    className="
                      flex
                      max-w-full
                      items-center
                      gap-2
                      rounded-full
                      border
                      border-orange-light
                      bg-background
                      px-3
                      py-1.5
                    "
                  >

                    <span className="max-w-[180px] truncate text-xs text-text-muted">
                      📷 {file.name}
                    </span>


                    <button
                      type="button"
                      onClick={() =>
                        removeFile(
                          index
                        )
                      }
                      className="text-xs text-text-muted transition hover:text-orange-dark"
                    >
                      ×
                    </button>

                  </div>
                )
              )}

            </div>

          </div>
        )}


        <div className="flex items-center justify-between px-4 pb-3">

          <div className="flex items-center gap-4">

            {/* Hidden real file input */}
            <input
              ref={
                fileInputRef
              }
              type="file"
              accept="
                image/jpeg,
                image/png,
                image/webp
              "
              multiple
              onChange={
                handleFileChange
              }
              className="hidden"
            />


            {/* Pretty photo button */}
            <button
              type="button"
              onClick={() =>
                fileInputRef.current?.click()
              }
              className="
                text-xs
                font-medium
                text-orange-dark
                transition
                hover:text-orange
              "
            >
              + photo
            </button>


            <span className="hidden text-xs text-text-muted sm:inline">
              ⌘ + enter to save
            </span>

          </div>


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