import { authStore } from './stores/auth.svelte'

const BASE_URL = 'http://localhost:8000'

export async function apiFetch(path: string, options: RequestInit = {}) {
    const accessToken = authStore.accessToken

    const headers: Record<string, string> = {

        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string> ?? {})
    }

    if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`
    }
    const res = await fetch(`${BASE_URL}${path}`, {
        ...options,
        headers,
        credentials: 'include'
    })

    return res

}