<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const status = ref(null)
const entries = ref([])
const draft = ref('')
const error = ref('')
const busy = ref(false)
let timer = null

async function get(path) {
  const res = await fetch(path)
  if (!res.ok) throw new Error(`${path} → ${res.status}`)
  return res.json()
}

async function refresh() {
  try {
    status.value = await get('/api/status')
    error.value = ''
  } catch (e) {
    error.value = e.message
  }
  try {
    entries.value = await get('/api/entries')
  } catch {
    entries.value = []
  }
}

async function add() {
  const message = draft.value.trim()
  if (!message) return
  busy.value = true
  try {
    const res = await fetch('/api/entries', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    })
    if (!res.ok) throw new Error(`Could not save (${res.status})`)
    draft.value = ''
    await refresh()
  } catch (e) {
    error.value = e.message
  } finally {
    busy.value = false
  }
}

async function remove(id) {
  busy.value = true
  try {
    await fetch(`/api/entries/${id}`, { method: 'DELETE' })
    await refresh()
  } finally {
    busy.value = false
  }
}

function when(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString()
}

onMounted(() => {
  refresh()
  // Slow poll so uptime and heap visibly move during a walkthrough.
  timer = setInterval(refresh, 5000)
})
onUnmounted(() => clearInterval(timer))
</script>

