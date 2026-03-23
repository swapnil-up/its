interface User {
	id: string;
	email: string;
	full_name: string;
}

const STORAGE_KEY = 'its_auth_data';

const getStoredAuth = () => {
	if (typeof window === 'undefined') return null;
	const data = localStorage.getItem(STORAGE_KEY);
	return data ? JSON.parse(data) : null;
};

const initial = getStoredAuth();

let accessToken = $state<string | null>(initial?.token ?? null);
let user = $state<User | null>(initial?.user ?? null);

export const authStore = {
	get accessToken() {
		return accessToken;
	},
	get user() {
		return user;
	},
	get isAuthenticated() {
		return accessToken !== null;
	},
	setAuth(token: string, userData: User) {
		accessToken = token;
		user = userData;
		localStorage.setItem(STORAGE_KEY, JSON.stringify({ token, user: userData }));
	},
	clearAuth() {
		accessToken = null;
		user = null;
		localStorage.removeItem(STORAGE_KEY);
	}
};
