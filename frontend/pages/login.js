import { signIn, useSession } from "next-auth/react";
import { useEffect } from "react";

export default function Login() {
  const { data: session } = useSession();

  useEffect(() => {
    if (!session) {
      // Redirect to Google login immediately
      signIn("google");
    }
  }, [session]);

  return <div>{session ? "You are logged in." : "Redirecting to Google..."}</div>;
}
