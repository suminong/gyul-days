"use client";

import { useEffect, useState } from "react";
import type { StreakResponse } from "../types";

type StreakCardProps = {
  spaceId: number | null;
  refreshKey?: number;
};


function StageVisual({
  stage,
  currentStreak,
}: {
  stage: StreakResponse["stage"];
  currentStreak: number;
}) {
  const sproutProgress =
    Math.min(currentStreak / 7, 1);
  if (stage === "none") {
    return (
      <div className="flex h-20 w-24 items-center justify-center">
        <svg
          viewBox="0 0 96 80"
          className="h-16 w-20"
          fill="none"
          aria-hidden="true"
        >
          <path
            d="M48 68 C46 56 46 42 49 30"
            stroke="var(--green-dark)"
            strokeWidth="2"
            strokeLinecap="round"
          />

          <path
            d="M48 45
               C36 45 29 38 28 29
               C39 28 47 33 50 41"
            fill="var(--green-light)"
            stroke="var(--green)"
            strokeWidth="1.4"
          />

          <path
            d="M49 36
               C52 25 61 20 71 22
               C69 33 61 39 50 40"
            fill="var(--green-light)"
            stroke="var(--green)"
            strokeWidth="1.4"
          />

          <path
            d="M49 29
               C45 23 46 17 50 13
               C56 19 55 25 49 29"
            fill="var(--green)"
            opacity="0.75"
          />

          <ellipse
            cx="48"
            cy="70"
            rx="15"
            ry="2.5"
            fill="var(--orange-light)"
            opacity="0.2"
          />
        </svg>
      </div>
    );
  }

  if (stage === "orange") {
    const fruitProgress =
      Math.min(
        Math.max(
          (currentStreak - 7) / 6,
          0
        ),
        1
      );

    const fruitScale =
      0.68 + fruitProgress * 0.32;

    return (
      <div
        className="
          flex
          h-20
          w-24
          items-center
          justify-center
        "
        aria-hidden="true"
      >
        <svg
          viewBox="0 0 96 80"
          className="h-16 w-20"
          fill="none"
        >
          {/* soft shadow */}
          <ellipse
            cx="48"
            cy="69"
            rx={14 + fruitProgress * 5}
            ry="3"
            fill="var(--orange-dark)"
            opacity="0.08"
          />

          {/* fruit */}
          <g
            style={{
              transform: `scale(${fruitScale})`,
              transformOrigin: "48px 47px",
              transition:
                "transform 700ms ease",
            }}
          >
            {/* young green fruit */}
            <circle
              cx="48"
              cy="46"
              r="22"
              fill="var(--green)"
            />

            {/* orange gradually appears */}
            <circle
              cx="48"
              cy="46"
              r="22"
              fill="var(--orange)"
              style={{
                opacity: fruitProgress,
                transition:
                  "opacity 700ms ease",
              }}
            />

            {/* soft highlight */}
            <ellipse
              cx="41"
              cy="38"
              rx="6"
              ry="8"
              fill="white"
              opacity={
                0.05 +
                fruitProgress * 0.08
              }
            />
          </g>

          {/* stem */}
          <path
            d="
              M48 25
              C49 20 51 17 54 14
            "
            stroke="var(--green-dark)"
            strokeWidth="2"
            strokeLinecap="round"
          />

          {/* leaf */}
          <path
            d="
              M52 20
              C59 14 67 15 71 20
              C64 23 58 23 52 20
            "
            fill="var(--green-light)"
            stroke="var(--green)"
            strokeWidth="1.3"
          />
        </svg>
      </div>
    );
  }

  if (stage === "two_oranges") {
    const secondFruitProgress =
      Math.min(
        Math.max(
          (currentStreak - 14) / 15,
          0
        ),
        1
      );

    const secondFruitScale =
      0.45 + secondFruitProgress * 0.55;

    return (
      <div
        className="
          flex
          h-20
          w-24
          items-center
          justify-center
        "
        aria-hidden="true"
      >
        <svg
          viewBox="0 0 96 80"
          className="h-16 w-20"
          fill="none"
        >
          {/* soft shadow */}
          <ellipse
            cx="49"
            cy="70"
            rx="27"
            ry="3"
            fill="var(--orange-dark)"
            opacity="0.08"
          />

          {/* first mature orange */}
          <g>
            <circle
              cx="38"
              cy="48"
              r="19"
              fill="var(--orange)"
            />

            <ellipse
              cx="33"
              cy="42"
              rx="5"
              ry="7"
              fill="white"
              opacity="0.1"
            />

            <path
              d="
                M38 29
                C39 25 41 22 44 20
              "
              stroke="var(--green-dark)"
              strokeWidth="1.8"
              strokeLinecap="round"
            />

            <path
              d="
                M42 23
                C48 18 54 19 58 23
                C52 26 47 26 42 23
              "
              fill="var(--green-light)"
              stroke="var(--green)"
              strokeWidth="1.2"
            />
          </g>

          {/* second growing orange */}
          <g
            style={{
              transform: `scale(${secondFruitScale})`,
              transformOrigin: "60px 43px",
              transition:
                "transform 700ms ease",
            }}
          >
            {/* young green base */}
            <circle
              cx="60"
              cy="43"
              r="20"
              fill="var(--green)"
            />

            {/* orange ripening layer */}
            <circle
              cx="60"
              cy="43"
              r="20"
              fill="var(--orange)"
              style={{
                opacity:
                  secondFruitProgress,
                transition:
                  "opacity 700ms ease",
              }}
            />

            <ellipse
              cx="54"
              cy="36"
              rx="5"
              ry="7"
              fill="white"
              opacity={
                0.05 +
                secondFruitProgress * 0.08
              }
            />
          </g>

          {/* second stem */}
          <path
            d="
              M60 23
              C61 19 63 16 66 14
            "
            stroke="var(--green-dark)"
            strokeWidth="1.8"
            strokeLinecap="round"
          />

          <path
            d="
              M64 17
              C70 13 76 14 80 18
              C74 21 69 21 64 17
            "
            fill="var(--green-light)"
            stroke="var(--green)"
            strokeWidth="1.2"
          />
        </svg>
      </div>
    );
  }

  if (stage === "box") {
    const boxProgress =
      Math.min(
        Math.max(
          (currentStreak - 30) / 29,
          0
        ),
        1
      );

    const visibleOrangeCount =
      3 + Math.floor(
        boxProgress * 5
      );

    const oranges = [
      { cx: 28, cy: 38, r: 10 },
      { cx: 42, cy: 32, r: 11 },
      { cx: 57, cy: 34, r: 11 },
      { cx: 70, cy: 40, r: 10 },
      { cx: 35, cy: 48, r: 11 },
      { cx: 50, cy: 46, r: 11 },
      { cx: 64, cy: 49, r: 11 },
      { cx: 49, cy: 24, r: 10 },
    ];

    return (
      <div
        className="
          flex
          h-20
          w-24
          items-center
          justify-center
        "
        aria-hidden="true"
      >
        <svg
          viewBox="0 0 96 80"
          className="h-20 w-24"
          fill="none"
        >
          {/* soft ground shadow */}
          <ellipse
            cx="49"
            cy="72"
            rx="31"
            ry="3"
            fill="var(--orange-dark)"
            opacity="0.08"
          />

          {/* oranges */}
          {oranges.map(
            (orange, index) => {
              if (
                index >=
                visibleOrangeCount
              ) {
                return null;
              }

              return (
                <g
                  key={index}
                  style={{
                    transformOrigin:
                      `${orange.cx}px ${orange.cy}px`,
                    animation:
                      "gyul-pop 500ms ease-out",
                  }}
                >
                  <circle
                    cx={orange.cx}
                    cy={orange.cy}
                    r={orange.r}
                    fill="var(--orange)"
                  />

                  <ellipse
                    cx={
                      orange.cx - 3
                    }
                    cy={
                      orange.cy - 3
                    }
                    rx="2.5"
                    ry="3.5"
                    fill="white"
                    opacity="0.09"
                  />
                </g>
              );
            }
          )}

          {/* box */}
          <path
            d="
              M18 45
              L78 45
              L72 69
              Q48 74 24 69
              Z
            "
            fill="var(--orange-light)"
            fillOpacity="0.58"
            stroke="var(--orange-dark)"
            strokeOpacity="0.4"
            strokeWidth="1.5"
          />

          {/* box slats */}
          <path
            d="M27 53 L69 53"
            stroke="var(--orange-dark)"
            strokeOpacity="0.2"
            strokeWidth="1.2"
          />

          <path
            d="M29 62 L67 62"
            stroke="var(--orange-dark)"
            strokeOpacity="0.18"
            strokeWidth="1.2"
          />
        </svg>
      </div>
    );
  }

  const treeProgress =
    Math.min(
      Math.max(
        (currentStreak - 60) / 30,
        0
      ),
      1
    );

  const visibleFruitCount =
    3 + Math.floor(
      treeProgress * 5
    );

  const fruits = [
    { cx: 33, cy: 30, r: 6 },
    { cx: 58, cy: 24, r: 6 },
    { cx: 68, cy: 39, r: 6 },
    { cx: 28, cy: 45, r: 6 },
    { cx: 49, cy: 43, r: 7 },
    { cx: 41, cy: 18, r: 5 },
    { cx: 62, cy: 52, r: 6 },
    { cx: 76, cy: 28, r: 5 },
  ];

  return (
    <div
      className="
        flex
        h-24
        w-28
        items-center
        justify-center
      "
      aria-hidden="true"
    >
      <svg
        viewBox="0 0 104 90"
        className="h-24 w-28"
        fill="none"
      >
        {/* ground shadow */}
        <ellipse
          cx="52"
          cy="83"
          rx={22 + treeProgress * 8}
          ry="3"
          fill="var(--orange-dark)"
          opacity="0.08"
        />

        {/* trunk */}
        <path
          d="
            M51 80
            C50 67 49 55 52 38
          "
          stroke="var(--green-dark)"
          strokeWidth="4"
          strokeLinecap="round"
        />

        {/* branches */}
        <path
          d="M51 56 C43 49 38 43 34 36"
          stroke="var(--green-dark)"
          strokeWidth="2"
          strokeLinecap="round"
          opacity="0.8"
        />

        <path
          d="M52 51 C60 44 65 38 68 31"
          stroke="var(--green-dark)"
          strokeWidth="2"
          strokeLinecap="round"
          opacity="0.8"
        />

        {/* canopy */}
        <circle
          cx="38"
          cy="35"
          r={16 + treeProgress * 3}
          fill="var(--green-light)"
          opacity="0.88"
        />

        <circle
          cx="57"
          cy="28"
          r={18 + treeProgress * 4}
          fill="var(--green-light)"
        />

        <circle
          cx="70"
          cy="42"
          r={14 + treeProgress * 3}
          fill="var(--green-light)"
          opacity="0.9"
        />

        <circle
          cx="31"
          cy="49"
          r={12 + treeProgress * 2}
          fill="var(--green-light)"
          opacity="0.84"
        />

        <circle
          cx="52"
          cy="49"
          r={15 + treeProgress * 2}
          fill="var(--green-light)"
          opacity="0.92"
        />

        {/* oranges */}
        {fruits.map(
          (fruit, index) => {
            if (
              index >=
              visibleFruitCount
            ) {
              return null;
            }

            return (
              <g
                key={index}
                style={{
                  transformOrigin:
                    `${fruit.cx}px ${fruit.cy}px`,
                  animation:
                    "gyul-pop 500ms ease-out",
                }}
              >
                <circle
                  cx={fruit.cx}
                  cy={fruit.cy}
                  r={fruit.r}
                  fill="var(--orange)"
                />

                <ellipse
                  cx={fruit.cx - 2}
                  cy={fruit.cy - 2}
                  rx="1.5"
                  ry="2"
                  fill="white"
                  opacity="0.11"
                />
              </g>
            );
          }
        )}

        {/* small leaves appearing later */}
        <g
          style={{
            opacity: treeProgress,
            transition:
              "opacity 700ms ease",
          }}
        >
          <path
            d="
              M29 25
              C22 21 18 23 16 27
              C21 30 26 29 29 25
            "
            fill="var(--green)"
            opacity="0.7"
          />

          <path
            d="
              M76 49
              C84 46 89 49 90 54
              C84 56 79 54 76 49
            "
            fill="var(--green)"
            opacity="0.7"
          />
        </g>
      </svg>
    </div>
  );
}

