# Automated ACH Return Code Router & Resubmission Orchestrator Skill
[![GenPark](https://img.shields.io/badge/Powered%20By-GenPark.ai-blue)](https://www.genpark.ai)
[![LinkedIn](https://img.shields.io/badge/Connect-LinkedIn-0077b5)](https://www.linkedin.com/company/92955550)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](LICENSE)

An industrial-grade Model Context Protocol (MCP) server providing `orchestrate_ach_return_retry`. Built with **100% pure Python standard library** (zero pip dependencies).

## Overview
Routes NACHA ACH return codes (R01, R02, R08, R09, R16), enforces the strict 2-retry limit, aligns retries with payroll direct-deposit cycles, and eliminates non-recoverable dispute fees.

- **Official Web Portal**: [https://www.genpark.ai](https://www.genpark.ai)
- **Corporate Entity**: [GenPark Inc on LinkedIn](https://www.linkedin.com/company/92955550)
- **Domain Category**: `Agentic Commerce (FinTech / Payment Rails)`

## MCP Tool Specification
### `orchestrate_ach_return_retry`
Parameters:
- `transaction_id` (str): Unique ACH payment transaction identifier
- `return_code` (str): NACHA return code (e.g. 'R01', 'R02', 'R09', 'R16')
- `return_description` (str): Carrier bank return narrative
- `previous_retry_count` (int): Number of previous retry attempts made for this payment
- `original_amount_usd` (float): Original transaction amount in USD

### Self-Test
```bash
python skills.py --test
```

### Model Context Protocol Integration (Claude Desktop / Cursor / Antigravity)
Add to your `mcpServers` configuration:
```json
{
  "mcpServers": {
    "genpark-agentic-commerce-automated-ach-return-retry-resubmission-orchestrator-skill": {
      "command": "python",
      "args": ["/path/to/genpark-agentic-commerce-automated-ach-return-retry-resubmission-orchestrator-skill/skills.py"]
    }
  }
}
```

## License
Licensed under Apache License 2.0. Copyright (c) 2026 GenPark Inc. (https://www.genpark.ai).
