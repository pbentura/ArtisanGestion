<script setup lang="ts">
import HeroSection from '@/components/landing/HeroSection.vue'
// import StatsSection from '@/components/landing/StatsSection.vue'
import Features from '@/components/landing/Features.vue'
import VideoSection from '@/components/landing/VideoSection.vue'
import AIRapportSection from '@/components/landing/AIRapportSection.vue'
import CompareSection from '@/components/landing/CompareSection.vue'
// TestimonialsSection reste désactivée : ses témoignages sont encore des
// exemples marqués « [À REMPLACER] ». Publier de faux avis violerait les
// règles Google Ads — à réactiver avec de vrais retours d'artisans.
// import TestimonialsSection from '@/components/landing/TestimonialsSection.vue'
import Pricing from '@/components/landing/Pricing.vue'
import FAQSection from '@/components/landing/FAQSection.vue'
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
    <!-- Répond aux objections juste après les tarifs, avant le dernier CTA. -->
    <FAQSection />
    <CTAFinal />
    <Footer />
  </div>
</template>
