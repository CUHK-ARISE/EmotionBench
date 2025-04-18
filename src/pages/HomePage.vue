<template>
  <main class="p-8">
    <h2 class="text-4xl font-bold text-center mt-12 mb-4">Introduction</h2>
    <p class="text-md text-gray-700 max-w-4xl mx-auto leading-relaxed text-justify"
    v-html="introductionHTML"
    ></p>
    <br>
    <!-- <h2 class="text-4xl font-bold text-center mt-12 mb-4">Perturbation Strategies</h2> -->
    <div class="flex justify-center">
      <img
      src="/Execution_Flow.png"
      alt="Execution Flow Diagram"
      class="rounded-xl max-w-5xl w-900px"
      />
    </div>

    <p class="text-md text-gray-700 max-w-4xl mx-auto leading-relaxed text-justify">
      {{ execution_flow_caption }}
    </p>

    <h2 class="text-4xl font-bold text-center mt-12 mb-4">Experimental Results (Direct Inference)</h2>
    <div class="flex justify-center">
      <img
      src="/Results_Direct.png"
      alt="Results Direct"
      class="rounded-xl max-w-5xl w-900px"
      />
    </div>
    <p class="text-md text-gray-700 max-w-4xl mx-auto leading-relaxed text-justify"
    v-html="findingsHTML"
    ></p>

    <h2 class="text-4xl font-bold text-center mt-12 mb-4">Direct Inference v.s. CoT Prompting</h2>
    <div class="flex justify-center">
      <img
      src="/CoT.png"
      alt="CoT Prompting"
      class="rounded-xl max-w-5xl w-900px"
      />
    </div>
    <p class="text-md text-gray-700 max-w-4xl mx-auto leading-relaxed text-justify"
    v-html="cotHTML"
    ></p>

    <h2 class="text-4xl font-bold text-center mt-12 mb-4">Reasoning Collapse in QwQ-32B</h2>
    <div class="flex justify-center items-center gap-6 flex-wrap">
      <img
        src="/CS4-Confusion-Trend.png"
        alt="CS4-Confusion-Trend"
        class="max-w-md w-full sm:w-[400px]"
      />
      <img
        src="/CS4-Stages.png"
        alt="CS4-Stages"
        class="max-w-md w-full sm:w-[600px]"
      />
    </div>

    <p class="text-md text-gray-700 max-w-4xl mx-auto leading-relaxed text-justify"
    v-html="collapseHTML"
    ></p>

    <h2 class="text-4xl font-bold text-center mt-12 mb-4">BibTex</h2>
    <div class="relative max-w-4xl mx-auto mt-8">
      <button
        @click="copyBib"
        class="absolute top-2 right-2 text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded hover:bg-gray-300 transition"
      >
        📋 Copy
      </button>
      <pre class="bg-gray-100 p-4 border border-gray-300 text-sm font-mono text-left rounded-xl overflow-x-auto"><code ref="bib">
@article{lam2025codecrash,
  title={CodeCrash: Stress Testing LLM Reasoning under Structural and Semantic Perturbations},
  author={Man Ho, Lam and Chaozheng, Wang and Jen-tse Huang and Michael R., Lyu},
  journal={arXiv preprint arXiv:-},
  year={2025}
}</code></pre>
    </div>

  </main>
</template>

<script setup>
const introductionHTML = `
<b>CodeCrash</b> is a unified and stress-testing benchmark for evaluating the robustness of Large Language Models (LLMs) in code reasoning.
Unlike prior work focusing on prompt variations, CodeCrash targets deeper comprehension by applying logic-preserving structural changes and misleading textual cues to real code.
We systematically perturb two established benchmarks —
<a href="https://arxiv.org/abs/2401.03065" class="text-blue-600 hover:underline font-medium" target="_blank" rel="noopener">CRUXEval</a>
and
<a href="https://arxiv.org/abs/2403.07974" class="text-blue-600 hover:underline font-medium" target="_blank" rel="noopener">LiveCodeBench</a>
— with controlled distractions, and evaluate 17 LLMs across input prediction and code execution tasks.
CodeCrash reveals key failure modes in modern LLMs, including overreliance on natural language cues and reasoning collapse in large reasoning models.
`

const execution_flow_caption = "CodeCrash Pipeline. Original code is standardized, perturbed, validated, and then passed to LLMs for evaluation. Structural and textual perturbations include renaming, reformatting, garbage code insertion, and misleading NL cues."

const findingsHTML = `
<b>CodeCrash</b> reveals that LLMs exhibit an <b>inherent reliance on natural language (NL) cues</b>, such as identifiers, comments, and embedded hints, often prioritizing them over actual program logic.
Structural perturbations like renaming and garbage code disrupt reasoning, while misleading textual cues lead to substantial performance degradation.
Models also demonstrate an <b>internal cognitive preference</b> toward specific NL formats: some are more vulnerable to misleading comments, others to print statements.
This behavior remains consistent across datasets, indicating a hidden bias rooted in model architecture or pretraining corpora.
`

const cotHTML = `
CoT prompting improves LLM robustness by guiding step-by-step reasoning, with gains up to <b>13.57pp</b> on MHC.
It helps models focus on code semantics and reduces overthinking, especially in high-capacity models like GPT-4o.
However, <b>CoT does not fully eliminate reliance on NL cues</b>, and smaller models remain vulnerable—especially to MPS.
`

const collapseHTML = `
We uncover a critical vulnerability in Large Reasoning Models: when facing plausible but incorrect hints, models may enter a <b>recursive self-reflection loop</b>, repeatedly doubting their reasoning.
In one case, QwQ-32B generated over <b>32,000 tokens</b>, including 12,000+ repeated "<code>Hmm</code>", after gradually shifting from correct logic to hallucinatory brute-force enumeration.
By tracking confusion words, we observed a <b>quadratic increase</b> in uncertainty before collapse, confirming progressive instability once misleading hints are introduced.
`


</script>

<style scoped>

</style>