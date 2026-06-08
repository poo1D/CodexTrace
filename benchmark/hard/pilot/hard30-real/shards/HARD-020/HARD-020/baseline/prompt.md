You are Codex working on a coding benchmark task.

Task ID: HARD-020
Category: sandbox_friction
Repository hint: typescript/asset_loader

User request:
Fix the asset loader so it never depends on network access: remote asset URLs must resolve through a local fixture manifest fallback, local fixture paths must still load directly, JSON and text assets must be decoded correctly, and missing assets should raise AssetLoadError.

Success check:
npm test

Complete the task with your normal coding workflow.
