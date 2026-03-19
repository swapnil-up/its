import { writable, derived } from 'svelte/store'

interface AuthState {
    accessToken: string | null
    user: { id: string; email: string; full_name: string } | null
}

function createAuthStore() {
    const { subscribe, set, update } = writable<AuthState>({
        accessToken: null,
        user: null
    })

    return {
        subscribe,
        setAuth: (token: string, user: AuthState['user']) => {
            set({ accessToken: token, user })
        },
        clearAuth: () => {
            set({ accessToken: null, user: null })
        }
    }
}

export const authStore = createAuthStore()
export const isAuthenticated = derived(
    authStore,
    $auth => $auth.accessToken !== null
)