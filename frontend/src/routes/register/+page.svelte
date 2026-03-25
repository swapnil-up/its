<script lang="ts">
  import { goto } from '$app/navigation'
  import * as Card from '$lib/components/ui/card'
  import { Button } from '$lib/components/ui/button'
  import { Input } from '$lib/components/ui/input'
  import { Label } from '$lib/components/ui/label'
  import { Alert, AlertDescription } from '$lib/components/ui/alert'
  import { apiFetch } from '$lib/api'

  let fullName = $state('')
  let email = $state('')
  let password = $state('')
  let loading = $state(false)
  let error = $state<string | null>(null)

  let isValid = $derived(
    fullName.length > 0 &&
    email.includes('@') &&
    password.length >= 8
  )

  async function handleRegister() {
    loading = true
    error = null
    try {
      const res = await apiFetch('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ full_name: fullName, email, password })
      })
      if (!res.ok) {
        const data = await res.json()
        error = data.detail[0].msg ?? 'Registration failed'
        return
      }
      goto('/login?registered=true')
    } catch {
      error = 'Could not reach server'
    } finally {
      loading = false
    }
  }
</script>

<div class="min-h-screen flex items-center justify-center bg-background">
  <Card.Root class="w-full max-w-md">
    <Card.Header>
      <Card.Title>Create an account</Card.Title>
      <Card.Description>Start tracking issues today</Card.Description>
    </Card.Header>
    <Card.Content class="space-y-4">
      {#if error}
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      {/if}

      <div class="space-y-2">
        <Label for="name">Full name</Label>
        <Input id="name" bind:value={fullName} placeholder="Ada Lovelace" />
      </div>
      <div class="space-y-2">
        <Label for="email">Email</Label>
        <Input id="email" type="email" bind:value={email} placeholder="ada@example.com" />
      </div>
      <div class="space-y-2">
        <Label for="password">Password</Label>
        <Input id="password" type="password" bind:value={password} placeholder="8+ characters" />
      </div>
    </Card.Content>
    <Card.Footer class="flex flex-col gap-3">
      <Button
        class="w-full"
        disabled={!isValid || loading}
        onclick={handleRegister}
      >
        {loading ? 'Creating account...' : 'Create account'}
      </Button>
      <p class="text-sm text-muted-foreground text-center">
        Already have an account?
        <a href="/login" class="underline">Sign in</a>
      </p>
    </Card.Footer>
  </Card.Root>
</div>