# Changelog - Deep-Sea Nexus v2.0

## Version 2.0.0 (2026-02-08)

### Added
- ✅ Complete core engine implementation (nexus_core.py)
- ✅ Session management (CRUD operations)
- ✅ Index maintenance and parsing (parse_index)
- ✅ Memory recall system with relevance scoring
- ✅ Daily flush and archiving system
- ✅ Cross-date archive search (recall_archives)
- ✅ Session splitting tool (session_split.py)
- ✅ Index rebuild tool (index_rebuild.py)
- ✅ Migration tool for v1.0 -> v2.0 (migrate.py)
- ✅ Complete CLI interface
- ✅ Unit tests with 80%+ coverage
- ✅ Configuration via config.yaml
- ✅ Logging system (src/logger.py)
- ✅ Custom exceptions (src/exceptions.py)
- ✅ File locking for concurrency (src/lock.py)
- ✅ AGENTS.md protocol integration

### Changed
- Refactored data structures for better type safety
- Improved token economy (< 300 tokens for index)
- Optimized recall algorithm with GOLD priority

### Fixed
- Fixed active session path issues
- Fixed recall result type consistency
- Fixed index parsing edge cases

### Performance
- Startup time: < 1 second ✅
- Index size: < 300 tokens ✅
- Recall latency: < 100ms ✅

### Compatibility
- Pure Python (no external dependencies)
- Compatible with OpenClaw v2.0
- AGENTS.md v2.0 protocol ready

---

## Version 1.0.0 (2026-02-07)

- Initial prototype
- Basic session management
- Simple index system
