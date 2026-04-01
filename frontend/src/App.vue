<script setup lang="ts">
import { ref, onMounted } from 'vue'

const message = ref('Chargement...')
const error = ref<string | null>(null)

async function fetchHello() {
  try {
    const res = await fetch('http://localhost:8000/')
    if (!res.ok) throw new Error('Erreur réseau')
    const data = await res.json()
    console.log(data)
    message.value = data.message
  } catch (e: any) {
    error.value = "Impossible de contacter le backend (" + e.message + ")"
  }
}

onMounted(() => {
  fetchHello()
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-zinc-950 text-white font-sans">
    <div class="max-w-md w-full p-8 rounded-2xl bg-zinc-900 border border-zinc-800 shadow-2xl text-center space-y-6">
      <div class="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/20 mb-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      
      <h1 class="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent">
        Ventura Minimal
      </h1>
      
      <p v-if="error" class="text-red-400 bg-red-400/10 p-3 rounded-lg border border-red-400/20 text-sm">
        {{ error }}
      </p>
      <p v-else class="text-zinc-400 text-lg">
        {{ message }}
      </p>

      <div class="pt-4 flex flex-col gap-2">
        <div class="flex items-center justify-center gap-2 text-xs text-zinc-500">
          <span class="px-2 py-1 rounded bg-zinc-800">FastAPI</span>
          <span class="px-2 py-1 rounded bg-zinc-800">Vue 3</span>
          <span class="px-2 py-1 rounded bg-zinc-800">Docker</span>
        </div>
      </div>
    </div>
  </div>
</template>
