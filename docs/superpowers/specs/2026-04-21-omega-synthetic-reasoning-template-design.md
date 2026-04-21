---
author: GitHub Copilot
date: "2026-04-21"
description: "Design for adding concrete OMEGA templates for synthetic reasoning taxonomy and evaluation packets"
last_updated: "2026-04-21"
status: active
tags:
- omega
- synthetic-reasoning
- templates
- evaluation
- docs
title: OMEGA Synthetic Reasoning Template Design
version: 1.0.0
---

# OMEGA Synthetic Reasoning Template Design

## Goal

Turn the Simula extraction from a methodology note into concrete OMEGA operator surfaces by
adding a taxonomy template and an evaluation-packet template that future synthetic reasoning or
benchmark-generation work can copy into a problem workspace.

## Trigger

OMEGA now recognizes Simula as a donor, but the repository still lacks a repo-native artifact
contract for synthetic reasoning work. Without templates, future work would drift into ad hoc
prompt logs or narrative summaries.

## Decision

Use two minimal templates plus lightweight wiring in existing docs.

Reasoning:

1. `templates/` is already the canonical place for reproducibility and publication scaffolds.
2. A small template pair is enough to make the new lane actionable without inventing a new runtime.
3. Existing operator docs can point to the templates without widening OMEGA's current claim scope.

## New Surfaces

- `templates/synthetic-reasoning-taxonomy.md`
- `templates/synthetic-evaluation-packet.md`
- `protocol/synthetic-reasoning-packets.md`

## Wiring Updates

- `protocol/agent-teams.md`
- `protocol/operator-runbook.md`
- `research/active/README.md`
- `protocol/research-intelligence-stack.md`

## Validation

1. changed-file diagnostics
2. `npm run sync:metrics`
3. `npm run sync:metrics:check`
4. `process: agent:preflight:docs`