#!/usr/bin/env node

import("../dist/index.js").catch(async (err) => {
  // If dist isn't built yet, try importing source via tsx loader if available
  try {
    const { runServer } = await import("../src/index.js");
    runServer();
  } catch {
    console.error("Failed to start Revtelic MCP server:", err);
    process.exit(1);
  }
});
