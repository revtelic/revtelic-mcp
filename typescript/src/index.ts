/**
 * Revtelic MCP Stdio Server
 *
 * Runs an official Model Context Protocol server over stdio for:
 * - Claude Desktop
 * - Cursor
 * - Windsurf
 * - Antigravity / Any MCP Host
 */

declare const process: any;
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { RevtelicClient } from "./client.js";

const client = new RevtelicClient();

function formatAnalysisMarkdown(analysis: any): string {
  const score = analysis.health_score ?? analysis.score ?? 50;
  const status =
    score >= 75 ? "🟢 Strong / Healthy" : score >= 50 ? "🟡 Slipping / At Risk" : "🔴 Critical / Stalled";

  let md = `# 🎯 Revtelic Deal Health Intelligence: ${analysis.name || "Sales Opportunity"}\n\n`;
  md += `**Deal Health Score**: **${score}/100** — *${status}*\n\n`;

  if (analysis.brutal_truth) {
    md += `### 💥 Brutal Truth\n${analysis.brutal_truth}\n\n`;
  }

  if (Array.isArray(analysis.risks) && analysis.risks.length > 0) {
    md += `### ⚠️ Key Deal Risks\n`;
    for (const r of analysis.risks) {
      if (typeof r === "string") {
        md += `- ${r}\n`;
      } else if (r && typeof r === "object") {
        const sev = r.severity ? `[${r.severity.toUpperCase()}] ` : "";
        md += `- **${sev}${r.type || "Risk"}**: ${r.description || JSON.stringify(r)}\n`;
        if (r.mitigation) md += `  - *Mitigation*: ${r.mitigation}\n`;
      }
    }
    md += "\n";
  }

  if (Array.isArray(analysis.stakeholders) && analysis.stakeholders.length > 0) {
    md += `### 👥 Stakeholder Map\n`;
    for (const s of analysis.stakeholders) {
      if (typeof s === "string") {
        md += `- ${s}\n`;
      } else if (s && typeof s === "object") {
        const role = s.role ? ` (${s.role})` : "";
        const sentiment = s.sentiment ? ` [${s.sentiment}]` : "";
        const eb = s.is_economic_buyer ? " ⭐ *Economic Buyer*" : "";
        md += `- **${s.name}**${role}${sentiment}${eb}\n`;
      }
    }
    md += "\n";
  }

  if (analysis.next_best_action) {
    md += `### 🚀 Next Best Action\n`;
    if (typeof analysis.next_best_action === "string") {
      md += `${analysis.next_best_action}\n\n`;
    } else {
      md += `**Action**: ${analysis.next_best_action.action}\n`;
      if (analysis.next_best_action.rationale) {
        md += `*Rationale*: ${analysis.next_best_action.rationale}\n`;
      }
      md += "\n";
    }
  }

  if (analysis.one_pager_url) {
    md += `---\n`;
    md += `📊 **Interactive Deal One-Pager**: [Open Dealboard in Revtelic](${analysis.one_pager_url})\n`;
    md += `*(Collaborate, share with buyers as a Mutual Action Plan, or claim to your workspace)*\n`;
  }

  return md;
}

