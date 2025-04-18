<template>
  <main class="min-h-screen bg-white text-gray-800 px-8 py-10 font-sans">
    <!-- Title -->
    <h1 class="text-5xl font-bold mb-6 text-center">
      <span>{{ title }}</span>
    </h1>

    <!-- Authors -->
    <section class="mb-12 text-center">
      <div class="text-xl mb-3 font-semibold">
        <span v-for="(author, index) in authors" :key="author.name">
          <a :href="author.url" class="text-blue-600 hover:underline" target="_blank" rel="noopener">
            {{ author.name }}
          </a><sup>{{ author.affiliationId }}</sup><span v-if="index !== authors.length - 1">, </span>
        </span>
      </div>
      <div class="text-base text-gray-600 flex justify-center flex-wrap gap-x-6">
        <div v-for="(affiliation, id) in affiliations" :key="id">
          <sup>{{ id }}</sup> {{ affiliation }}
        </div>
      </div>
    </section>

    <!-- Buttons -->
    <div class="flex justify-center flex-wrap gap-4 mt-6">
      <!-- 外部連結 -->
      <a
        v-for="link in allLinks"
        :key="link.label"
        :href="link.url"
        class="flex items-center gap-2 px-5 py-2.5 bg-black text-white rounded-xl text-base font-semibold hover:bg-gray-800 transition"
        target="_blank"
        rel="noopener"
      >
        <component :is="link.icon" class="w-5 h-5" />
        {{ link.label }}
      </a>

      <!-- 切換頁面的內部按鈕 -->
      <RouterLink
        :to="navLink.route"
        class="flex items-center gap-2 px-5 py-2.5 bg-black text-white rounded-xl text-base font-semibold hover:bg-gray-800 transition"
      >
        <component :is="navLink.icon" class="w-5 h-5" />
        {{ navLink.label }}
      </RouterLink>
    </div>

    <!-- Routed Page Content -->
    <div class="mt-10">
      <router-view />
    </div>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { FileText, Github, Database, BarChart2, Home } from 'lucide-vue-next'

const route = useRoute()

const title = 'CodeCrash: Stress Testing LLM Reasoning under Structural and Semantic Perturbations'

const authors = [
  { name: 'Man Ho Lam', affiliationId: 1, url: 'https://donaldlamnl.github.io/DonaldLamNL' },
  { name: 'Chaozheng Wang', affiliationId: 1, url: 'https://adf1178.github.io' },
  { name: 'Jen-tse Huang', affiliationId: 2, url: 'https://penguinnnnn.github.io' },
  { name: 'Michael R. Lyu', affiliationId: 1, url: 'https://www.cse.cuhk.edu.hk/lyu/home' },
]

const affiliations = {
  1: 'The Chinese University of Hong Kong',
  2: 'Johns Hopkins University',
}

// 全部的 link（Paper/Code/Data 為 external）
const allLinks = [
  { label: 'Paper', icon: FileText, url: 'https://arxiv.org/abs/your-paper-id' },
  { label: 'Code', icon: Github, url: 'https://github.com/CUHK-ARISE/CodeCrash' },
  { label: 'Data', icon: Database, url: 'https://huggingface.co/datasets/CUHK-ARISE/CodeCrash' },
]

// 根據當前路由，決定要顯示 Home 還是 Leaderboard
const navLink = computed(() =>
  route.path === '/leaderboard'
    ? { label: 'Home', icon: Home, route: '/', internal: true }
    : { label: 'Leaderboard', icon: BarChart2, route: '/leaderboard', internal: true }
)
</script>

<style scoped>
/* Add styles if needed */
</style>