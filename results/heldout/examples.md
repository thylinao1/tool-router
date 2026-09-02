# Example outputs

Full traces from `Assistant.handle()` with the hybrid router (LLM = ollama).

## What's 12 squared plus 7?

```json
{
  "query": "What's 12 squared plus 7?",
  "routes": [
    "calculator"
  ],
  "steps": [
    {
      "step": "What's 12 squared plus 7?",
      "decision": {
        "route": "calculator",
        "confidence": 0.88,
        "reason": "matched math_verb, what_is_number for calculator (score 0.88)",
        "router": "hybrid(rules)",
        "candidates": [
          [
            "calculator",
            0.88
          ],
          [
            "weather",
            0.0
          ],
          [
            "web_search",
            0.0
          ],
          [
            "direct",
            0.0
          ]
        ],
        "vetoed": [],
        "abstained": false,
        "latency_ms": 0.389
      },
      "answer": "12 **2 + 7 = 151",
      "tool_ms": 3.464,
      "llm_ms": 0.0,
      "fallback": false,
      "asked_by": null
    }
  ],
  "answer": "12 **2 + 7 = 151",
  "latency_ms": {
    "routing": 0.389,
    "tool": 3.464,
    "llm": 0.0,
    "total": 4.001
  },
  "fallback": false,
  "llm": "ollama"
}
```

## Will it be windy in Cape Town tomorrow?

```json
{
  "query": "Will it be windy in Cape Town tomorrow?",
  "routes": [
    "weather"
  ],
  "steps": [
    {
      "step": "Will it be windy in Cape Town tomorrow?",
      "decision": {
        "route": "weather",
        "confidence": 0.85,
        "reason": "matched weather_word for weather (score 0.85)",
        "router": "hybrid(rules)",
        "candidates": [
          [
            "weather",
            0.85
          ],
          [
            "calculator",
            0.0
          ],
          [
            "web_search",
            0.0
          ],
          [
            "direct",
            0.0
          ]
        ],
        "vetoed": [],
        "abstained": false,
        "latency_ms": 0.126
      },
      "answer": "Weather in Cape Town: 23°C, sunny, humidity 78% (mock data)",
      "tool_ms": 0.125,
      "llm_ms": 0.0,
      "fallback": false,
      "asked_by": null
    }
  ],
  "answer": "Weather in Cape Town: 23°C, sunny, humidity 78% (mock data)",
  "latency_ms": {
    "routing": 0.126,
    "tool": 0.125,
    "llm": 0.0,
    "total": 0.309
  },
  "fallback": false,
  "llm": "ollama"
}
```

## Latest headlines about the Singapore general election

```json
{
  "query": "Latest headlines about the Singapore general election",
  "routes": [
    "web_search"
  ],
  "steps": [
    {
      "step": "Latest headlines about the Singapore general election",
      "decision": {
        "route": "web_search",
        "confidence": 0.722,
        "reason": "rules (0.70) and embeddings (0.74) both chose web_search",
        "router": "hybrid(agree)",
        "candidates": [
          [
            "web_search",
            0.35
          ],
          [
            "weather",
            0.244
          ],
          [
            "direct",
            0.097
          ],
          [
            "calculator",
            0.089
          ]
        ],
        "vetoed": [],
        "abstained": false,
        "latency_ms": 22.47
      },
      "answer": "Top result for 'Latest headlines about the Singapore general election' (mock search): no canned snippet; a real engine would return live pages here.",
      "tool_ms": 0.552,
      "llm_ms": 0.0,
      "fallback": false,
      "asked_by": null
    }
  ],
  "answer": "Top result for 'Latest headlines about the Singapore general election' (mock search): no canned snippet; a real engine would return live pages here.",
  "latency_ms": {
    "routing": 22.47,
    "tool": 0.552,
    "llm": 0.0,
    "total": 23.075
  },
  "fallback": false,
  "llm": "ollama"
}
```

## Explain the difference between supervised and unsupervised learning

