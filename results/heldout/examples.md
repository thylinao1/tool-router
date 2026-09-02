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
        "latency_ms": 0.201
      },
      "answer": "12 **2 + 7 = 151",
      "tool_ms": 4.397,
      "llm_ms": 0.0,
      "fallback": false,
      "asked_by": null,
      "dependency": null
    }
  ],
  "answer": "12 **2 + 7 = 151",
  "latency_ms": {
    "routing": 0.201,
    "tool": 4.397,
    "llm": 0.0,
    "total": 4.747
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
        "latency_ms": 0.125
      },
      "answer": "Weather in Cape Town: 23°C, sunny, humidity 78% (mock data)",
      "tool_ms": 0.117,
      "llm_ms": 0.0,
      "fallback": false,
      "asked_by": null,
      "dependency": null
    }
  ],
  "answer": "Weather in Cape Town: 23°C, sunny, humidity 78% (mock data)",
  "latency_ms": {
    "routing": 0.125,
    "tool": 0.117,
    "llm": 0.0,
    "total": 0.3
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
        "latency_ms": 19.379
      },
      "answer": "No canned snippet; a real engine would return live pages here (mock search for 'Latest headlines about the Singapore general election').",
      "tool_ms": 0.533,
      "llm_ms": 0.0,
      "fallback": false,
      "asked_by": null,
      "dependency": null
    }
  ],
  "answer": "No canned snippet; a real engine would return live pages here (mock search for 'Latest headlines about the Singapore general election').",
  "latency_ms": {
    "routing": 19.379,
    "tool": 0.533,
    "llm": 0.0,
    "total": 19.965
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
        "latency_ms": 12.552
      },
      "answer": "Supervised learning involves training a model on labeled data, where the correct output is already known, and the goal is to learn a mapping between inputs and outputs. In contrast, unsupervised learning involves training a model on unlabeled data, where the goal is to identify patterns or structure in the data without a predefined output. Supervised learning typically results in more accurate models, but requires more labeled data, while unsupervised learning can discover new insights and relationships. Unsupervised learning often requires more creativity and domain expertise to design effective algorithms.",
      "tool_ms": 0.0,
      "llm_ms": 3078.315,
      "fallback": false,
      "asked_by": null,
      "dependency": null
    }
  ],
  "answer": "Supervised learning involves training a model on labeled data, where the correct output is already known, and the goal is to learn a mapping between inputs and outputs. In contrast, unsupervised learning involves training a model on unlabeled data, where the goal is to identify patterns or structure in the data without a predefined output. Supervised learning typically results in more accurate models, but requires more labeled data, while unsupervised learning can discover new insights and relationships. Unsupervised learning often requires more creativity and domain expertise to design effective algorithms.",
  "latency_ms": {
    "routing": 12.552,
    "tool": 0.0,
    "llm": 3078.315,
    "total": 3090.939
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
        "latency_ms": 19.873
      },
      "answer": "Octopuses have three hearts, two of which pump blood to their gills, while the third pumps blood to the rest of their body. This unique circulatory system allows them to efficiently pump blood to their entire body, including their arms, which require a constant supply of oxygen. Additionally, octopuses can also change the color and texture of their skin to blend in with their surroundings, making them expert camouflage artists.",
      "tool_ms": 0.0,
      "llm_ms": 2444.121,
      "fallback": false,
      "asked_by": null,
      "dependency": null
    }
  ],
  "answer": "Octopuses have three hearts, two of which pump blood to their gills, while the third pumps blood to the rest of their body. This unique circulatory system allows them to efficiently pump blood to their entire body, including their arms, which require a constant supply of oxygen. Additionally, octopuses can also change the color and texture of their skin to blend in with their surroundings, making them expert camouflage artists.",
  "latency_ms": {
    "routing": 19.873,
    "tool": 0.0,
    "llm": 2444.121,
    "total": 2464.406
  },
  "fallback": false,
  "llm": "ollama"
}
```
