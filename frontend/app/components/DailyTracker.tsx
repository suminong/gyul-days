"use client";

import {
  useEffect,
  useState,
} from "react";


function getLocalDateString() {
  const now = new Date();

  const year = now.getFullYear();

  const month = String(
    now.getMonth() + 1
  ).padStart(2, "0");

  const day = String(
    now.getDate()
  ).padStart(2, "0");

  return `${year}-${month}-${day}`;
}


type ScoreButtonProps = {
  label: string;
  value: number;
  onChange: (
    value: number
  ) => void;
};


function ScoreButtons({
  label,
  value,
  onChange,
}: ScoreButtonProps) {
  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <span className="text-sm text-text">
          {label}
        </span>

        <span className="text-xs text-text-muted">
          {value}/5
        </span>
      </div>

      <div className="flex gap-2">
        {[1, 2, 3, 4, 5].map(
          (score) => (
            <button
              key={score}
              type="button"
              onClick={() =>
                onChange(score)
              }
              className={`
                flex
                h-8
                w-8
                items-center
                justify-center
                rounded-full
                text-xs
                transition

                ${
                  score === value
                    ? "bg-orange text-white"
                    : "border border-border bg-surface text-text-muted hover:border-orange-light"
                }
              `}
            >
              {score}
            </button>
          )
        )}
      </div>
    </div>
  );
}


