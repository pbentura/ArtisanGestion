<script setup lang="ts">
const props = defineProps<{
  options: { label: string, value: string }[]
  modelValue: string
}>()

const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <div class="segmented-control">
    <button 
      v-for="option in options" 
      :key="option.value"
      class="segment-btn"
      :class="{ 'active': modelValue === option.value }"
      @click="emit('update:modelValue', option.value)"
    >
      {{ option.label }}
    </button>
  </div>
</template>

<style scoped>
.segmented-control {
  display: flex;
  background: var(--muted);
  padding: 4px;
  border-radius: 12px;
  width: 100%;
  margin-bottom: 16px;
}

.segment-btn {
  flex: 1;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--muted-foreground);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  -webkit-tap-highlight-color: transparent;
}

.segment-btn.active {
  background: var(--card);
  color: var(--foreground);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
</style>
