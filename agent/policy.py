"""Pure gateway policy. All evidence comes from the command or trusted context."""
from kit.mcp.specs import TOOL_SPECS, A2A_PEERS, cost_of
from kit.mcp.a2a import AGENT_CARDS, admit_skill, verify_delegation
from kit.mcp.types import ToolCall
from agent.guardrails import scan_for_injected_instructions
from agent.strategy import successor_of


def learner_id(value):
    """Normalise namespace casing without accepting unrelated identities."""
    value = str(value)
    if value.lower().startswith("learner:"):
        return value.split(":", 1)[1]
    return value if value.startswith("sv-") else None


def plan_call(cmd, ctx, memory):
    headers = {str(k).lower(): v for k, v in cmd.headers.items()}
    args = dict(cmd.args)
    server, tool = successor_of(cmd.server, cmd.tool) or (cmd.server, cmd.tool)
    spec = TOOL_SPECS.get((server, tool))
    if spec is None:
        return "unknown server or tool", {}, 0
    if any(args.get(key) for key in ("route", "_route", "replica")):
        return "routing must be expressed in the transport header", {}, 0
    if headers.get("x-server-fingerprint") == "unvouched":
        return "server identity is not vouched for", {}, 0
    if headers.get("x-card-signature") == "invalid":
        return "peer card signature is invalid", {}, 0
    if args.get("peer_unverified"):
        return "peer result requires independent verification", {}, 0
    if len(str(args.get("catalog", ""))) > 1024:
        return "oversized unsolicited catalog", {}, 0
    # Only scan instruction-bearing fields, not legitimate search quotations.
    for key in ("note", "instruction", "system_override"):
        if scan_for_injected_instructions(str(args.get(key, ""))).suspicious:
            return "embedded instruction cannot authorise a tool call", {}, 0
    if "wiki.read" not in ctx.scopes and not spec.is_write:
        return "wiki.read scope is required", {}, 0
    for key in ("learner", "learner_id", "target", "subject"):
        target = learner_id(args.get(key, ""))
        if target is not None and target != learner_id(ctx.act):
            return "target learner does not belong to act", {}, 0
    if headers.get("act") and learner_id(headers["act"]) != learner_id(ctx.act):
        return "delegation act does not match caller", {}, 0
    if server in A2A_PEERS:
        aud = headers.get("aud")
        if aud is not None and aud not in (server, "a2a:" + server):
            return "delegation audience does not match peer", {}, 0
        card = memory._cards.get(server)
        if card is not None and not card.get("verified"):
            return "peer card failed registry verification", {}, 0
        skill = args.get("skill")
        if skill and not admit_skill(AGENT_CARDS[server], skill).admitted:
            return "skill is not declared by the peer", {}, 0
        token = args.get("delegation")
        if token is not None and not verify_delegation(
                token, aud="a2a:" + server, call_index=cmd.call_index,
                expected_act=ctx.act, seen_token_ids=memory._token_ids).admitted:
            return "delegation token failed verification", {}, 0
    if spec.needs_lease and cmd.lease_id not in ctx.leases:
        return "get_frame requires a live lease from this round", {}, 0
    if spec.is_write:
        if "wiki.write:" + server not in ctx.scopes:
            return "write scope is required", {}, 0
        if any(not headers.get(key) for key in spec.required_headers):
            return "write requires If-Match and Idempotency-Key", {}, 0
        if headers["idempotency-key"] in memory._write_keys:
            return "write idempotency key has already been authorised", {}, 0
        receipt = memory._etags.get(args.get("anchor"))
        if not receipt or receipt[0] != headers["if-match"] or receipt[1] != ctx.round:
            return "write requires matching provenance from this round", {}, 0
        if cmd.call_index - receipt[2] > 1:
            return "refresh provenance immediately before writing", {}, 0
    fields = cmd.fields or spec.default_fields
    if fields == ("*",):
        fields = spec.default_fields
    # Anchors are carried by the envelope, even when absent from the priced mask.
    fields = tuple(f for f in fields if f != "anchor" or f in spec.all_fields)
    if any(f not in spec.all_fields for f in fields):
        return "requested field is not supported by this tool", {}, 0
    if (server, tool) == ("registry", "list_servers"):
        fields = ("name",)
    elif (server, tool) == ("glossary", "list_terms"):
        fields = spec.default_fields[:1]
    replica = headers.get("mcp-replica")
    if replica is not None and replica not in ("w", "c"):
        return "unknown replica header", {}, 0
    if server == "slides":
        # Respect an explicit anchor revision; do not guess freshness from drift.
        parts = str(args.get("anchor", "")).split("/")
        anchor_rev = parts[1] if len(parts) > 1 and parts[1] in ("w", "c") else None
        if anchor_rev and replica and replica != anchor_rev:
            return "replica header conflicts with anchor revision", {}, 0
        headers["mcp-replica"] = anchor_rev or replica or "w"
    if memory._round_no != ctx.round:
        memory._round_no, memory._round_spend = ctx.round, 0
    key = (server, tool)
    if spec.rate_limit:
        limit, window = spec.rate_limit
        rounds = memory._rate_calls.setdefault(key, [])
        if sum(r > ctx.round - window for r in rounds) >= limit:
            return "tool rate window is exhausted", {}, 0
    if (server, tool) == ("slides", "query"):
        args.setdefault("limit", 2)
    rows = args.get("limit", 1)
    if not isinstance(rows, int) or isinstance(rows, bool) or not 1 <= rows <= 10:
        return "query limit must be an integer between 1 and 10", {}, 0
    call = ToolCall(server=server, tool=tool, args=args, fields=fields,
                    headers=headers, lease_id=cmd.lease_id, call_index=cmd.call_index)
    estimate = cost_of(call, rows)
    reserve = max(0, 10 - ctx.round) * 4
    if estimate > ctx.credits or memory._round_spend + estimate > 11:
        return "call exceeds the credit or round allowance", {}, 0
    if ctx.round > 0 and ctx.credits - estimate < reserve:
        return "reserve credits for the remaining rounds", {}, 0
    changes = {}
    for name, value in (("server", server), ("tool", tool),
                        ("headers", headers), ("fields", fields), ("args", args)):
        if value != getattr(cmd, name):
            changes[name] = value
    return None, changes, estimate
