<template>
  <div class="p-8 min-h-screen bg-gray-50 font-sans">
    <h2 class="text-3xl font-bold text-center mb-8 text-gray-800">
      CodeCrash Leaderboard
    </h2>

    <div class="flex justify-center gap-4 mb-6">
      <!-- Source Buttons -->
      <button
        class="px-4 py-2 border rounded-lg transition-colors duration-200 text-sm font-medium"
        :class="{
          'bg-blue-600 text-white': activeSources.includes('CRUXEval'),
          'bg-white text-gray-700 border-gray-300 hover:bg-gray-100': !activeSources.includes('CRUXEval')
        }"
        @click="toggleSource('CRUXEval')"
      >
        CRUXEval
      </button>
      <button
        class="px-4 py-2 border rounded-lg transition-colors duration-200 text-sm font-medium"
        :class="{
          'bg-blue-600 text-white': activeSources.includes('LiveCodeBench (CE)'),
          'bg-white text-gray-700 border-gray-300 hover:bg-gray-100': !activeSources.includes('LiveCodeBench (CE)')
        }"
        @click="toggleSource('LiveCodeBench (CE)')"
      >
        LiveCodeBench (CE)
      </button>

      <!-- Expand Button -->
      <button
        class="px-4 py-2 border rounded-lg transition-colors duration-200 text-sm font-medium bg-white text-gray-700 hover:bg-gray-100"
        @click="showExpanded = !showExpanded"
      >
        {{ showExpanded ? 'Collapse' : 'Expand' }}
      </button>
    </div>

    <div class="overflow-x-auto shadow-lg rounded-xl bg-white">
      <table class="min-w-full table-auto border-collapse">
        <thead>
          <tr class="bg-gradient-to-r from-gray-100 to-gray-200 text-sm text-gray-700">
            <th class="border px-4 py-3 text-center">Model</th>
            <th
              v-for="metric in metricsWithAvg"
              :key="metric"
              class="border px-4 py-2 cursor-pointer select-none hover:bg-gray-300 transition-colors duration-150 text-center group whitespace-nowrap"
              @click="toggleSort(metric)"
            >
              <div class="h-4 leading-none invisible">▲</div>
              <div class="font-semibold">{{ metric }}</div>
              <div
                class="text-xs h-4 leading-none transition-opacity duration-150"
                :class="[
                  sortBy === metric ? 'opacity-100' : 'opacity-0 group-hover:opacity-40',
                ]"
              >
                {{ sortOrder === 'asc' ? '▲' : '▼' }}
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="{ model, values } in sortedModels"
            :key="model"
            class="hover:bg-blue-50 transition-colors duration-150"
          >
            <td class="border px-4 py-2 font-medium text-gray-800 whitespace-nowrap">
              {{ model }}
            </td>
            <td
              v-for="metric in metricsWithAvg"
              :key="metric"
              class="border w-[150px] px-4 py-2 text-center text-sm text-gray-700"
            >
              {{ typeof values[metric] === 'number' ? values[metric].toFixed(1) : '-' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>


<script setup>
import { ref, computed, onMounted } from 'vue'

// === Status ===
const leaderboardData = ref({})
const sortBy = ref('Weighted Avg')
const sortOrder = ref('desc')
const activeSources = ref(['CRUXEval', 'LiveCodeBench (CE)']) 
const showExpanded = ref(false)

// === Switch source button ===
function toggleSource(source) {
  if (activeSources.value.includes(source)) {
    activeSources.value = activeSources.value.filter(s => s !== source)
  } else {
    activeSources.value.push(source)
  }
  if (activeSources.value.length === 0) {
    activeSources.value = [source]
  }
}

// === Compute the average based on the source ===
function getWeightedAvg(score) {
  const keys = ['ALL', 'MDC', 'MPS', 'MHC']
  if (keys.some(k => score[k] === '-' || score[k] === undefined || score[k] === null || score[k] === 'None')) return '-'
  return (
    0.5 * score.ALL +
    0.125 * score.MDC +
    0.125 * score.MPS +
    0.25 * score.MHC
  )
}

function getPureAvg(score) {
  const keys = ['ALL', 'MDC', 'MPS', 'MHC']
  if (keys.some(k => score[k] === '-' || score[k] === undefined || score[k] === null || score[k] === 'None')) return '-'
  return (
    0.25 * (score.ALL + score.MDC + score.MPS + score.MHC)
  )
}

const metricsWithAvg = computed(() => {
  const base = ["VAN", "ALL", "MDC", "MPS", "MHC", "Weighted Avg"]
  const expanded = ["REN", "RTF", "GBC", "Average"]
  return showExpanded.value ? base.concat(expanded) : base
})

// === Determine which data to show based on the source ===
const sortedModels = computed(() => {
  return Object.entries(leaderboardData.value).map(([model, sourceData]) => {
    const sourceKey = activeSources.value.length === 2
      ? 'Merge'
      : activeSources.value[0] || 'CRUXEval'

    const data = sourceData[sourceKey] ?? {}

    const enriched = {
      model,
      scores: data,
      values: {
        ...data,
        "Weighted Avg": getWeightedAvg(data),
        "Average": getPureAvg(data)
      }
    }

    return enriched
  }).sort((a, b) => {
    const aVal = a.values[sortBy.value]
    const bVal = b.values[sortBy.value]
    if (typeof aVal !== 'number') return 1
    if (typeof bVal !== 'number') return -1
    return sortOrder.value === 'asc' ? aVal - bVal : bVal - aVal
  })
})

// === Toggle sort order when clicking on the column header ===
function toggleSort(column) {
  if (sortBy.value === column) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = column
    sortOrder.value = 'desc'
  }
}

// === Load data from summary.json ===
onMounted(async () => {
  try {
    const res = await fetch('/summary.json')
    leaderboardData.value = await res.json()
  } catch (e) {
    console.error('Failed to load summary.json:', e)
  }
})
</script>

<style scoped>
table {
  font-family: Arial, sans-serif;
}
</style>