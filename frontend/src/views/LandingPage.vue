<script setup lang="ts">
import HeroSection from '@/components/landing/HeroSection.vue'
import ProblemSolution from '@/components/landing/ProblemSolution.vue'
import Features from '@/components/landing/Features.vue'
import DemoVisual from '@/components/landing/DemoVisual.vue'
import Benefits from '@/components/landing/Benefits.vue'
import Pricing from '@/components/landing/Pricing.vue'
import CTAFinal from '@/components/landing/CTAFinal.vue'
import Footer from '@/components/landing/Footer.vue'
</script>

<template>
  <div>
    <HeroSection />
    <ProblemSolution />
    <Features id="features" />
    <DemoVisual id="demo" />
    <Benefits />
    <Pricing id="pricing" />
    <CTAFinal id="cta" />
    <Footer />
  </div>
</template>
