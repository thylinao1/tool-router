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
        "latency_ms": 0.155
      },
      "answer": "12 **2 + 7 = 151",
      "tool_ms": 1.689,
      "llm_ms": 0.0,
      "fallback": false
    }
  ],
  "answer": "12 **2 + 7 = 151",
  "latency_ms": {
    "routing": 0.155,
    "tool": 1.689,
    "llm": 0.0,
    "total": 1.971
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
        "latency_ms": 0.091
      },
      "answer": "Weather in Cape Town: 23°C, sunny, humidity 78% (mock data)",
      "tool_ms": 0.058,
      "llm_ms": 0.0,
      "fallback": false
    }
  ],
  "answer": "Weather in Cape Town: 23°C, sunny, humidity 78% (mock data)",
  "latency_ms": {
    "routing": 0.091,
    "tool": 0.058,
    "llm": 0.0,
    "total": 0.191
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
        "latency_ms": 12.306
      },
      "answer": "Top result for 'Latest headlines about the Singapore general election' (mock search): no canned snippet; a real engine would return live pages here.",
      "tool_ms": 0.453,
      "llm_ms": 0.0,
      "fallback": false
    }
  ],
  "answer": "Top result for 'Latest headlines about the Singapore general election' (mock search): no canned snippet; a real engine would return live pages here.",
  "latency_ms": {
    "routing": 12.306,
    "tool": 0.453,
    "llm": 0.0,
    "total": 12.799
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
        "reason": "embeddings abstained; matched explain for direct (score 0.70); vetoed weather",
        "router": "hybrid(rules)",
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
        "latency_ms": 9.129
      },
      "answer": "Supervised learning involves training a model on labeled data, where the correct output is already known, to learn a mapping between inputs and outputs. In contrast, unsupervised learning involves training a model on unlabeled data, where the model must discover patterns and relationships on its own. Supervised learning aims to minimize the error between predicted and actual outputs, while unsupervised learning aims to identify hidden structures or groupings in the data. This fundamental difference in approach leads to distinct applications and use cases for each type of learning.",
      "tool_ms": 0.0,
      "llm_ms": 3106.777,
      "fallback": false
    }
  ],
  "answer": "Supervised learning involves training a model on labeled data, where the correct output is already known, to learn a mapping between inputs and outputs. In contrast, unsupervised learning involves training a model on unlabeled data, where the model must discover patterns and relationships on its own. Supervised learning aims to minimize the error between predicted and actual outputs, while unsupervised learning aims to identify hidden structures or groupings in the data. This fundamental difference in approach leads to distinct applications and use cases for each type of learning.",
  "latency_ms": {
    "routing": 9.129,
    "tool": 0.0,
    "llm": 3106.777,
    "total": 3116.058
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
    "clarify"
  ],
  "steps": [
    {
      "step": "Tell me a fun fact about octopuses",
      "decision": {
        "route": "clarify",
        "confidence": 0.443,
        "reason": "rules chose direct (0.50), embeddings chose direct (0.44); top candidates direct and web_search are too close",
        "router": "hybrid(clarify)",
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
        "abstained": false,
        "latency_ms": 12.883
      },
      "answer": "I can help with that, but I am not sure whether you want a general answer from me or a web search for current information. Which one did you mean?",
      "tool_ms": 0.0,
      "llm_ms": 0.0,
      "fallback": false
    }
  ],
  "answer": "I can help with that, but I am not sure whether you want a general answer from me or a web search for current information. Which one did you mean?",
  "latency_ms": {
    "routing": 12.883,
    "tool": 0.0,
    "llm": 0.0,
    "total": 12.906
  },
  "fallback": false,
  "llm": "ollama"
}
```
