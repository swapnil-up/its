<script lang="ts">
  import { Button } from '$lib/components/ui/button'
  import { ChevronLeft, ChevronRight } from 'lucide-svelte'

  let {
    currentPage,
    totalPages,
    onPageChange
  }: {
    currentPage: number
    totalPages: number
    onPageChange: (page: number) => void
  } = $props()
</script>

{#if totalPages > 1}
  <div class="flex items-center justify-between px-1">
    <p class="text-sm text-muted-foreground">
      Page {currentPage} of {totalPages}
    </p>
    <div class="flex items-center gap-1">
      <Button
        variant="outline"
        size="sm"
        disabled={currentPage === 1}
        onclick={() => onPageChange(currentPage - 1)}
      >
        <ChevronLeft class="h-4 w-4" />
      </Button>

      {#each Array.from({ length: totalPages }, (_, i) => i + 1) as page}
        <Button
          variant={page === currentPage ? 'default' : 'outline'}
          size="sm"
          onclick={() => onPageChange(page)}
        >
          {page}
        </Button>
      {/each}

      <Button
        variant="outline"
        size="sm"
        disabled={currentPage >= totalPages}
        onclick={() => onPageChange(currentPage + 1)}
      >
        <ChevronRight class="h-4 w-4" />
      </Button>
    </div>
  </div>
{/if}