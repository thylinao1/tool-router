# Example outputs

Full traces from `Assistant.handle()` with the hybrid router (LLM = ollama).

## What is 245 * 18?

```json
{
  "query": "What is 245 * 18?",
  "routes": [
    "calculator"
  ],
  "steps": [
    {
      "step": "What is 245 * 18?",
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
        "latency_ms": 0.54
      },
      "answer": "245 * 18 = 4410",
      "tool_ms": 3.955,
      "llm_ms": 0.0,
      "fallback": false,
      "asked_by": null
    }
  ],
  "answer": "245 * 18 = 4410",
  "latency_ms": {
    "routing": 0.54,
    "tool": 3.955,
    "llm": 0.0,
    "total": 5.391
  },
  "fallback": false,
  "llm": "ollama"
}
```

## What is the weather in Singapore today?

```json
{
  "query": "What is the weather in Singapore today?",
  "routes": [
    "weather"
  ],
  "steps": [
    {
      "step": "What is the weather in Singapore today?",
      "decision": {
        "route": "weather",
        "confidence": 0.806,
        "reason": "rules (0.65) and embeddings (0.96) both chose weather",
        "router": "hybrid(agree)",
        "candidates": [
          [
            "weather",
            0.602
          ],
          [
            "web_search",
            0.289
          ],
          [
            "direct",
            0.256
          ],
          [
            "calculator",
            0.184
          ]
        ],
        "vetoed": [],
        "abstained": false,
        "latency_ms": 591.014
      },
      "answer": "Weather in Singapore: 31°C, thunderstorms, humidity 78% (mock data)",
      "tool_ms": 0.037,
      "llm_ms": 0.0,
      "fallback": false,
      "asked_by": null
    }
  ],
  "answer": "Weather in Singapore: 31°C, thunderstorms, humidity 78% (mock data)",
  "latency_ms": {
    "routing": 591.014,
    "tool": 0.037,
    "llm": 0.0,
    "total": 591.103
  },
  "fallback": false,
  "llm": "ollama"
}
```

## Who won the latest Formula 1 race?

```json
{
  "query": "Who won the latest Formula 1 race?",
  "routes": [
    "web_search"
  ],
  "steps": [
    {
      "step": "Who won the latest Formula 1 race?",
      "decision": {
        "route": "web_search",
        "confidence": 0.94,
        "reason": "matched recency, who_won for web_search (score 0.94)",
        "router": "hybrid(rules)",
        "candidates": [
          [
            "web_search",
            0.94
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
            "direct",
            0.0
          ]
        ],
        "vetoed": [],
        "abstained": false,
        "latency_ms": 0.055
      },
      "answer": "Top result for 'Who won the latest Formula 1 race?' (mock search): Formula 1: the most recent Grand Prix was won by the driver starting from pole; full results on formula1.com.",
      "tool_ms": 0.1,
      "llm_ms": 0.0,
      "fallback": false,
      "asked_by": null
    }
  ],
  "answer": "Top result for 'Who won the latest Formula 1 race?' (mock search): Formula 1: the most recent Grand Prix was won by the driver starting from pole; full results on formula1.com.",
  "latency_ms": {
    "routing": 0.055,
    "tool": 0.1,
    "llm": 0.0,
    "total": 0.172
  },
  "fallback": false,
  "llm": "ollama"
}
```

## Explain gradient descent.

```json
{
  "query": "Explain gradient descent.",
  "routes": [
    "direct"
  ],
  "steps": [
    {
      "step": "Explain gradient descent.",
      "decision": {
        "route": "direct",
        "confidence": 0.759,
        "reason": "rules (0.70) and embeddings (0.82) both chose direct",
        "router": "hybrid(agree)",
        "candidates": [
          [
            "direct",
            0.351
          ],
          [
            "calculator",
            0.203
          ],
          [
            "web_search",
            0.097
          ],
          [
            "weather",
            0.058
          ]
        ],
        "vetoed": [
          "calculator",
          "weather"
        ],
        "abstained": false,
        "latency_ms": 10.189
      },
      "answer": "Gradient descent is an optimization algorithm used to minimize the cost function of a machine learning model. It iteratively updates the model's parameters in the direction of the negative gradient of the cost function, which is a measure of how well the model is performing. The update rule is typically given by: `w_new = w_old - α * ∇(cost function)`, where `α` is the learning rate and `w_old` is the previous parameter value. By iteratively applying this update rule, the model's parameters converge to a minimum of the cost function.",
      "tool_ms": 0.0,
      "llm_ms": 3569.359,
      "fallback": false,
      "asked_by": null
    }
  ],
  "answer": "Gradient descent is an optimization algorithm used to minimize the cost function of a machine learning model. It iteratively updates the model's parameters in the direction of the negative gradient of the cost function, which is a measure of how well the model is performing. The update rule is typically given by: `w_new = w_old - α * ∇(cost function)`, where `α` is the learning rate and `w_old` is the previous parameter value. By iteratively applying this update rule, the model's parameters converge to a minimum of the cost function.",
  "latency_ms": {
    "routing": 10.189,
    "tool": 0.0,
    "llm": 3569.359,
    "total": 3579.942
  },
  "fallback": false,
  "llm": "ollama"
}
```

## Write a haiku about rain

