"""Visualization Agent — deterministic charts + LLM knowledge graph & mind map."""
from app.agents.base import BaseAgent
from app.agents.state import PipelineState
from app.prompts.templates import VISUALIZER_PROMPT, VISUALIZER_SYSTEM
from app.schemas.research import ChartSpec, GraphEdge, GraphNode, KnowledgeGraph
from app.utils.text import format_evidence
from app.visualizations.builder import build_data_charts, chart_aggregates_summary


class VisualizationAgent(BaseAgent):
    name = "visualizer"

    async def run(self, state: PipelineState) -> dict:
        docs = state.get("documents", [])
        data_charts = build_data_charts(docs)

        visuals: dict = {
            "charts": [c.model_dump() for c in data_charts],
            "knowledge_graph": KnowledgeGraph().model_dump(),
            "mindmap_mermaid": "",
        }

        try:
            raw = await self.ask_structured(
                VISUALIZER_PROMPT.format(
                    topic=state["topic"],
                    aggregates=chart_aggregates_summary(data_charts),
                    evidence=format_evidence(
                        state.get("context_blocks", []), docs, max_chars=8000
                    ),
                ),
                system=VISUALIZER_SYSTEM,
                max_tokens=4096,
            )
            visuals["knowledge_graph"] = self._validate_graph(
                raw.get("knowledge_graph", {})
            ).model_dump()
            visuals["mindmap_mermaid"] = raw.get("mindmap_mermaid", "") or ""
            for chart in raw.get("extra_charts", [])[:2]:
                try:
                    spec = ChartSpec(**chart)
                    if spec.id not in {c["id"] for c in visuals["charts"]}:
                        visuals["charts"].append(spec.model_dump())
                except Exception:
                    continue  # drop malformed LLM charts, keep the real ones
        except Exception as exc:
            # Visuals are enhancement, not core research — degrade gracefully.
            self.logger.error("visualizer.llm_failed", error=str(exc))

        self.logger.info(
            "visualizer.done",
            charts=len(visuals["charts"]),
            graph_nodes=len(visuals["knowledge_graph"]["nodes"]),
        )
        return {"visuals": visuals}

    @staticmethod
    def _validate_graph(raw: dict) -> KnowledgeGraph:
        nodes = []
        node_ids = set()
        for n in raw.get("nodes", [])[:20]:
            try:
                node = GraphNode(**n)
            except Exception:
                continue
            if node.id not in node_ids:
                node_ids.add(node.id)
                nodes.append(node)
        edges = []
        for e in raw.get("edges", [])[:40]:
            try:
                edge = GraphEdge(**e)
            except Exception:
                continue
            if edge.source in node_ids and edge.target in node_ids:
                edges.append(edge)
        return KnowledgeGraph(nodes=nodes, edges=edges)