<template>
  <div class="min-h-screen">
    <header class="border-b border-slate-200 bg-white">
      <div class="mx-auto max-w-4xl px-4 py-6 sm:px-6">
        <h1 class="text-xl font-semibold tracking-tight">CM Cloud Java Starter</h1>
        <p class="mt-1 text-sm text-slate-500">
          Spring Boot, Vue and managed PostgreSQL — and the path a request takes between them.
        </p>
      </div>
    </header>

    <main class="mx-auto max-w-4xl space-y-6 px-4 py-8 sm:px-6">
      <p v-if="error" class="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</p>

      <!-- The request path, drawn from live values at each hop. -->
      <section class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <h2 class="border-b border-slate-200 px-5 py-3 text-sm font-semibold">The request path</h2>

        <div v-if="status" class="divide-y divide-slate-100">
          <!-- Tier 1 -->
          <div class="flex flex-col gap-1 px-5 py-4 sm:flex-row sm:items-baseline sm:gap-6">
            <div class="w-40 shrink-0">
              <span class="text-xs font-semibold uppercase tracking-wide text-slate-400">1 · Web</span>
              <p class="text-sm font-medium">nginx</p>
            </div>
            <dl class="grid flex-1 gap-x-6 gap-y-1 text-sm sm:grid-cols-2">
              <div class="flex justify-between gap-4">
                <dt class="text-slate-500">Served by</dt>
                <dd class="text-right font-medium">{{ status.web.servedBy }}</dd>
              </div>
              <div class="flex justify-between gap-4">
                <dt class="text-slate-500">Host</dt>
                <dd class="text-right font-mono text-xs">{{ status.web.host }}</dd>
              </div>
              <div class="flex justify-between gap-4">
                <dt class="text-slate-500">Scheme</dt>
                <dd class="text-right font-medium">{{ status.web.scheme }}</dd>
              </div>
              <div class="flex justify-between gap-4">
                <dt class="text-slate-500">Client</dt>
                <dd class="text-right font-mono text-xs">{{ status.web.clientAddress }}</dd>
              </div>
            </dl>
          </div>

          <!-- Tier 2 -->
          <div class="flex flex-col gap-1 px-5 py-4 sm:flex-row sm:items-baseline sm:gap-6">
            <div class="w-40 shrink-0">
              <span class="text-xs font-semibold uppercase tracking-wide text-slate-400">2 · Application</span>
              <p class="text-sm font-medium">Spring Boot</p>
            </div>
            <dl class="grid flex-1 gap-x-6 gap-y-1 text-sm sm:grid-cols-2">
              <div class="flex justify-between gap-4">
                <dt class="text-slate-500">Java</dt>
                <dd class="text-right font-medium">{{ status.application.javaVersion }}</dd>
              </div>
              <div class="flex justify-between gap-4">
                <dt class="text-slate-500">Listening on</dt>
                <dd class="text-right font-mono text-xs">{{ status.application.listeningOn }}</dd>
              </div>
              <div class="flex justify-between gap-4">
                <dt class="text-slate-500">Heap</dt>
                <dd class="text-right font-medium">
                  {{ status.application.heapUsedMb }} / {{ status.application.heapMaxMb }} MB
                </dd>
              </div>
              <div class="flex justify-between gap-4">
                <dt class="text-slate-500">Uptime</dt>
                <dd class="text-right font-medium">{{ status.application.uptime }}</dd>
              </div>
              <div class="flex justify-between gap-4">
                <dt class="text-slate-500">Host</dt>
                <dd class="text-right font-mono text-xs">{{ status.application.hostname }}</dd>
              </div>
              <div class="flex justify-between gap-4">
                <dt class="text-slate-500">vCPU</dt>
                <dd class="text-right font-medium">{{ status.application.availableProcessors }}</dd>
              </div>
            </dl>
          </div>

          <!-- Tier 3 -->
          <div class="flex flex-col gap-1 px-5 py-4 sm:flex-row sm:items-baseline sm:gap-6">
            <div class="w-40 shrink-0">
              <span class="text-xs font-semibold uppercase tracking-wide text-slate-400">3 · Data</span>
              <p class="text-sm font-medium">Managed PostgreSQL</p>
            </div>

            <dl v-if="status.database.reachable" class="grid flex-1 gap-x-6 gap-y-1 text-sm sm:grid-cols-2">
              <div class="flex justify-between gap-4">
                <dt class="text-slate-500">Server</dt>
                <dd class="text-right font-medium">{{ status.database.serverVersion }}</dd>
              </div>
              <div class="flex justify-between gap-4">
                <dt class="text-slate-500">TLS</dt>
                <dd class="text-right font-medium">{{ status.database.tls }}</dd>
              </div>
              <div class="flex justify-between gap-4">
                <dt class="text-slate-500">Dialled</dt>
                <dd class="text-right font-mono text-xs">{{ status.database.configuredEndpoint }}</dd>
              </div>
              <div class="flex justify-between gap-4">
                <dt class="text-slate-500">Backend answered</dt>
                <dd class="text-right font-mono text-xs">{{ status.database.backendAddress }}</dd>
              </div>
              <div class="flex justify-between gap-4">
                <dt class="text-slate-500">Database</dt>
                <dd class="text-right font-mono text-xs">{{ status.database.connectedDatabase }}</dd>
              </div>
              <div class="flex justify-between gap-4">
                <dt class="text-slate-500">Role</dt>
                <dd class="text-right font-mono text-xs">{{ status.database.connectedUser }}</dd>
              </div>
              <div class="flex justify-between gap-4">
                <dt class="text-slate-500">Round trip</dt>
                <dd class="text-right font-medium">{{ status.database.roundTripMs }} ms</dd>
              </div>
              <div class="flex justify-between gap-4">
                <dt class="text-slate-500">Rows stored</dt>
                <dd class="text-right font-medium">{{ status.database.rowCount }}</dd>
              </div>
            </dl>

            <p v-else class="flex-1 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
              Not reachable — {{ status.database.error }}
            </p>
          </div>
        </div>

        <p v-else class="px-5 py-8 text-center text-sm text-slate-400">Loading…</p>
      </section>

      <p
        v-if="status && status.database.reachable
              && status.database.configuredEndpoint !== status.database.backendAddress"
        class="rounded-lg bg-slate-900/[0.03] px-4 py-3 text-sm text-slate-600"
      >
        The application dialled
        <span class="font-mono text-xs">{{ status.database.configuredEndpoint }}</span>
        and a backend at
        <span class="font-mono text-xs">{{ status.database.backendAddress }}</span>
        answered. That gap is the connection pooler: the app holds one cheap connection to the
        pooler, and the pooler shares a small set of real database connections across everything.
      </p>

      <!-- Persistence proof -->
      <section class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 class="text-sm font-semibold">Write something to the database</h2>
        <p class="mt-1 text-sm text-slate-500">
          It is stored in PostgreSQL, not in the application. Restart the service and it is still here.
        </p>

        <form class="mt-4 flex flex-col gap-2 sm:flex-row" @submit.prevent="add">
          <label for="msg" class="sr-only">Message</label>
          <input
            id="msg"
            v-model="draft"
            maxlength="200"
            placeholder="Anything at all"
            class="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-900/10"
          />
          <button
            type="submit"
            :disabled="busy || !draft.trim()"
            class="shrink-0 rounded-lg bg-slate-900 px-5 py-2 text-sm font-medium text-white transition hover:bg-slate-700 disabled:opacity-40"
          >
            Save
          </button>
        </form>

        <ul v-if="entries.length" class="mt-4 divide-y divide-slate-100">
          <li v-for="e in entries" :key="e.id" class="flex items-start justify-between gap-4 py-3">
            <div class="min-w-0">
              <p class="break-words text-sm">{{ e.message }}</p>
              <p class="mt-0.5 text-xs text-slate-400">#{{ e.id }} · {{ when(e.createdAt) }}</p>
            </div>
            <button
              type="button"
              :disabled="busy"
              class="shrink-0 text-xs text-slate-400 transition hover:text-red-600 disabled:opacity-40"
              @click="remove(e.id)"
            >
              Delete
            </button>
          </li>
        </ul>

        <p v-else class="mt-4 text-sm text-slate-400">No rows yet.</p>
      </section>
    </main>

    <footer class="mx-auto max-w-4xl px-4 pb-10 text-xs text-slate-400 sm:px-6">
      Refreshes every 5 seconds · <span class="font-mono">/actuator/health</span> for monitoring
    </footer>
  </div>
</template>
