<script setup lang="ts">
defineProps<{
  src: string
  alt?: string
}>()
</script>

<template>
  <div class="iphone-mockup relative w-[280px] h-[580px] sm:w-[300px] sm:h-[620px] rounded-[3rem] bg-black p-[10px] shadow-[inset_0_0_2px_1px_rgba(255,255,255,0.2),0_0_0_1px_#333,0_0_0_3px_#111,0_25px_50px_-12px_rgba(0,0,0,0.5)]">
    <!-- Hardware Buttons -->
    <!-- Action Button -->
    <div class="absolute left-[-4px] top-[100px] w-[3px] h-[26px] bg-[#222] rounded-l-md border-l border-y border-[#444]"></div>
    <!-- Volume Up -->
    <div class="absolute left-[-4px] top-[145px] w-[3px] h-[50px] bg-[#222] rounded-l-md border-l border-y border-[#444]"></div>
    <!-- Volume Down -->
    <div class="absolute left-[-4px] top-[210px] w-[3px] h-[50px] bg-[#222] rounded-l-md border-l border-y border-[#444]"></div>
    <!-- Power Button -->
    <div class="absolute right-[-4px] top-[160px] w-[3px] h-[75px] bg-[#222] rounded-r-md border-r border-y border-[#444]"></div>
    
    <!-- Screen -->
    <div class="relative w-full h-full bg-background rounded-[2.25rem] overflow-hidden flex flex-col border border-border/10 ring-1 ring-black">
      
      <!-- Dynamic Island -->
      <div class="absolute top-2 left-1/2 -translate-x-1/2 w-[90px] h-[26px] bg-black rounded-full z-20 flex items-center justify-between px-2 shadow-[inset_0_0_2px_rgba(255,255,255,0.1)]">
        <!-- Hidden sensors -->
        <div class="w-[8px] h-[8px] rounded-full bg-[#050505] ml-0.5 shadow-[inset_0_1px_2px_rgba(255,255,255,0.05)]"></div>
        <!-- Front Camera -->
        <div class="w-[12px] h-[12px] rounded-full bg-[#0a0a0a] flex items-center justify-center shadow-[inset_0_0_4px_rgba(255,255,255,0.15)] border border-[#1a1a1a]">
          <div class="w-[3px] h-[3px] bg-[#1a1a4a] rounded-full blur-[0.5px]"></div>
        </div>
      </div>

      <img :src="src" :alt="alt || 'App screenshot'" class="w-full h-full object-cover" />
    </div>
  </div>
</template>
