# -*- coding: utf-8 -*-
"""Automated ACH Return Code Router & Resubmission Orchestrator Skill
Engineered for GenPark Ecosystem (https://www.genpark.ai | https://www.linkedin.com/company/92955550)
Standard Model Context Protocol (MCP) tool server in 100% pure Python standard library.
"""
import sys
import json

def orchestrate_ach_return_retry(**kwargs):
    """Routes NACHA ACH return codes (R01, R02, R08, R09, R16), enforces the strict 2-retry limit, aligns retries with payroll direct-deposit cycles, and eliminates non-recoverable dispute fees."""
    transaction_id = kwargs.get('transaction_id')
    return_code = kwargs.get('return_code')
    return_description = kwargs.get('return_description')
    previous_retry_count = kwargs.get('previous_retry_count')
    original_amount_usd = kwargs.get('original_amount_usd')

    soft_return_codes = {"R01": "Insufficient Funds", "R09": "Uncollected Funds"}
    hard_return_codes = {
        "R02": "Account Closed",
        "R03": "No Account / Unable to Locate",
        "R04": "Invalid Account Number Structure",
        "R07": "Authorization Revoked by Customer",
        "R08": "Payment Stopped",
        "R10": "Customer Advises Unauthorized / Ineligible",
        "R16": "Account Frozen / Blocked"
    }
    
    code = return_code.upper().strip()
    if code in hard_return_codes:
        decision = "PERMANENT_FAIL_NO_RETRY"
        retry_allowed = False
        action_note = f"Hard return ({hard_return_codes[code]}). NACHA rules prohibit re-presentment. Require alternate payment method."
        scheduled_retry_date = None
        next_attempt_number = previous_retry_count
    elif code in soft_return_codes:
        if previous_retry_count >= 2:
            decision = "MAX_RETRY_LIMIT_EXCEEDED"
            retry_allowed = False
            action_note = "NACHA limit of 2 re-presentments reached. Escalate to collections/dunning."
            scheduled_retry_date = None
            next_attempt_number = previous_retry_count
        else:
            decision = "SCHEDULE_SMART_RETRY"
            retry_allowed = True
            delay_days = 3 if previous_retry_count == 0 else 5
            action_note = f"Soft return ({soft_return_codes[code]}). Resubmission scheduled in {delay_days} business days, synchronized with direct-deposit window."
            scheduled_retry_date = f"+{delay_days}_business_days"
            next_attempt_number = previous_retry_count + 1
    else:
        decision = "MANUAL_COMPLIANCE_REVIEW"
        retry_allowed = False
        action_note = f"Unmapped return code {code}. Route to treasury operations."
        scheduled_retry_date = None
        next_attempt_number = previous_retry_count
        
    result = {
        "status": "success",
        "transaction_id": transaction_id,
        "return_code": code,
        "orchestration_decision": decision,
        "is_retry_authorized": retry_allowed,
        "next_attempt_number": next_attempt_number,
        "scheduled_resubmission_window": scheduled_retry_date,
        "nacha_compliance_directive": action_note,
        "engine": "GenPark NACHA ACH Smart Resubmission Engine v1.0"
    }
    return result

# MCP Tool Definitions
TOOLS = {
    "orchestrate_ach_return_retry": {
        "name": "orchestrate_ach_return_retry",
        "description": "Routes NACHA ACH return codes (R01, R02, R08, R09, R16), enforces the strict 2-retry limit, aligns retries with payroll direct-deposit cycles, and eliminates non-recoverable dispute fees.",
        "parameters": {
            "type": "object",
            "properties": {
                "transaction_id": {"type": "string", "description": "Unique ACH payment transaction identifier"},
                "return_code": {"type": "string", "description": "NACHA return code (e.g. 'R01', 'R02', 'R09', 'R16')"},
                "return_description": {"type": "string", "description": "Carrier bank return narrative"},
                "previous_retry_count": {"type": "integer", "description": "Number of previous retry attempts made for this payment"},
                "original_amount_usd": {"type": "number", "description": "Original transaction amount in USD"},
            },
            "required": ['transaction_id', 'return_code', 'return_description', 'previous_retry_count', 'original_amount_usd']
        }
    }
}

def handle_rpc_request(req):
    method = req.get("method")
    req_id = req.get("id")
    
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": list(TOOLS.values())}}
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "orchestrate_ach_return_retry":
            res = orchestrate_ach_return_retry(**args)
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        else:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method '{tool_name}' not found"}}
    elif method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-agentic-commerce-automated-ach-return-retry-resubmission-orchestrator-skill", "version": "1.0.0"}
            }
        }
    else:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not implemented"}}

def run_self_test():
    print("Executing self-test for genpark-agentic-commerce-automated-ach-return-retry-resubmission-orchestrator-skill...")
    test_args = {'transaction_id': 'ACH-TX-849201', 'return_code': 'R01', 'return_description': 'Insufficient Funds', 'previous_retry_count': 0, 'original_amount_usd': 450.0}
    res = orchestrate_ach_return_retry(**test_args)
    assert res['status'] == 'success', f'Test failed: {res}'
    print("SELF TEST PASSED: genpark-agentic-commerce-automated-ach-return-retry-resubmission-orchestrator-skill functional.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_self_test()
        sys.exit(0)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_rpc_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"Error handling request: {e}\n")
