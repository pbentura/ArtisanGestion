<script setup lang="ts">
import { Plus } from 'lucide-vue-next'

defineEmits(['click'])
</script>

<template>
  <button class="mobile-fab" @click="$emit('click')">
    <Plus class="w-6 h-6" />
  </button>
</template>

<style scoped>
.mobile-fab {
  position: fixed;
  bottom: calc(80px + env(safe-area-inset-bottom, 0px));
  right: 16px;
  width: 56px;
  height: 56px;
  border-radius: 28px;
  background: var(--primary);
  color: var(--primary-foreground);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  border: none;
  z-index: 40;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.mobile-fab:active {
  transform: scale(0.95);
}
</style>
