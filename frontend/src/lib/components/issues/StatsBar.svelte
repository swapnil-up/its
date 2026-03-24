<script lang="ts">
    import * as Card from '$lib/components/ui/card'
    import { 
        Clock, 
        CircleCheck, 
        CircleX, 
        PlayCircle, 
        Activity,      
        Info,          
        AlertTriangle, 
        ShieldAlert,   
        Flame          
    } from 'lucide-svelte'

    let { stats }: { stats: {
        total: number,
        by_status: Record<string, number>,
        by_severity: Record<string, number>
    }} = $props()
</script>

<div class="flex px-4">
    <div class="flex items-center gap-4 rounded-xl border-2 border-primary/20 bg-primary/5 p-6 shadow-sm sm:col-span-2 lg:col-span-4">
        <div class="rounded-full bg-primary p-3">
            <Activity class="h-6 w-6 text-primary-foreground" />
        </div>
        <div>
            <p class="text-4xl font-black leading-none tracking-tight text-center">{stats.total}</p>
            <p class="text-sm text-muted-foreground  font-bold uppercase tracking-widest">Total Tickets</p>
        </div>
    </div>

<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 px-4 flex-1">
    <div class="flex items-center gap-4 rounded-xl border bg-card p-4 shadow-sm">
        <div class="rounded-full bg-blue-100 p-2">
            <Clock class="h-5 w-5 text-blue-600" />
        </div>
        <div>
            <p class="text-2xl font-bold leading-none">{stats.by_status.new || 0}</p>
            <p class="text-xs text-muted-foreground  font-medium uppercase">New</p>
        </div>
    </div>

    <div class="flex items-center gap-4 rounded-xl border bg-card p-4 shadow-sm">
        <div class="rounded-full bg-amber-100 p-2">
            <PlayCircle class="h-5 w-5 text-amber-600" />
        </div>
        <div>
            <p class="text-2xl font-bold leading-none">{stats.by_status.in_progress || 0}</p>
            <p class="text-xs text-muted-foreground  font-medium uppercase">In Progress</p>
        </div>
    </div>

    <div class="flex items-center gap-4 rounded-xl border bg-card p-4 shadow-sm">
        <div class="rounded-full bg-emerald-100 p-2">
            <CircleCheck class="h-5 w-5 text-emerald-600" />
        </div>
        <div>
            <p class="text-2xl font-bold leading-none">{stats.by_status.resolved || 0}</p>
            <p class="text-xs text-muted-foreground  font-medium uppercase">Resolved</p>
        </div>
    </div>

    <div class="flex items-center gap-4 rounded-xl border bg-card p-4 shadow-sm">
        <div class="rounded-full bg-slate-100 p-2">
            <CircleX class="h-5 w-5 text-slate-600" />
        </div>
        <div>
            <p class="text-2xl font-bold leading-none">{stats.by_status.closed || 0}</p>
            <p class="text-xs text-muted-foreground  font-medium uppercase">Closed</p>
        </div>
    </div>

    <div class="flex items-center gap-4 rounded-xl border bg-card p-4 shadow-sm">
        <div class="rounded-full bg-blue-50 p-2">
            <Info class="h-5 w-5 text-blue-500" />
        </div>
        <div>
            <p class="text-2xl font-bold leading-none">{stats.by_severity.low || 0}</p>
            <p class="text-xs text-muted-foreground  font-medium uppercase">Low</p>
        </div>
    </div>

    <div class="flex items-center gap-4 rounded-xl border bg-card p-4 shadow-sm border-l-4 border-l-yellow-400">
        <div class="rounded-full bg-yellow-100 p-2">
            <AlertTriangle class="h-5 w-5 text-yellow-600" />
        </div>
        <div>
            <p class="text-2xl font-bold leading-none">{stats.by_severity.medium || 0}</p>
            <p class="text-xs text-muted-foreground  font-medium uppercase">Medium</p>
        </div>
    </div>

    <div class="flex items-center gap-4 rounded-xl border bg-card p-4 shadow-sm border-l-4 border-l-orange-500">
        <div class="rounded-full bg-orange-100 p-2">
            <ShieldAlert class="h-5 w-5 text-orange-600" />
        </div>
        <div>
            <p class="text-2xl font-bold leading-none">{stats.by_severity.high || 0}</p>
            <p class="text-xs text-muted-foreground  font-medium uppercase">High</p>
        </div>
    </div>

    <div class="flex items-center gap-4 rounded-xl border-2 border-red-200 bg-red-50 p-4 shadow-sm">
        <div class="rounded-full bg-red-600 p-2 text-white">
            <Flame class="h-5 w-5 animate-pulse" />
        </div>
        <div>
            <p class="text-2xl font-black leading-none text-red-700">{stats.by_severity.critical || 0}</p>
            <p class="text-xs text-red-600  font-bold uppercase">Critical</p>
        </div>
    </div>
</div>
</div>