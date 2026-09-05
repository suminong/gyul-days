"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function SignupPage() {
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/users`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            username,
            email,
            password,
          }),
        }
      );

      if (!response.ok) {
        const data = await response.json();

        throw new Error(
          data.detail || "couldn't create your account."
        );
      }

      router.push("/login");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-background text-text">
      <div className="mx-auto flex min-h-screen max-w-md items-center px-6">

        <div className="w-full">
          <div className="mb-10">
            <h1 className="text-3xl font-semibold tracking-tight text-orange-dark">
              gyul days
            </h1>

            <p className="mt-2 text-sm text-text-muted">
              start keeping the little things.
            </p>
          </div>

          <form
            onSubmit={handleSubmit}
            className="space-y-4"
          >
            <input
              value={username}
              onChange={(event) =>
                setUsername(event.target.value)
              }
              placeholder="username"
              required
              minLength={3}
              className="
                w-full rounded-2xl border border-border
                bg-surface px-4 py-3 text-text
                outline-none transition
                placeholder:text-text-muted
                focus:border-orange
              "
            />

            <input
              type="email"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              placeholder="email"
              required
              className="
                w-full rounded-2xl border border-border
                bg-surface px-4 py-3 text-text
                outline-none transition
                placeholder:text-text-muted
                focus:border-orange
              "
            />

            <input
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              placeholder="password"
              required
              minLength={8}
              className="
                w-full rounded-2xl border border-border
                bg-surface px-4 py-3 text-text
                outline-none transition
                placeholder:text-text-muted
                focus:border-orange
              "
            />

            {error && (
              <p className="text-sm text-orange-dark">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="
                w-full rounded-2xl bg-orange
                py-3 text-sm font-medium text-white
                transition hover:bg-orange-dark
                disabled:opacity-50
              "
            >
              {loading ? "creating..." : "create account"}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-text-muted">
            already have an account?{" "}
            <Link
              href="/login"
              className="font-medium text-orange-dark hover:underline"
            >
              sign in
            </Link>
          </p>
        </div>

      </div>
    </main>
  );
}