const TOOLS: Tool[] = [
  {
    name: "analyze_deal",
    description:
      "Analyse a raw B2B sales call transcript, meeting notes, sales conversation, or email thread and produce a Revtelic Deal Health Intelligence assessment. Returns 0-100 deal health, buyer commitment, brutal truth, hidden risks, stakeholder intelligence, next best action, and an interactive Deal One-Pager URL. Open for zero-friction analysis without requiring an account or API key.",
    inputSchema: {
      type: "object",
      properties: {
        transcript: {
          type: "string",
          description: "Raw sales meeting transcript, call notes, or email thread to evaluate",
        },
        name: {
          type: "string",
          description: "Optional company or deal name (e.g. 'Stripe Renewal' or 'Acme Corp')",
        },
      },
      required: ["transcript"],
    },
  },
  {
    name: "get_deal_health",
    description:
      "Assess the health of a saved B2B sales opportunity using Revtelic Deal Intelligence and return a 0–100 health score with the reasons behind it. Requires Revtelic account or REVTELIC_API_KEY.",
    inputSchema: {
      type: "object",
      properties: {
        deal_id: {
          type: "string",
          description: "ID or slug of the saved dealboard in Revtelic",
        },
      },
      required: ["deal_id"],
    },
  },
  {
    name: "get_deal_risks",
    description:
      "Identify hidden and explicit blockers, technical risks, timing delays, and qualification gaps that could kill a saved sales deal. Requires Revtelic account or REVTELIC_API_KEY.",
    inputSchema: {
      type: "object",
      properties: {
        deal_id: {
          type: "string",
          description: "ID or slug of the saved dealboard in Revtelic",
        },
      },
      required: ["deal_id"],
    },
  },
  {
    name: "get_stakeholders",
    description:
      "Analyse buyer champions, economic buyer engagement, technical evaluators, and missing decision makers for a saved deal. Requires Revtelic account or REVTELIC_API_KEY.",
    inputSchema: {
      type: "object",
      properties: {
        deal_id: {
          type: "string",
          description: "ID or slug of the saved dealboard in Revtelic",
        },
      },
      required: ["deal_id"],
    },
  },
  {
    name: "get_next_best_action",
    description:
      "Determine the single highest-priority action the seller should take next to unblock, progress, or close a saved deal. Requires Revtelic account or REVTELIC_API_KEY.",
    inputSchema: {
      type: "object",
      properties: {
        deal_id: {
          type: "string",
          description: "ID or slug of the saved dealboard in Revtelic",
        },
      },
      required: ["deal_id"],
    },
  },
  {
    name: "list_deals",
    description:
      "List active deals and dealboards from your connected Revtelic workspace. Requires Revtelic account or REVTELIC_API_KEY.",
    inputSchema: {
      type: "object",
      properties: {
        search: {
          type: "string",
          description: "Optional search query to filter deals by company or buyer name",
        },
        limit: {
          type: "number",
          description: "Max number of deals to return (default: 20)",
        },
      },
    },
  },
];

export function runServer() {
  const server = new Server(
    {
      name: "revtelic-mcp",
      version: "1.0.0",
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return { tools: TOOLS };
  });

  server.setRequestHandler(CallToolRequestSchema, async (request: any) => {
    const { name, arguments: args = {} } = request.params;

    try {
      switch (name) {
        case "analyze_deal": {
          const transcript = String(args.transcript || "").trim();
          if (!transcript) {
            return {
              isError: true,
              content: [{ type: "text", text: "Error: 'transcript' argument is required." }],
            };
          }
          const analysis = await client.analyzeDeal({
            transcript,
            name: args.name ? String(args.name) : undefined,
          });

          const markdown = formatAnalysisMarkdown(analysis);
          return {
            content: [
              {
                type: "text",
                text: `${markdown}\n\n\`\`\`json\n${JSON.stringify(analysis, null, 2)}\n\`\`\``,
              },
            ],
          };
        }

        case "get_deal_health": {
          const dealId = String(args.deal_id || "").trim();
          if (!dealId) {
            return { isError: true, content: [{ type: "text", text: "Error: 'deal_id' is required." }] };
          }
          const result = await client.getDealHealth(dealId);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        }

        case "get_deal_risks": {
          const dealId = String(args.deal_id || "").trim();
          if (!dealId) {
            return { isError: true, content: [{ type: "text", text: "Error: 'deal_id' is required." }] };
          }
          const result = await client.getDealRisks(dealId);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        }

        case "get_stakeholders": {
          const dealId = String(args.deal_id || "").trim();
          if (!dealId) {
            return { isError: true, content: [{ type: "text", text: "Error: 'deal_id' is required." }] };
          }
          const result = await client.getStakeholders(dealId);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        }

        case "get_next_best_action": {
          const dealId = String(args.deal_id || "").trim();
          if (!dealId) {
            return { isError: true, content: [{ type: "text", text: "Error: 'deal_id' is required." }] };
          }
          const result = await client.getNextBestAction(dealId);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        }

        case "list_deals": {
          const deals = await client.listDeals({
            search: args.search ? String(args.search) : undefined,
            limit: typeof args.limit === "number" ? args.limit : 20,
          });
          return { content: [{ type: "text", text: JSON.stringify(deals, null, 2) }] };
        }

        default:
          return {
            isError: true,
            content: [{ type: "text", text: `Unknown tool: ${name}` }],
          };
      }
    } catch (err: any) {
      return {
        isError: true,
        content: [{ type: "text", text: `Revtelic Error: ${err.message || String(err)}` }],
      };
    }
  });

  const transport = new StdioServerTransport();
  server.connect(transport).catch((err: any) => {
    console.error("Fatal error running Revtelic MCP server:", err);
    process.exit(1);
  });
}

// Auto-run if executed directly
const currentScript = typeof process !== "undefined" ? process.argv?.[1] : "";
if ((import.meta as any).url === `file://${currentScript}` || currentScript?.endsWith("revtelic-mcp.js")) {
  runServer();
}

export { RevtelicClient };
export * from "./types.js";
