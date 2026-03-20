interface User {
	id: string;
	email: string;
	full_name: string;
}

let accessToken = $state<string | null>(null);
let user = $state<User | null>(null);

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
	},
	clearAuth() {
		accessToken = null;
		user = null;
	}
};
