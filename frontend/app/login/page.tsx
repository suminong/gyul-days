"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";


export default function LoginPage() {
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setError("");
    setLoading(true);

    const formData = new URLSearchParams();

    formData.append("username", username);
    formData.append("password", password);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/auth/login`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/x-www-form-urlencoded",
          },
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(
          "Invalid username or password"
        );
      }

      const data = await response.json();

      localStorage.setItem(
        "access_token",
        data.access_token
      );

      router.push("/");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong"
      );
    } finally {
      setLoading(false);
    }
  }


  return (
    <main className="min-h-screen bg-background text-text">
      <div className="mx-auto flex min-h-screen max-w-md items-center px-6">

        <div className="w-full">

          <h1 className="mb-2 text-3xl font-semibold tracking-tight text-orange-dark">
            gyul days
          </h1>

          <p className="mb-10 text-sm text-text-muted">
            come back to your days.
          </p>


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
              className="
                w-full
                rounded-2xl
                border
                border-border
                bg-surface
                px-4
                py-3
                text-text
                outline-none
                transition
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
              className="
                w-full
                rounded-2xl
                border
                border-border
                bg-surface
                px-4
                py-3
                text-text
                outline-none
                transition
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
                w-full
                rounded-2xl
                bg-orange
                py-3
                text-sm
                font-medium
                text-white
                transition
                hover:bg-orange-dark
                disabled:opacity-50
              "
            >
              {loading
                ? "signing in..."
                : "sign in"}
            </button>

          </form>


          <p className="mt-6 text-center text-sm text-text-muted">
            new here?{" "}
            <Link
              href="/signup"
              className="font-medium text-orange-dark hover:underline"
            >
              create an account
            </Link>
          </p>

        </div>
      </div>
    </main>
  );
}