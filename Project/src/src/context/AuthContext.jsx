import { createContext, useContext, useState, useEffect } from "react";
import { Navigate } from "react-router-dom";

const AuthContext = createContext();

export function AuthProvider({ children }) {
	const [isAdmin, setIsAdmin] = useState(false);
	const [username, setUsername] = useState(null);
	const [email, setEmail] = useState(null);
	const [update, setUpdate] = useState(false);

	useEffect(() => {
		// Load from cookie
		if (document.cookie.includes("user-info") == false) {
			if (window.location.pathname !== "/login") window.location.href = "/login";
			return;
		}
		const userInfo = JSON.parse(atob(document.cookie.split("user-info=")[1].split(";")[0]));
		if (!userInfo && window.location.pathname !== "/login") window.location.href = "/login";

		setIsAdmin(userInfo.admin);
		setUsername(userInfo.username);
		setEmail(userInfo.email);

		setUpdate(false);
	}, [update]);

	return (
		<AuthContext.Provider value={{ isAdmin, setIsAdmin, username, setUsername, email, setEmail, setUpdate }}>
			{children}
		</AuthContext.Provider>
	);
}

export function useAuth() {
	return useContext(AuthContext);
}
