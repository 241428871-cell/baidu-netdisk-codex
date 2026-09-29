---
name: baidu-netdisk
description: Connect to Baidu Netdisk through this plugin's official MCP bridge and manage files with safe, verifiable operations.
---

# Baidu Netdisk

Use the bundled baidu-netdisk MCP server for Baidu Netdisk tasks. It relays
tools from Baidu's official SSE MCP endpoint. Inspect the live tool schemas
before calling a tool; availability and parameter names can change.

## Connection

- A missing authorization means the user must run the plugin's local
  scripts/bootstrap.py auth flow. The Baidu success URL and token belong in
  that local window or terminal only. Never request them in chat, put them in
  a repository, or log them.
- The OAuth consent application's displayed name is configured in Baidu's
  developer console. A plugin cannot rename another Baidu application.
- scripts/bootstrap.py check performs a read-only connection check.
- This bridge uses Baidu's SSE mode. Baidu's local upload tool requires its
  separate stdio SDK and is not included here.

## File operations

1. Confirm the exact source and destination paths from the user's request.
   List the source and target first, including all pages where the tool
   paginates.
2. For a large task, save an inventory and a concrete action plan in the
   working directory. Keep personal inventories and tokens out of the plugin
   repository.
3. Use the requested operation exactly. A request to copy does not authorize
   moving or deleting the source. Check for existing target names before
   creating folders or copying files.
4. Check both overall and per-item errors in responses. A successful HTTP
   response may still contain a Baidu error. On frequency control (including
   code 31034 or HTTP 429), pause, reduce concurrency, and retry with a
   resumable checkpoint. Split a rejected copy batch into smaller batches.
5. Verify the destination and report counts of completed, already present,
   skipped, and unresolved items. Do not count a submitted request as a
   successful copy until the response or a destination listing confirms it.

For hundreds of thousands of files, use a resumable local script with Baidu's
documented file APIs if repeated one-file MCP calls would be impractical. Read
the access token from the same local credential store; never put it in a
command line, URL shown to the user, transcript, or output artifact.
