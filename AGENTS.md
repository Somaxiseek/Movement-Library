# Movement Library development

- Canonical repository: https://github.com/Somaxiseek/Movement-Library . Continue this project in this Git working copy, separate from Somarise and Somaxis. Check the remote and current work before changes; do not overwrite others' work.
- Preserve the existing 101 original records, IDs, names, sources, optional fields, unknown imported fields, and local attachments. Never automatically merge similar or duplicate records. Treat `original/` as immutable reference material.
- Keep the app fully offline with local IndexedDB and JSON backup. Do not add cloud sync, AI classification, external dependencies or a complex graph without a new user request.
- Prefer reading and navigating to editing. Preserve direct family and relationship entry points. Keep scapula as a separate body region. Muscle mappings are optional and do not belong in the main sidebar.
- Edit `extension.js`, `navigation.js`, `ui.css`, `navigation.css`, or the build/launcher sources, then run `python3 upgrade.py`. Commit the generated `index.html` with source changes. `qa.html` is generated and ignored.
- Verify meaningful behavioral changes in a real browser. Run the isolated `qa.html` checks after changes affecting persistence or navigation; record what was actually verified and what remains unverified.
- Keep default browser origin `http://127.0.0.1:8774` and database `MovementLibraryV1` stable. Do not delete browser data to resolve development issues. Do not leave test services occupying the user's normal port; use an isolated test port and stop it afterward.
- Keep personal backups, browser database exports, attachments, credentials, temporary packaging, and unrelated Somarise files out of Git. The public repository contains application code and the supplied seed records, not the user's private local library.
- Update user-facing documentation when behavior changes. Use Git commits to preserve completed work in this repository; do not force-push or overwrite remote changes.
