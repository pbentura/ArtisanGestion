<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'

const props = defineProps<{
  isOpen: boolean
  title?: string
}>()

const emit = defineEmits(['close'])

const sheetContent = ref<HTMLElement | null>(null)
let startY = 0
let currentY = 0

function close() {
  emit('close')
}

function handleTouchStart(e: TouchEvent) {
  startY = e.touches[0].clientY
  currentY = startY
}

function handleTouchMove(e: TouchEvent) {
  currentY = e.touches[0].clientY
  const delta = currentY - startY
  
  if (delta > 0 && sheetContent.value) {
    // Ne pas faire de drag si on scroll dans le contenu (basique)
    const scrollTop = sheetContent.value.scrollTop
    if (scrollTop <= 0) {
      e.preventDefault()
      sheetContent.value.style.transform = `translateY(${delta}px)`
    }
  }
}

function handleTouchEnd() {
  const delta = currentY - startY
  if (delta > 100) {
    close()
  }
  
  if (sheetContent.value) {
    sheetContent.value.style.transform = ''
  }
}

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

onUnmounted(() => {
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <div class="bottom-sheet-wrapper" :class="{ 'is-open': isOpen }">
      <div class="overlay" @click="close"></div>
      
      <div 
        class="sheet" 
        ref="sheetContent"
        @touchstart="handleTouchStart"
        @touchmove="handleTouchMove"
        @touchend="handleTouchEnd"
      >
        <div class="drag-handle"></div>
        
        <div v-if="title" class="sheet-header">
          <h3 class="sheet-title">{{ title }}</h3>
        </div>
        
        <div class="sheet-content">
          <slot></slot>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.bottom-sheet-wrapper {
  position: fixed;
  inset: 0;
  z-index: 100;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.bottom-sheet-wrapper.is-open {
  pointer-events: auto;
}

.overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(2px);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.is-open .overlay {
  opacity: 1;
}

.sheet {
  background: var(--card);
  border-top-left-radius: 20px;
  border-top-right-radius: 20px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  transform: translateY(100%);
  transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1);
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.1);
  padding-bottom: env(safe-area-inset-bottom, 0px);
  position: relative;
  z-index: 1;
}

.is-open .sheet {
  transform: translateY(0);
}

.drag-handle {
  width: 36px;
  height: 5px;
  background: var(--border);
  border-radius: 3px;
  margin: 12px auto;
}

.sheet-header {
  padding: 0 16px 12px 16px;
  text-align: center;
}

.sheet-title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--muted-foreground);
}

.sheet-content {
  overflow-y: auto;
  padding: 0 16px 24px 16px;
}
</style>
