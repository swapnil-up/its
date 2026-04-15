const STORAGE_KEY = 'its_theme';

const getStored = () => {
	if (typeof window === 'undefined') return 'light';
	return localStorage.getItem(STORAGE_KEY) ?? 'light';
};

let theme = $state<'light' | 'dark'>(getStored());

function applyTheme(t: 'light' | 'dark') {
	if (typeof document === 'undefined') return;
	document.documentElement.classList.toggle('dark', t === 'dark');
}

export const themeStore = {
	get current() {
		return theme;
	},
	get isDark() {
		return theme === 'dark';
	},
	toggle() {
		theme = theme === 'dark' ? 'light' : 'dark';
		localStorage.setItem(STORAGE_KEY, theme);
		applyTheme(theme);
	},
	init() {
		applyTheme(theme);
	}
};
