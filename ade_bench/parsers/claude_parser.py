import json
import re
from typing import Dict, Any

from ade_bench.parsers.base_parser import BaseParser, UnitTestStatus


class ClaudeParser(BaseParser):
    """Parser for Claude agent responses to extract runtime, token usage, and cost metrics."""
    
    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse Claude agent response to extract metrics.
        
        Returns a dictionary with the following keys:
        - runtime_ms: The higher of duration_ms and duration_api_ms
        - total_input_tokens: input_tokens + cache_creation_input_tokens
        - total_output_tokens: output_tokens
        - cost_usd: total_cost_usd
        - success: Whether the response indicates success
        """

        default_return = {
            "runtime_ms": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "cost_usd": 0.0,
            "success": False
        }
        try:
            # Get lines and remove empty ones
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            lines_to_try = []

            # Find line after AGENT RESPONSE and add it to the list of lines to try
            agent_response_line = None
            for i, line in enumerate(lines):
                if line.startswith('AGENT RESPONSE:'):
                    if i + 1 < len(lines):
                        agent_response_line = lines[i + 1]
                        lines_to_try.append(agent_response_line)
                        break
                    
            # Add lines from bottom up
            lines_to_try.extend(reversed(lines))

            # Try parsing each line
            for line in lines_to_try:
                self._logger.debug(f"Trying to parse line: {line}")
                if line.startswith('{') and line.endswith('}'):
                    try:
                        data = json.loads(line)
                        self._logger.info("Found parsable JSON response")
                        return self._parse_json_response(data)
                    except json.JSONDecodeError:
                        continue

            # If we can't parse JSON, return default values
            self._logger.warning("Could not find parsable JSON response")
            return default_return
            
        except Exception as e:
            self._logger.error(f"Error parsing Claude response: {e}")
            return default_return
    
    def _parse_json_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the JSON response data to extract metrics."""
        # Extract runtime - use the higher of duration_ms and duration_api_ms
        duration_ms = data.get("duration_ms", 0)
        duration_api_ms = data.get("duration_api_ms", 0)
        runtime_ms = max(duration_ms, duration_api_ms)
        
        # Extract token usage
        usage = data.get("usage", {})
        input_tokens = usage.get("input_tokens", 0)
        cache_creation_input_tokens = usage.get("cache_creation_input_tokens", 0)
        total_input_tokens = input_tokens + cache_creation_input_tokens
        total_output_tokens = usage.get("output_tokens", 0)
        
        # Extract cost
        cost_usd = data.get("total_cost_usd", 0.0)
        
        # Determine success
        success = data.get("is_error", True) == False
        
        self._logger.info(
            f"Claude response \n\t- Runtime: {runtime_ms}ms \n"
            f"\t- Input tokens: {total_input_tokens}\n"
            f"\t- Output tokens: {total_output_tokens}\n"
            f"\t- Cost: ${cost_usd:.6f}\n"
            f"\t- SUCCESS: {success}"
        )
        
        return {
            "runtime_ms": runtime_ms,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "cost_usd": cost_usd,
            "success": success
        }
