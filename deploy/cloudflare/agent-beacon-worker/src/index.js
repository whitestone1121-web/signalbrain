const LINKS = {
  repository: "https://github.com/whitestone1121-web/signalbrain",
  beacon_issue: "https://github.com/whitestone1121-web/signalbrain/issues/19",
  agent_instructions: "https://github.com/whitestone1121-web/signalbrain/blob/main/AGENTS.md",
  beacon_doc: "https://github.com/whitestone1121-web/signalbrain/blob/main/docs/AGENT_BEACON.md",
  receipt_spec: "https://github.com/whitestone1121-web/signalbrain/blob/main/docs/RECEIPT_SPEC.md"
};

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (url.pathname === "/agent-beacon.json") {
      return Response.json({
        name: "SignalBrain Agent Beacon",
        invariant:
          "No unmerged, modified, self-scored, or test-only/pin claim can increase earned trust.",
        review_lanes: ["install", "receipt parsing", "scoring", "gate", "report", "docs"],
        links: LINKS
      });
    }
    return Response.redirect(LINKS.beacon_issue, 302);
  }
};
