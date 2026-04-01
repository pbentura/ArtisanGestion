<script setup lang="ts">
import { Button } from '@/components/ui/button'
import GoogleIcon from '@/components/icons/GoogleIcon.vue'
</script>

<template>
  <Button
    type="button"
    variant="outline"
    class="w-full rounded-xl py-6 font-medium border-2 hover:bg-muted transition-colors"
    @click="$emit('click')"
  >
    <GoogleIcon class="mr-2 h-5 w-5" />
    Continuer avec Google
  </Button>
</template>