export default function DailyTracker() {
  const today =
    getLocalDateString();

  const [
    sleepSessionId,
    setSleepSessionId,
  ] = useState<number | null>(null);

  const [
    sleepStart,
    setSleepStart,
  ] = useState("");

  const [
    sleepEnd,
    setSleepEnd,
  ] = useState("");

  const [
    energy,
    setEnergy,
  ] = useState(3);

  const [
    focus,
    setFocus,
  ] = useState(3);

  const [
    mood,
    setMood,
  ] = useState(3);

  const [
    stress,
    setStress,
  ] = useState(3);

  const [
    overallCondition,
    setOverallCondition,
  ] = useState(3);

  const [
    note,
    setNote,
  ] = useState("");

  const [
    sleepSaving,
    setSleepSaving,
  ] = useState(false);

  const [
    checkInSaving,
    setCheckInSaving,
  ] = useState(false);

  const [
    message,
    setMessage,
  ] = useState("");

  const [
    error,
    setError,
  ] = useState("");


  function getToken() {
    return localStorage.getItem(
      "access_token"
    );
  }


  useEffect(() => {
		async function loadToday() {
			const token =
				getToken();

			if (!token) {
				return;
			}

			// -------------------------
			// Load today's check-in
			// -------------------------

			const checkInResponse =
				await fetch(
					`${process.env.NEXT_PUBLIC_API_URL}/me/check-in/${today}`,
					{
						headers: {
							Authorization:
								`Bearer ${token}`,
						},
					}
				);

			if (checkInResponse.ok) {
				const data =
					await checkInResponse.json();

				setEnergy(
					data.energy
				);

				setFocus(
					data.focus
				);

				setMood(
					data.mood
				);

				setStress(
					data.stress
				);

				setOverallCondition(
					data.overall_condition
				);

				setNote(
					data.note ?? ""
				);
			}


			// -------------------------
			// Load sleep sessions
			// -------------------------

			const sleepResponse =
				await fetch(
					`${process.env.NEXT_PUBLIC_API_URL}/me/sleep`,
					{
						headers: {
							Authorization:
								`Bearer ${token}`,
						},
					}
				);

			if (!sleepResponse.ok) {
				return;
			}

			const sleepSessions =
				await sleepResponse.json();


			// 오늘 아침에 끝난
			// main sleep 찾기
			const todayDate =
				new Date();

			const todaySleep =
				sleepSessions.find(
					(
						session: {
							id: number;
							start_at: string;
							end_at: string;
							session_type: string;
						}
					) => {
						if (
							session.session_type
							!== "main_sleep"
						) {
							return false;
						}

						const end =
							new Date(
								session.end_at
							);

						return (
							end.getFullYear()
								=== todayDate.getFullYear()
							&&
							end.getMonth()
								=== todayDate.getMonth()
							&&
							end.getDate()
								=== todayDate.getDate()
						);
					}
				);


			if (!todaySleep) {
				return;
			}


			setSleepSessionId(
				todaySleep.id
			);


			function toLocalInputValue(
				isoString: string
			) {
				const date =
					new Date(
						isoString
					);

				const year =
					date.getFullYear();

				const month =
					String(
						date.getMonth() + 1
					).padStart(
						2,
						"0"
					);

				const day =
					String(
						date.getDate()
					).padStart(
						2,
						"0"
					);

				const hours =
					String(
						date.getHours()
					).padStart(
						2,
						"0"
					);

				const minutes =
					String(
						date.getMinutes()
					).padStart(
						2,
						"0"
					);

				return (
					`${year}-${month}-${day}` +
					`T${hours}:${minutes}`
				);
			}


			setSleepStart(
				toLocalInputValue(
					todaySleep.start_at
				)
			);

			setSleepEnd(
				toLocalInputValue(
					todaySleep.end_at
				)
			);
		}


		loadToday();

	}, [today]);


  async function saveSleep() {
      console.log("saveSleep clicked", {
      sleepStart,
      sleepEnd,
      sleepSessionId,
    });
    if (
      !sleepStart ||
      !sleepEnd
    ) {
      setError(
        "잠든 시간과 일어난 시간을 모두 입력해줘."
      );

      return;
    }

    const start =
      new Date(
        sleepStart
      );

    const end =
      new Date(
        sleepEnd
      );

    if (
      end <= start
    ) {
      setError(
        "일어난 시간은 잠든 시간보다 뒤여야 해."
      );

      return;
    }

    const token =
      getToken();

    if (!token) {
      setError(
        "로그인이 필요해."
      );

      return;
    }

    setSleepSaving(true);
    setError("");
    setMessage("");

    try {
      const sleepUrl =
  sleepSessionId === null
    ? `${process.env.NEXT_PUBLIC_API_URL}/me/sleep`
    : `${process.env.NEXT_PUBLIC_API_URL}/me/sleep/${sleepSessionId}`;

console.log("Sending sleep request", {
  method: sleepSessionId === null ? "POST" : "PUT",
  sleepUrl,
});

const response =
  await fetch(
    sleepUrl,
    {
      method:
        sleepSessionId === null
          ? "POST"
          : "PUT",

      headers: {
        "Content-Type":
          "application/json",

        Authorization:
          `Bearer ${token}`,
      },

      body: JSON.stringify({
        start_at:
          start.toISOString(),

        end_at:
          end.toISOString(),

        session_type:
          "main_sleep",

        source:
          "manual",
      }),
    }
  );


if (!response.ok) {
  throw new Error();
}


const savedSleep =
  await response.json();


setSleepSessionId(
  savedSleep.id
);


setMessage(
  sleepSessionId === null
    ? "수면 기록을 저장했어."
    : "수면 기록을 수정했어."
);

      if (!response.ok) {
        throw new Error();
      }

      setMessage(
        "수면 기록을 저장했어."
      );

    } catch (error) {
      console.error("Sleep save error:", error);

      setError(
        "수면 기록을 저장하지 못했어."
      );
    } finally {
      setSleepSaving(false);
    }
  }


  async function saveCheckIn() {
    const token =
      getToken();

    if (!token) {
      setError(
        "로그인이 필요해."
      );

      return;
    }

    setCheckInSaving(true);
    setError("");
    setMessage("");

    try {
      const response =
        await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/me/check-in/${today}`,
          {
            method: "PUT",

            headers: {
              "Content-Type":
                "application/json",

              Authorization:
                `Bearer ${token}`,
            },

            body: JSON.stringify({
              energy,
              focus,
              mood,
              stress,

              overall_condition:
                overallCondition,

              note:
                note.trim()
                || null,
            }),
          }
        );

      if (!response.ok) {
        throw new Error();
      }

      setMessage(
        "오늘 컨디션을 저장했어."
      );

    } catch {
      setError(
        "오늘 컨디션을 저장하지 못했어."
      );

    } finally {
      setCheckInSaving(false);
    }
  }


  return (
    <section
      className="
        mb-10
        rounded-3xl
        border
        border-border
        bg-surface
        p-5
        shadow-sm
      "
    >
      <div className="mb-6">
        <p className="text-xs text-text-muted">
          today · {today}
        </p>

        <h2 className="mt-1 text-lg font-medium text-orange-dark">
          오늘의 리듬
        </h2>
      </div>


      {/* SLEEP */}

      <div className="mb-8">
        <p className="mb-3 text-sm font-medium text-text">
          어젯밤 수면
        </p>

        <div className="grid gap-3 sm:grid-cols-2">
          <label className="text-xs text-text-muted">
            잠든 시간

            <input
              type="datetime-local"
              value={sleepStart}
              onChange={(event) =>
                setSleepStart(
                  event.target.value
                )
              }
              className="
                mt-1
                w-full
                rounded-2xl
                border
                border-border
                bg-transparent
                px-3
                py-2
                text-sm
                text-text
                outline-none
                focus:border-orange-light
              "
            />
          </label>

          <label className="text-xs text-text-muted">
            일어난 시간

            <input
              type="datetime-local"
              value={sleepEnd}
              onChange={(event) =>
                setSleepEnd(
                  event.target.value
                )
              }
              className="
                mt-1
                w-full
                rounded-2xl
                border
                border-border
                bg-transparent
                px-3
                py-2
                text-sm
                text-text
                outline-none
                focus:border-orange-light
              "
            />
          </label>
        </div>

        <button
          type="button"
          onClick={saveSleep}
          disabled={sleepSaving}
          className="
            mt-3
            rounded-full
            border
            border-orange-light
            px-4
            py-2
            text-xs
            text-orange-dark
            transition
            hover:bg-orange-light/20
            disabled:opacity-40
          "
        >
          {sleepSaving
            ? "saving..."
            : "save sleep"}
        </button>
      </div>


      {/* CHECK IN */}

      <div className="border-t border-border pt-6">
        <p className="mb-5 text-sm font-medium text-text">
          오늘 컨디션
        </p>

        <div className="grid gap-5 sm:grid-cols-2">
          <ScoreButtons
            label="energy"
            value={energy}
            onChange={setEnergy}
          />

          <ScoreButtons
            label="focus"
            value={focus}
            onChange={setFocus}
          />

          <ScoreButtons
            label="mood"
            value={mood}
            onChange={setMood}
          />

          <ScoreButtons
            label="stress"
            value={stress}
            onChange={setStress}
          />
        </div>

        <div className="mt-6">
          <ScoreButtons
            label="overall"
            value={
              overallCondition
            }
            onChange={
              setOverallCondition
            }
          />
        </div>

        <textarea
          value={note}
          onChange={(event) =>
            setNote(
              event.target.value
            )
          }
          placeholder="오늘 몸이나 집중 상태에 대해 짧게 기록..."
          rows={2}
          className="
            mt-6
            w-full
            resize-none
            rounded-2xl
            border
            border-border
            bg-transparent
            px-4
            py-3
            text-sm
            leading-6
            text-text
            outline-none
            placeholder:text-text-muted
            focus:border-orange-light
          "
        />

        <button
          type="button"
          onClick={
            saveCheckIn
          }
          disabled={
            checkInSaving
          }
          className="
            mt-3
            rounded-full
            bg-orange
            px-5
            py-2
            text-xs
            text-white
            transition
            hover:opacity-90
            disabled:opacity-40
          "
        >
          {checkInSaving
            ? "saving..."
            : "save condition"}
        </button>
      </div>


      {message && (
        <p className="mt-4 text-xs text-green-dark">
          {message}
        </p>
      )}

      {error && (
        <p className="mt-4 text-xs text-orange-dark">
          {error}
        </p>
      )}
    </section>
  );
}