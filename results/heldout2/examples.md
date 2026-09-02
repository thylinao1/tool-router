# Example outputs

Full traces from `Assistant.handle()` with the hybrid router (LLM = ollama).

## What's 81 divided by 9 plus 4?

```json
{
  "query": "What's 81 divided by 9 plus 4?",
  "routes": [
    "calculator"
  ],
  "steps": [
    {
      "step": "What's 81 divided by 9 plus 4?",
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
        "latency_ms": 0.139
      },
      "answer": "81 / 9 + 4 = 13",
      "tool_ms": 2.358,
      "llm_ms": 0.0,
      "fallback": false,
      "asked_by": null
    }
  ],
  "answer": "81 / 9 + 4 = 13",
  "latency_ms": {
    "routing": 0.139,
    "tool": 2.358,
    "llm": 0.0,
    "total": 2.602
  },
  "fallback": false,
  "llm": "ollama"
}
```

## Umbrella needed in Manila tomorrow?

```json
{
  "query": "Umbrella needed in Manila tomorrow?",
  "routes": [
    "weather"
  ],
  "steps": [
    {
      "step": "Umbrella needed in Manila tomorrow?",
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
        "latency_ms": 0.205
      },
      "answer": "Weather in Manila: 25°C, light rain, humidity 80% (mock data)",
      "tool_ms": 0.101,
      "llm_ms": 0.0,
      "fallback": false,
      "asked_by": null
    }
  ],
  "answer": "Weather in Manila: 25°C, light rain, humidity 80% (mock data)",
  "latency_ms": {
    "routing": 0.205,
    "tool": 0.101,
    "llm": 0.0,
    "total": 0.531
  },
  "fallback": false,
  "llm": "ollama"
}
```

## Who is leading the Premier League right now?

```json
{
  "query": "Who is leading the Premier League right now?",
  "routes": [
    "web_search"
  ],
  "steps": [
    {
      "step": "Who is leading the Premier League right now?",
      "decision": {
        "route": "web_search",
        "confidence": 0.663,
        "reason": "rules (0.40) and embeddings (0.93) both chose web_search",
        "router": "hybrid(agree)",
        "candidates": [
          [
            "web_search",
            0.476
          ],
          [
            "weather",
            0.248
          ],
          [
            "direct",
            0.147
          ],
          [
            "calculator",
            0.077
          ]
        ],
        "vetoed": [],
        "abstained": false,
        "latency_ms": 24.585
      },
      "answer": "Top result for 'Who is leading the Premier League right now?' (mock search): no canned snippet; a real engine would return live pages here.",
      "tool_ms": 0.562,
      "llm_ms": 0.0,
      "fallback": false,
      "asked_by": null
    }
  ],
  "answer": "Top result for 'Who is leading the Premier League right now?' (mock search): no canned snippet; a real engine would return live pages here.",
  "latency_ms": {
    "routing": 24.585,
    "tool": 0.562,
    "llm": 0.0,
    "total": 25.196
  },
  "fallback": false,
  "llm": "ollama"
}
```

## Describe how a transformer model works

```json
{
  "query": "Describe how a transformer model works",
  "routes": [
    "direct"
  ],
  "steps": [
    {
      "step": "Describe how a transformer model works",
      "decision": {
        "route": "direct",
        "confidence": 0.7,
        "reason": "embeddings abstained; matched explain for direct (score 0.70); vetoed weather",
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
          "weather"
        ],
        "abstained": false,
        "latency_ms": 11.153
      },
      "answer": "A transformer model is a type of neural network architecture that uses self-attention mechanisms to process sequential data, such as text or images. It consists of an encoder and a decoder, where the encoder takes in input data and generates a sequence of vectors, and the decoder takes these vectors and generates the final output. The self-attention mechanism allows the model to weigh the importance of different input elements relative to each other, enabling it to capture long-range dependencies and relationships. This allows the model to learn complex patterns and relationships in the input data.",
      "tool_ms": 0.0,
      "llm_ms": 3067.824,
      "fallback": false,
      "asked_by": null
    }
  ],
  "answer": "A transformer model is a type of neural network architecture that uses self-attention mechanisms to process sequential data, such as text or images. It consists of an encoder and a decoder, where the encoder takes in input data and generates a sequence of vectors, and the decoder takes these vectors and generates the final output. The self-attention mechanism allows the model to weigh the importance of different input elements relative to each other, enabling it to capture long-range dependencies and relationships. This allows the model to learn complex patterns and relationships in the input data.",
  "latency_ms": {
    "routing": 11.153,
    "tool": 0.0,
    "llm": 3067.824,
    "total": 3079.196
  },
  "fallback": false,
  "llm": "ollama"
}
```

## Is it sunny in Lisbon and what's 9 * 9?

```json
{
  "query": "Is it sunny in Lisbon and what's 9 * 9?",
  "routes": [
    "weather",
    "calculator"
  ],
  "steps": [
    {
      "step": "Is it sunny in Lisbon",
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
        "latency_ms": 0.082
      },
      "answer": "Weather in Lisbon: 19°C, light rain, humidity 74% (mock data)",
      "tool_ms": 0.18,
      "llm_ms": 0.0,
      "fallback": false,
      "asked_by": null
    },
    {
      "step": "what's 9 * 9",
      "decision": {
        "route": "calculator",
        "confidence": 0.98,
        "reason": "matched arithmetic_expression, what_is_number for calculator (score 0.98)",
        "router": "hybrid(rules)",
        "candidates": [
          [
            "calculator",
            0.98
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
        "latency_ms": 0.061
      },
      "answer": "9 * 9 = 81",
      "tool_ms": 0.521,
      "llm_ms": 0.0,
      "fallback": false,
      "asked_by": null
    }
  ],
  "answer": "Weather in Lisbon: 19°C, light rain, humidity 74% (mock data)\n9 * 9 = 81",
  "latency_ms": {
    "routing": 0.143,
    "tool": 0.701,
    "llm": 0.0,
    "total": 0.959
  },
  "fallback": false,
  "llm": "ollama"
}
```