function getStageMessage(
  streak: StreakResponse
) {
  if (streak.stage === "tree") {
    return "your gyul tree is growing";
  }

  if (streak.next_milestone === null) {
    return "keep growing";
  }

  const daysLeft =
    streak.next_milestone -
    streak.current_streak;

  if (streak.stage === "none") {
    return `${daysLeft} more ${
      daysLeft === 1 ? "day" : "days"
    } until your first gyul`;
  }

  return `${daysLeft} more ${
    daysLeft === 1 ? "day" : "days"
  } until the next milestone`;
}

function getStageProgress(
  streak: StreakResponse
) {
  const current =
    streak.current_streak;

  if (current >= 60) {
    return 100;
  }

  if (current >= 30) {
    return (
      ((current - 30) / 30) * 100
    );
  }

  if (current >= 14) {
    return (
      ((current - 14) / 16) * 100
    );
  }

  if (current >= 7) {
    return (
      ((current - 7) / 7) * 100
    );
  }

  return (
    (current / 7) * 100
  );
}

export default function StreakCard({
  spaceId,
  refreshKey = 0,
}: StreakCardProps) {
  const [streak, setStreak] =
    useState<StreakResponse | null>(
      null
    );

  const [loading, setLoading] =
    useState(false);

  useEffect(() => {
    if (spaceId === null) {
      setStreak(null);
      return;
    }

    async function loadStreak() {
      const token =
        localStorage.getItem(
          "access_token"
        );

      if (!token) {
        return;
      }

      setLoading(true);

      try {
        const timezone =
          Intl.DateTimeFormat()
            .resolvedOptions()
            .timeZone;

        const response = await fetch(
          `${
            process.env.NEXT_PUBLIC_API_URL
          }/spaces/${spaceId}/streak?timezone_name=${encodeURIComponent(
            timezone
          )}`,
          {
            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error(
            "Could not load streak"
          );
        }

        const data:
          StreakResponse =
          await response.json();

        setStreak(data);
      } catch (error) {
        console.error(
          "Streak error:",
          error
        );
      } finally {
        setLoading(false);
      }
    }

    loadStreak();
  }, [spaceId, refreshKey]);

  if (
    spaceId === null ||
    loading ||
    streak === null
  ) {
    return null;
  }
  const progress = getStageProgress(streak);

  return (
    <section
      className="
        mt-4  
        rounded-3xl
        border
        border-orange-light/50
        bg-surface/70
        px-5
        py-4
        shadow-sm
        backdrop-blur-sm
      "
    >
      <div
        className="
          flex
          items-center
          justify-between
          gap-4
        "
      >
        <div>
          <p
            className="
              text-xs
              uppercase
              tracking-[0.16em]
              text-text-muted
            "
          >
            gyul streak
          </p>

          <p
            className="
              mt-1
              text-lg
              font-semibold
              text-orange-dark
            "
          >
            {streak.current_streak}
            {" "}
            {streak.current_streak === 1
              ? "day"
              : "days"}
          </p>

          <p
            className="
              mt-1
              text-sm
              text-text-muted
            "
          >
            {getStageMessage(
              streak
            )}
          </p>

          <div className="mt-4">
            <div
              className="
                h-2
                overflow-hidden
                rounded-full
                bg-orange-light/30
              "
            >
              <div
                className="
                  h-full
                  rounded-full
                  bg-orange
                  transition-all
   ㄴ               duration-500
                "
                style={{
                  width: `${Math.min(
                    progress,
                    100
                  )}%`,
                }}
              />
            </div>

            {streak.next_milestone !== null && (
              <p
                className="
                  mt-2
                  text-[11px]
                  text-text-muted
                "
              >
                {streak.current_streak}
                {" / "}
                {streak.next_milestone}
                {" days"}
              </p>
            )}
          </div>
        </div>
        <div
          className="
            flex
            min-w-24
            items-center
            justify-center
          "
          aria-hidden="true"
        >
          <StageVisual
            stage={streak.stage}
            currentStreak={streak.current_streak}
          />
        </div>
      </div>

      <div
        className="
          mt-4
          flex
          gap-4
          border-t
          border-border/60
          pt-3
          text-xs
          text-text-muted
        "
      >
        <span>
          longest{" "}
          <strong
            className="
              text-orange-dark
            "
          >
            {streak.longest_streak}
          </strong>
        </span>

        <span>
          recorded{" "}
          <strong
            className="
              text-orange-dark
            "
          >
            {
              streak.total_recorded_days
            }
          </strong>{" "}
          days
        </span>
      </div>
    </section>
  );
}