```json
{
  "query": "Write a haiku about rain",
  "routes": [
    "direct"
  ],
  "steps": [
    {
      "step": "Write a haiku about rain",
      "decision": {
        "route": "direct",
        "confidence": 0.8,
        "reason": "matched creative for direct (score 0.80); vetoed weather",
        "router": "hybrid(rules)",
        "candidates": [
          [
            "direct",
            0.8
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
        "latency_ms": 0.171
      },
      "answer": "Raindrops on my face\nCooling skin with gentle touch\nNature's soothing song",
      "tool_ms": 0.0,
      "llm_ms": 587.411,
      "fallback": false,
      "asked_by": null
    }
  ],
  "answer": "Raindrops on my face\nCooling skin with gentle touch\nNature's soothing song",
  "latency_ms": {
    "routing": 0.171,
    "tool": 0.0,
    "llm": 587.411,
    "total": 587.75
  },
  "fallback": false,
  "llm": "ollama"
}
```

## How many days until Christmas?

```json
{
  "query": "How many days until Christmas?",
  "routes": [
    "clarify"
  ],
  "steps": [
    {
      "step": "How many days until Christmas?",
      "decision": {
        "route": "clarify",
        "confidence": 0.522,
        "reason": "rules chose direct (0.50), embeddings chose weather (0.52); top candidates weather and web_search are too close",
        "router": "hybrid(clarify)",
        "candidates": [
          [
            "weather",
            0.321
          ],
          [
            "web_search",
            0.259
          ],
          [
            "calculator",
            0.215
          ],
          [
            "direct",
            0.189
          ]
        ],
        "vetoed": [],
        "abstained": false,
        "latency_ms": 22.731
      },
      "answer": "I can help with that, but I am not sure whether you want a weather report for a location or a web search for current information. Which one did you mean?",
      "tool_ms": 0.0,
      "llm_ms": 0.0,
      "fallback": false,
      "asked_by": "router"
    }
  ],
  "answer": "I can help with that, but I am not sure whether you want a weather report for a location or a web search for current information. Which one did you mean?",
  "latency_ms": {
    "routing": 22.731,
    "tool": 0.0,
    "llm": 0.0,
    "total": 23.054
  },
  "fallback": false,
  "llm": "ollama"
}
```

## Temperature

```json
{
  "query": "Temperature",
  "routes": [
    "weather"
  ],
  "steps": [
    {
      "step": "Temperature",
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
        "latency_ms": 0.026
      },
      "answer": "Which location would you like the weather for?",
      "tool_ms": 0.021,
      "llm_ms": 0.0,
      "fallback": false,
      "asked_by": "tool"
    }
  ],
  "answer": "Which location would you like the weather for?",
  "latency_ms": {
    "routing": 0.026,
    "tool": 0.021,
    "llm": 0.0,
    "total": 0.062
  },
  "fallback": false,
  "llm": "ollama"
}
```

## What's happening?

```json
{
  "query": "What's happening?",
  "routes": [
    "direct"
  ],
  "steps": [
    {
      "step": "What's happening?",
      "decision": {
        "route": "direct",
        "confidence": 0.5,
        "reason": "ambiguous, answering directly (neither router had any signal): rules chose direct (0.50), embeddings chose web_search (0.50); top candidates web_search and weather are too close",
        "router": "hybrid(fallback)",
        "candidates": [
          [
            "web_search",
            0.275
          ],
          [
            "weather",
            0.197
          ],
          [
            "direct",
            0.161
          ],
          [
            "calculator",
            0.097
          ]
        ],
        "vetoed": [],
        "abstained": true,
        "latency_ms": 11.512
      },
      "answer": "I'm here to provide information and assist with your questions. I'm a concise assistant, and I'll do my best to provide clear and concise answers. What's on your mind, and how can I help you today?",
      "tool_ms": 0.0,
      "llm_ms": 1478.071,
      "fallback": false,
      "asked_by": null
    }
  ],
  "answer": "I'm here to provide information and assist with your questions. I'm a concise assistant, and I'll do my best to provide clear and concise answers. What's on your mind, and how can I help you today?",
  "latency_ms": {
    "routing": 11.512,
    "tool": 0.0,
    "llm": 1478.071,
    "total": 1490.191
  },
  "fallback": false,
  "llm": "ollama"
}
```

## What's the weather in Tokyo and what is 12 * 7?

```json
{
  "query": "What's the weather in Tokyo and what is 12 * 7?",
  "routes": [
    "weather",
    "calculator"
  ],
  "steps": [
    {
      "step": "What's the weather in Tokyo",
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
        "latency_ms": 0.089
      },
      "answer": "Weather in Tokyo: 26°C, partly cloudy, humidity 60% (mock data)",
      "tool_ms": 0.14,
      "llm_ms": 0.0,
      "fallback": false,
      "asked_by": null
    },
    {
      "step": "what is 12 * 7",
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
        "latency_ms": 0.049
      },
      "answer": "12 * 7 = 84",
      "tool_ms": 5.207,
      "llm_ms": 0.0,
      "fallback": false,
      "asked_by": null
    }
  ],
  "answer": "Weather in Tokyo: 26°C, partly cloudy, humidity 60% (mock data)\n12 * 7 = 84",
  "latency_ms": {
    "routing": 0.138,
    "tool": 5.347,
    "llm": 0.0,
    "total": 5.724
  },
  "fallback": false,
  "llm": "ollama"
}
```
