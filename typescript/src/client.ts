/**
 * Revtelic Client — Zero-friction deal analysis & workspace sync client.
 */

import {
  AnalyzeDealArgs,
  DealAnalysis,
  DealboardSummary,
  RevtelicConfig,
} from "./types.js";

declare const process: any;
const getEnv = (key: string): string | undefined => {
  try {
    return typeof process !== "undefined" ? process?.env?.[key] : undefined;
  } catch {
    return undefined;
  }
};

const DEFAULT_API_BASE = "https://api.revtelic.com";

export class RevtelicClient {
  public readonly apiBase: string;
  public readonly apiKey?: string;

  constructor(config: RevtelicConfig = {}) {
    this.apiBase = (
      config.apiBase ||
      getEnv("REVTELIC_API_BASE_URL") ||
      getEnv("DEALWIZE_API_BASE_URL") ||
      DEFAULT_API_BASE
    ).replace(/\/+$/, "");

    this.apiKey =
      config.apiKey ||
      getEnv("REVTELIC_API_KEY") ||
      getEnv("DEALWIZE_API_KEY");
  }

  private getHeaders(extraHeaders: Record<string, string> = {}): Record<string, string> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "User-Agent": "revtelic-mcp-client/1.0.0",
      ...extraHeaders,
    };
    if (this.apiKey) {
      headers["Authorization"] = `Bearer ${this.apiKey}`;
    }
    return headers;
  }

  /**
   * Execute a tool call against Revtelic's Streamable HTTP MCP endpoint.
   */
  public async callMcpTool(name: string, args: Record<string, any>): Promise<any> {
    const url = `${this.apiBase}/api/v1/mcp`;
    const payload = {
      jsonrpc: "2.0",
      id: Math.floor(Math.random() * 1000000),
      method: "tools/call",
      params: {
        name,
        arguments: args,
      },
    };

    const response = await fetch(url, {
      method: "POST",
      headers: this.getHeaders({
        Accept: "application/json, text/event-stream",
      }),
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`Revtelic API Error (${response.status}): ${errText}`);
    }

    const resJson = (await response.json()) as any;
    if (resJson.error) {
      throw new Error(resJson.error.message || JSON.stringify(resJson.error));
    }

    const content = resJson.result?.content;
    if (Array.isArray(content) && content.length > 0 && content[0]?.text) {
      try {
        return JSON.parse(content[0].text);
      } catch {
        return content[0].text;
      }
    }
    return resJson.result;
  }

  /**
   * Analyze raw sales transcript, email thread, or call notes.
   * Works without an API key in zero-friction guest mode!
   */
  public async analyzeDeal(args: AnalyzeDealArgs): Promise<DealAnalysis> {
    try {
      const result = await this.callMcpTool("analyze_deal", {
        transcript: args.transcript,
        name: args.name,
      });

      if (typeof result === "object" && result !== null) {
        return result as DealAnalysis;
      }
      return {
        health_score: 50,
        brutal_truth: String(result),
        risks: [],
      };
    } catch (mcpErr: any) {
      // Fallback directly to public analyse endpoint if MCP endpoint returns error
      const url = `${this.apiBase}/api/v1/public/analyse`;
      const res = await fetch(url, {
        method: "POST",
        headers: this.getHeaders(),
        body: JSON.stringify({
          transcript: args.transcript,
          name: args.name,
        }),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(
          `Analysis failed: ${mcpErr?.message || text || res.statusText}`
        );
      }

      const json = (await res.json()) as any;
      const data = json.data || json;
      return data as DealAnalysis;
    }
  }

  /**
   * Get deal health score and assessment for a saved deal ID or slug.
   * Requires Revtelic account/API key.
   */
  public async getDealHealth(dealId: string): Promise<any> {
    return this.callMcpTool("get_deal_health", { deal_id: dealId });
  }

  /**
   * Uncover deal killers, technical risks, and blockers.
   * Requires Revtelic account/API key.
   */
  public async getDealRisks(dealId: string): Promise<any> {
    return this.callMcpTool("get_deal_risks", { deal_id: dealId });
  }

  /**
   * Get buyer champions, decision makers, and missing stakeholders.
   * Requires Revtelic account/API key.
   */
  public async getStakeholders(dealId: string): Promise<any> {
    return this.callMcpTool("get_stakeholders", { deal_id: dealId });
  }

  /**
   * Determine single highest-priority next best action to progress the deal.
   * Requires Revtelic account/API key.
   */
  public async getNextBestAction(dealId: string): Promise<any> {
    return this.callMcpTool("get_next_best_action", { deal_id: dealId });
  }

  /**
   * List dealboards for connected Revtelic workspace.
   */
  public async listDeals(params: { page?: number; limit?: number; search?: string } = {}): Promise<DealboardSummary[]> {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.set("page", String(params.page));
    if (params.limit) searchParams.set("limit", String(params.limit));
    if (params.search) searchParams.set("search", params.search);

    const queryStr = searchParams.toString();
    const url = `${this.apiBase}/api/integrations/v1/dealboards${queryStr ? `?${queryStr}` : ""}`;

    const res = await fetch(url, {
      method: "GET",
      headers: this.getHeaders(),
    });

    if (!res.ok) {
      const err = await res.text();
      throw new Error(`List deals failed (${res.status}): ${err}`);
    }

    const data = (await res.json()) as any;
    return (data.data?.dealboards || data.data || []) as DealboardSummary[];
  }
}
