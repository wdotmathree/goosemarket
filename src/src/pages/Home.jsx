import { Navigate } from "react-router-dom";

export default function Home() {
	if (document.cookie.includes("user-info")) {
		return <Navigate to="/dashboard" />;
	} else {
		// Temporary redirection to Login page
		// In the future we should have a proper landing page
		return <Navigate to="/login" />;
	}
}
