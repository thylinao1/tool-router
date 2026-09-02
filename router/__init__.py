"""Tool router: decides whether a query needs a tool, and which one, without native LLM tool calling."""

from .schema import RoutingDecision, DIRECT, CLARIFY
from .tools import RouteSpec, ToolResult, ToolRegistry, build_default_registry
from .rules import RuleRouter
from .embeddings import EmbeddingRouter
from .classifier import ClassifierRouter
from .hybrid import HybridRouter
from .multistep import split_compound_query, route_with_steps
from .llm import OllamaLLM, MockLLM, get_llm
from .app import Assistant

__all__ = [
    "RoutingDecision", "DIRECT", "CLARIFY",
    "RouteSpec", "ToolResult", "ToolRegistry", "build_default_registry",
    "RuleRouter", "EmbeddingRouter", "ClassifierRouter", "HybridRouter",
    "split_compound_query", "route_with_steps",
    "OllamaLLM", "MockLLM", "get_llm",
    "Assistant",
]
