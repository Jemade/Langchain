# Product and evaluation evidence

The project addresses a plausible logistics workflow, not a proven customer demand. Interview dispatchers before making sales or time-saving claims. Ask them to walk through the most recent delay, damage report and document exception. Identify information sources, approval owners, current tools, handoffs and measurable consequences. Obtain consent before using real operational records.

The initial policies are fictional. Replace them with an operator-approved, versioned corpus after discovery. The MVP loads policies at startup; policy changes require restart and existing pending requests retain their original evidence in checkpoints.

## Checks included

- Restart-safe human review and duplicate-reference handling.
- Invalid input, unauthorized API access and conflicting references.
- Export blocked before approval; repeated decision rejected.
- No applicable policy ends in needs-information.
- LangChain model composition tested with a fake chat model.
- A provider error can be retried without creating another request.
- Browser: enter report, open evidence, approve and download an export.
- 60 synthetic demo cases: category routing, correct source and policy restriction in deterministic output.

The 60 cases have only three underlying procedures and repeated shipment variants. They are smoke coverage, not a meaningful measure of generalization. They do not score live Bedrock factual accuracy, prompt-injection resistance or commercial usefulness.

## Build a stronger model evaluation after real discovery

Collect 50–100 independently reviewed, anonymized reports across ambiguous categories, contradictory notes, absent policy, instruction injection, uncertain ETA, missing facts, damage liability and stale policy. For each record, include expected applicable source, permissible next action, forbidden claims and required clarification. Evaluate source recall separately from factual grounding and action safety. Use exact checks for references/required fields and a calibrated model judge only as a supplementary signal for open-ended drafts. Human reviewers should inspect judge disagreements.

Track latency, model usage/cost and workflow completion when running live trials. Do not publish invented improvements. Record the dataset version, model ID, prompts, commit and actual run results. A dispatcher pilot should measure current vs assisted handling time and incorrect commitments, with a clear privacy policy.