```json
{
  "query": "Explain the difference between supervised and unsupervised learning",
  "routes": [
    "direct"
  ],
  "steps": [
    {
      "step": "Explain the difference between supervised and unsupervised learning",
      "decision": {
        "route": "direct",
        "confidence": 0.7,
        "reason": "embeddings abstained; matched explain for direct (score 0.70); vetoed calculator, weather",
        "router": "hybrid(rules-after-abstain)",
        "candidates": [
          [
            "direct",
            0.7
          ],
          [
            "calculator",
            0.0
          ],
          [
            "weather",
            0.0
          ],
          [
            "web_search",
            0.0
          ]
        ],
        "vetoed": [
          "calculator",
          "weather"
        ],
        "abstained": false,
        "latency_ms": 13.508
      },
      "answer": "Supervised learning involves training a model on labeled data, where the correct output is already known, to learn the relationship between inputs and outputs. In contrast, unsupervised learning involves training a model on unlabeled data, where the model must identify patterns or structure on its own. Supervised learning aims to minimize the error between predicted and actual outputs, while unsupervised learning aims to discover hidden patterns or relationships in the data. This fundamental difference in approach enables supervised learning to make precise predictions and unsupervised learning to uncover underlying structures.",
      "tool_ms": 0.0,
      "llm_ms": 3043.015,
      "fallback": false,
      "asked_by": null
    }
  ],
  "answer": "Supervised learning involves training a model on labeled data, where the correct output is already known, to learn the relationship between inputs and outputs. In contrast, unsupervised learning involves training a model on unlabeled data, where the model must identify patterns or structure on its own. Supervised learning aims to minimize the error between predicted and actual outputs, while unsupervised learning aims to discover hidden patterns or relationships in the data. This fundamental difference in approach enables supervised learning to make precise predictions and unsupervised learning to uncover underlying structures.",
  "latency_ms": {
    "routing": 13.508,
    "tool": 0.0,
    "llm": 3043.015,
    "total": 3056.654
  },
  "fallback": false,
  "llm": "ollama"
}
```

## Tell me a fun fact about octopuses

```json
{
  "query": "Tell me a fun fact about octopuses",
  "routes": [
    "direct"
  ],
  "steps": [
    {
      "step": "Tell me a fun fact about octopuses",
      "decision": {
        "route": "direct",
        "confidence": 0.443,
        "reason": "ambiguous, answering directly (neither router had any signal): rules chose direct (0.50), embeddings chose direct (0.44); top candidates direct and web_search are too close",
        "router": "hybrid(fallback)",
        "candidates": [
          [
            "direct",
            0.193
          ],
          [
            "web_search",
            0.141
          ],
          [
            "calculator",
            0.115
          ],
          [
            "weather",
            0.112
          ]
        ],
        "vetoed": [],
        "abstained": true,
        "latency_ms": 23.092
      },
      "answer": "Octopuses have three hearts, which pump blue-green blood through their bodies. Two of the hearts are branchial hearts that pump blood to their gills, while the third is a systemic heart that pumps blood to the rest of their body. This unique circulatory system allows them to efficiently oxygenate their bodies while also conserving energy. This adaptation is crucial for their ability to change color and texture to blend in with their surroundings.",
      "tool_ms": 0.0,
      "llm_ms": 2479.31,
      "fallback": false,
      "asked_by": null
    }
  ],
  "answer": "Octopuses have three hearts, which pump blue-green blood through their bodies. Two of the hearts are branchial hearts that pump blood to their gills, while the third is a systemic heart that pumps blood to the rest of their body. This unique circulatory system allows them to efficiently oxygenate their bodies while also conserving energy. This adaptation is crucial for their ability to change color and texture to blend in with their surroundings.",
  "latency_ms": {
    "routing": 23.092,
    "tool": 0.0,
    "llm": 2479.31,
    "total": 2502.467
  },
  "fallback": false,
  "llm": "ollama"
}
```
