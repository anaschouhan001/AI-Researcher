"use client";

import { useMemo } from "react";
import ReactFlow, {
  Background,
  BackgroundVariant,
  Controls,
  MarkerType,
  type Edge,
  type Node,
} from "reactflow";
import "reactflow/dist/style.css";
import { Network } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { KnowledgeGraph as KnowledgeGraphData } from "@/lib/types";

/** Validated categorical palette (dark surface) — one hue per entity group. */
const GROUP_COLORS = [
  "#e0447f",
  "#9d5ce6",
  "#e08a3c",
  "#3c9bd6",
  "#c93cb0",
  "#5cb85c",
  "#e06666",
  "#8a6d3b",
] as const;

export interface KnowledgeGraphProps {
  graph: KnowledgeGraphData;
}

export default function KnowledgeGraphView({ graph }: KnowledgeGraphProps) {
  const { nodes, edges, groups } = useMemo(() => {
    const uniqueGroups = Array.from(new Set(graph.nodes.map((n) => n.group)));
    const groupColor = new Map<string, string>(
      uniqueGroups.map((g, i) => [g, GROUP_COLORS[i % GROUP_COLORS.length]])
    );

    const count = graph.nodes.length;
    const radius = Math.max(220, count * 34);

    const flowNodes: Node[] = graph.nodes.map((node, i) => {
      const angle = (2 * Math.PI * i) / Math.max(count, 1) - Math.PI / 2;
      const color = groupColor.get(node.group) ?? GROUP_COLORS[0];
      return {
        id: node.id,
        position: {
          x: radius * Math.cos(angle),
          y: radius * Math.sin(angle),
        },
        data: { label: node.label },
        style: {
          background: "#ffffff",
          color: "#7d1a43",
          border: `1.5px solid ${color}`,
          borderRadius: 16,
          fontSize: 12,
          padding: "6px 10px",
          boxShadow: `0 0 14px ${color}22`,
          maxWidth: 180,
        },
      };
    });

    const flowEdges: Edge[] = graph.edges.map((edge, i) => ({
      id: `edge-${edge.source}-${edge.target}-${i}`,
      source: edge.source,
      target: edge.target,
      label: edge.label || undefined,
      type: "default",
      style: { stroke: "rgba(224, 68, 127, 0.35)", strokeWidth: 1.5 },
      labelStyle: { fill: "#b45580", fontSize: 10 },
      labelBgStyle: { fill: "#fff0f6", fillOpacity: 0.9 },
      labelBgPadding: [4, 2] as [number, number],
      labelBgBorderRadius: 4,
      markerEnd: { type: MarkerType.ArrowClosed, color: "rgba(224, 68, 127, 0.5)" },
    }));

    return {
      nodes: flowNodes,
      edges: flowEdges,
      groups: uniqueGroups.map((g) => ({
        name: g,
        color: groupColor.get(g) ?? GROUP_COLORS[0],
      })),
    };
  }, [graph]);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-sm">
          <Network className="h-4 w-4 text-pink-400" aria-hidden="true" />
          Knowledge graph
        </CardTitle>
      </CardHeader>
      <CardContent>
        {graph.nodes.length === 0 ? (
          <p className="text-sm text-pink-400">No knowledge graph was generated.</p>
        ) : (
          <>
            <div className="h-[480px] overflow-hidden rounded-2xl border-2 border-pink-200 bg-pink-50/60">
              <ReactFlow
                nodes={nodes}
                edges={edges}
                fitView
                fitViewOptions={{ padding: 0.15 }}
                minZoom={0.2}
                maxZoom={2}
                proOptions={{ hideAttribution: false }}
                nodesConnectable={false}
              >
                <Background
                  variant={BackgroundVariant.Dots}
                  color="rgba(244, 114, 182, 0.3)"
                  gap={22}
                  size={1}
                />
                <Controls showInteractive={false} />
              </ReactFlow>
            </div>
            {groups.length > 0 && (
              <ul className="mt-3 flex flex-wrap gap-x-4 gap-y-1.5" aria-label="Entity groups">
                {groups.map((group) => (
                  <li key={group.name} className="flex items-center gap-1.5 text-xs text-pink-500">
                    <span
                      className="h-2.5 w-2.5 rounded-full"
                      style={{ backgroundColor: group.color }}
                      aria-hidden="true"
                    />
                    {group.name}
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
