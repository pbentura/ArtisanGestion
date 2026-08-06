<script setup lang="ts">
import HeroSection from '@/components/landing/HeroSection.vue'
// import StatsSection from '@/components/landing/StatsSection.vue'
import Features from '@/components/landing/Features.vue'
import VideoSection from '@/components/landing/VideoSection.vue'
import AIRapportSection from '@/components/landing/AIRapportSection.vue'
import CompareSection from '@/components/landing/CompareSection.vue'
// import TestimonialsSection from '@/components/landing/TestimonialsSection.vue'
import Pricing from '@/components/landing/Pricing.vue'
// import FAQSection from '@/components/landing/FAQSection.vue'
import CTAFinal from '@/components/landing/CTAFinal.vue'
import Footer from '@/components/landing/Footer.vue'
</script>

<template>
  <div class="overflow-x-hidden">
    <HeroSection />
    <!-- <StatsSection /> -->
    <Features />
    <AIRapportSection />
    <VideoSection />
    <CompareSection />
    <!-- <TestimonialsSection /> -->
    <Pricing />
    <!-- <FAQSection /> -->
    <CTAFinal />
    <Footer />
  </div>
</template>
