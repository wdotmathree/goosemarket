import { createContext, useContext, useState, useEffect } from "react";
import { Navigate } from "react-router-dom";

const AuthContext = createContext();

export function AuthProvider({ children }) {
	const [isAdmin, setIsAdmin] = useState(false);
	const [username, setUsername] = useState(null);
	const [email, setEmail] = useState(null);
	const [userId, setUserId] = useState(null);
	const [balance, setBalance] = useState(null)
	const [update, setUpdate] = useState(false);
	const incrementBalance = amount => setBalance(prev => prev + amount);

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
		setUserId(userInfo.user_id);
		setBalance(userInfo.balance)

		setUpdate(false);
	}, [update]);

	return (
		<AuthContext.Provider
			value={{ isAdmin, setIsAdmin, username, setUsername, email, setEmail, userId, setUserId, balance, setBalance, incrementBalance, setUpdate }}
		>
			{children}
		</AuthContext.Provider>
	);
}

export function useAuth() {
	return useContext(AuthContext);
}
