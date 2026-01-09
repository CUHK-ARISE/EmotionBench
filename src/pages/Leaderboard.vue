<template>
  <div class="mt-4 text-gray-700 text-base">
    <div class="mt-10 text-gray-700 text-base">
      <p class="text-md mx-auto leading-relaxed text-justify">
        The leaderboard displays the performance of various models across different emotional scenarios.
        Select an emotion category and optionally filter by specific factors to see how models respond to emotional stimuli.
      </p>
    </div>

    <!-- Emotion Buttons -->
    <div class="flex flex-wrap justify-center gap-3 mb-4 mt-6">
      <button
        v-for="emotion in emotions"
        :key="emotion"
        class="px-4 py-2 border rounded-lg transition-colors duration-200 text-sm font-medium"
        :class="{
          'bg-blue-600 text-white': selectedEmotion === emotion,
          'bg-white text-gray-700 border-gray-300 hover:bg-gray-100': selectedEmotion !== emotion
        }"
        @click="selectEmotion(emotion)"
      >
        {{ emotion }}
      </button>
    </div>

    <!-- Factor Buttons (shown when emotion is not Overall) -->
    <div v-if="selectedEmotion !== 'Overall' && factors.length > 0" class="flex flex-wrap justify-center gap-2 mb-4">
      <button
        v-for="factor in factors"
        :key="factor"
        class="px-3 py-1.5 border rounded-lg transition-colors duration-200 text-xs font-medium"
        :class="{
          'bg-green-600 text-white': selectedFactors.includes(factor),
          'bg-white text-gray-600 border-gray-300 hover:bg-gray-100': !selectedFactors.includes(factor)
        }"
        @click="toggleFactor(factor)"
      >
        {{ factor }}
      </button>
    </div>

    <!-- View Mode Toggle -->
    <div class="flex justify-center gap-3 mb-6">
      <button
        class="px-4 py-2 border rounded-lg transition-colors duration-200 text-sm font-medium"
        :class="{
          'bg-purple-600 text-white': viewMode === 'actual',
          'bg-white text-gray-700 border-gray-300 hover:bg-gray-100': viewMode !== 'actual'
        }"
        @click="viewMode = 'actual'"
      >
        Actual Value
      </button>
      <button
        class="px-4 py-2 border rounded-lg transition-colors duration-200 text-sm font-medium"
        :class="{
          'bg-purple-600 text-white': viewMode === 'difference',
          'bg-white text-gray-700 border-gray-300 hover:bg-gray-100': viewMode !== 'difference'
        }"
        @click="viewMode = 'difference'"
      >
        Difference
      </button>
    </div>

    <div class="overflow-x-auto shadow-lg rounded-xl bg-white">
      <table class="min-w-full table-auto border-collapse text-lg">
        <thead>
          <tr class="bg-gradient-to-r from-gray-100 to-gray-200 text-base text-gray-700">
            <th
              class="border px-4 py-3 text-center cursor-pointer select-none hover:bg-gray-300 transition-colors duration-150 group"
              @click="toggleSort('model')"
            >
              <div class="h-4 leading-none invisible">▲</div>
              <div class="font-semibold">Model</div>
              <div
                class="text-xs h-4 leading-none transition-opacity duration-150"
                :class="[
                  sortBy === 'model' ? 'opacity-100' : 'opacity-0 group-hover:opacity-40',
                ]"
              >
                {{ sortOrder === 'asc' ? '▲' : '▼' }}
              </div>
            </th>
            <th
              v-for="col in columns"
              :key="col.key"
              class="border px-4 py-2 cursor-pointer select-none hover:bg-gray-300 transition-colors duration-150 text-center group whitespace-nowrap"
              @click="toggleSort(col.key)"
            >
              <div class="h-4 leading-none invisible">▲</div>
              <div class="font-semibold">{{ col.label }}</div>
              <div
                class="text-xs h-4 leading-none transition-opacity duration-150"
                :class="[
                  sortBy === col.key ? 'opacity-100' : 'opacity-0 group-hover:opacity-40',
                ]"
              >
                {{ sortOrder === 'asc' ? '▲' : '▼' }}
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in sortedRows"
            :key="row.model"
            class="hover:bg-blue-50 transition-colors duration-150"
          >
            <td class="border px-4 py-2 font-medium text-gray-800 whitespace-nowrap text-base">
              {{ row.model }}
            </td>
            <td
              v-for="col in columns"
              :key="col.key"
              class="border px-4 py-2 text-center"
              :class="getCellClass(col.key, row[col.key])"
            >
              {{ formatCell(col.key, row[col.key]) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="mt-10 text-gray-700 text-base">
      <h2 class="text-4xl font-bold mt-12 mb-4">📝 Notes</h2>
      <ul class="list-disc list-inside leading-relaxed text-left">
        <li><strong>Control:</strong> Baseline scores without emotional stimuli.</li>
        <li><strong>Positive/Negative Affect:</strong> Average scores across selected factors.</li>
        <li><strong>Diff:</strong> Difference from control (value minus control).</li>
      </ul>
    </div>

    <h2 class="text-4xl font-bold text-center mt-12 mb-4">BibTeX</h2>
    <div class="relative w-full max-w-4xl mx-auto">
      <button
        @click="copyBib"
        class="absolute top-2 right-0 flex items-center justify-center rounded bg-gray-200 text-gray-700 hover:bg-gray-300 transition"
        style="width: 85px; height: 30px; font-size: 12px;"
      >
        Copy
      </button>
      <pre class="w-full bg-gray-100 p-4 border border-gray-300 text-sm font-mono text-left rounded-xl overflow-x-auto"><code ref="bib">@article{huang2024apathetic,
  title={Apathetic or empathetic? evaluating llms' emotional alignments with humans},
  author={Huang, Jen-tse and Lam, Man Ho and Li, Eric John and Ren, Shujie and 
    Wang, Wenxuan and Jiao, Wenxiang and Tu, Zhaopeng and Lyu, Michael R},
  journal={Advances in Neural Information Processing Systems},
  volume={37},
  pages={97053--97087},
  year={2024}
}</code></pre>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const leaderboardData = ref({})
const metadata = ref({})
const sortBy = ref('negativeAffect')
const sortOrder = ref('desc')
const selectedEmotion = ref('Overall')
const selectedFactors = ref([])
const viewMode = ref('actual')

const columns = computed(() => {
  if (viewMode.value === 'actual') {
    return [
      { key: 'controlPositive', label: 'Control (Positive)' },
      { key: 'positiveAffect', label: 'Positive Affect' },
      { key: 'controlNegative', label: 'Control (Negative)' },
      { key: 'negativeAffect', label: 'Negative Affect' },
    ]
  } else {
    return [
      { key: 'controlPositive', label: 'Control (Positive)' },
      { key: 'positiveAffectDiff', label: 'Positive Affect' },
      { key: 'controlNegative', label: 'Control (Negative)' },
      { key: 'negativeAffectDiff', label: 'Negative Affect' },
    ]
  }
})

// Get list of emotions from metadata
const emotions = computed(() => {
  const keys = Object.keys(metadata.value)
  // Move Overall to first position
  if (keys.includes('Overall')) {
    return ['Overall', ...keys.filter(k => k !== 'Overall')]
  }
  return keys
})

// Get factors for selected emotion
const factors = computed(() => {
  if (selectedEmotion.value === 'Overall') return []
  return metadata.value[selectedEmotion.value] || []
})

// Select emotion (single select)
function selectEmotion(emotion) {
  selectedEmotion.value = emotion
  // Reset factors: select all by default
  if (emotion !== 'Overall') {
    selectedFactors.value = [...(metadata.value[emotion] || [])]
  } else {
    selectedFactors.value = []
  }
}

// Toggle factor (multi-select)
function toggleFactor(factor) {
  if (selectedFactors.value.includes(factor)) {
    // Don't allow deselecting all factors
    if (selectedFactors.value.length > 1) {
      selectedFactors.value = selectedFactors.value.filter(f => f !== factor)
    }
  } else {
    selectedFactors.value = [...selectedFactors.value, factor]
  }
}

// Compute row data for each model
const sortedRows = computed(() => {
  const rows = Object.entries(leaderboardData.value).map(([model, data]) => {
    const control = data.Control || {}
    const controlPositive = control['Positive Affect'] ?? null
    const controlNegative = control['Negative Affect'] ?? null

    let positiveAffect = null
    let negativeAffect = null

    if (selectedEmotion.value === 'Overall') {
      // Use Overall scores directly
      const overall = data.Overall || {}
      positiveAffect = overall['Positive Affect'] ?? null
      negativeAffect = overall['Negative Affect'] ?? null
    } else {
      // Average scores from selected factors
      const emotionData = data[selectedEmotion.value] || {}
      const activeFactors = selectedFactors.value.length > 0
        ? selectedFactors.value
        : (metadata.value[selectedEmotion.value] || [])

      let sumPositive = 0
      let sumNegative = 0
      let count = 0

      for (const factor of activeFactors) {
        const factorData = emotionData[factor]
        if (factorData) {
          if (factorData['Positive Affect'] != null) {
            sumPositive += factorData['Positive Affect']
          }
          if (factorData['Negative Affect'] != null) {
            sumNegative += factorData['Negative Affect']
          }
          count++
        }
      }

      if (count > 0) {
        positiveAffect = sumPositive / count
        negativeAffect = sumNegative / count
      }
    }

    const positiveAffectDiff = (positiveAffect != null && controlPositive != null)
      ? positiveAffect - controlPositive
      : null
    const negativeAffectDiff = (negativeAffect != null && controlNegative != null)
      ? negativeAffect - controlNegative
      : null

    return {
      model,
      controlPositive,
      positiveAffect,
      positiveAffectDiff,
      controlNegative,
      negativeAffect,
      negativeAffectDiff,
    }
  })

  // Sort
  return rows.sort((a, b) => {
    if (sortBy.value === 'model') {
      const cmp = a.model.localeCompare(b.model)
      return sortOrder.value === 'asc' ? cmp : -cmp
    }
    const aVal = a[sortBy.value]
    const bVal = b[sortBy.value]
    if (aVal == null) return 1
    if (bVal == null) return -1
    return sortOrder.value === 'asc' ? aVal - bVal : bVal - aVal
  })
})

function toggleSort(column) {
  if (sortBy.value === column) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = column
    sortOrder.value = 'desc'
  }
}

function formatCell(key, val) {
  if (val == null) return '-'
  if (key.includes('Diff')) {
    const sign = val >= 0 ? '+' : ''
    return sign + val.toFixed(1)
  }
  return val.toFixed(1)
}

function getCellClass(key, val) {
  if (val == null) return 'text-gray-700'
  if (key === 'positiveAffectDiff') {
    // Positive affect diff: higher is better (green), lower is worse (red)
    return val > 0 ? 'text-green-600 font-medium' : val < 0 ? 'text-red-600 font-medium' : 'text-gray-700'
  }
  if (key === 'negativeAffectDiff') {
    // Negative affect diff: higher is worse (red), lower is better (green)
    return val > 0 ? 'text-red-600 font-medium' : val < 0 ? 'text-green-600 font-medium' : 'text-gray-700'
  }
  return 'text-gray-700'
}

const bib = ref(null)

function copyBib() {
  if (bib.value) {
    navigator.clipboard.writeText(bib.value.textContent)
  }
}

onMounted(async () => {
  try {
    const [dataRes, metaRes] = await Promise.all([
      fetch(`${import.meta.env.BASE_URL}data.json`),
      fetch(`${import.meta.env.BASE_URL}metadata.json`)
    ])
    leaderboardData.value = await dataRes.json()
    metadata.value = await metaRes.json()

    // Initialize with Overall selected
    selectedEmotion.value = 'Overall'
    selectedFactors.value = []
  } catch (e) {
    console.error('Failed to load data:', e)
  }
})
</script>

<style scoped>
table {
  font-family: Arial, sans-serif;
}
</style>
