# AI features — design notes (not implemented)

Captured 2026-07-05 from a design discussion. Not built yet; picking-up notes for later.

## Two separate features

**1. Per-photo AI caption → searchable field**
- Add `ai_description` TextField to `ItemPhoto`.
- On photo save, send the image to a vision-capable LLM (Claude/GPT-4o/Gemini all work) with a prompt like "describe this object for a home-inventory catalog in one sentence." Store the result.
- Show it (don't hide it) — e.g. a small "AI: ..." caption under each photo — so a wrong caption is visible/correctable, and it's useful on its own even without search.
- The images are already small, capped-2500px JPEGs (from the compression work already done), so they're cheap/fast to send to an API.

**2. Title + description suggestion at item-creation time**
- "✨ Suggest title & description" button on the new-item page (explicit click, not automatic — keeps API calls opt-in).
- Sends the just-taken photo(s) to the same kind of vision call, gets back a suggested name + description, fills those two fields in — still fully editable before submit.
- This would be the app's first real use of JS `fetch()` (everything today is plain form POSTs). Small, well-understood pattern, not a framework.

## Search — start simpler than embeddings

At this item count (~hundreds), no vector DB / embeddings pipeline needed. Two tiers:

1. **Plain substring search**: `Q(name__icontains=q) | Q(description__icontains=q) | Q(photos__ai_description__icontains=q)`. Instant, free, reuses the existing search-box pattern from the store/retrieve pickers. Because the AI caption is already natural-language text, a lot of "smart" search comes for free — searching "black cylindrical" finds an item whose caption says "a black cylindrical battery" with no fuzzy-matching logic at all.
2. **"AI search" fallback**, invoked on demand only (e.g. a button when substring search comes up empty): send the whole catalog's name+caption text in one prompt along with the query, ask the LLM which item(s) best match, get back IDs. At ~200 items with short captions this fits in one request — no embeddings needed. Only costs an API call when actually used.

## Integration mechanics

- Needs its own API key, same pattern as `SECRET_KEY`: env var in `hordor_secrets.env` (outside the repo, never committed), loaded in settings. Leaking an LLM key is a more direct *financial* risk than `SECRET_KEY` (usage charges), so treat it with at least as much care.
- Anthropic is a natural fit given existing context; OpenAI/Gemini vision APIs would work equally well.
- One new lightweight dependency (`pip install anthropic` — a small SDK, not a framework).
- **Sync vs background**: captioning takes a few seconds. Simplest: do it synchronously when a photo is added (adds delay to that one action, not to Store/Retrieve, which is where the actual speed goal lives). If that's annoying, a plain Python background thread is enough at this scale — no Celery/task-queue needed.

## Things to keep in mind

- **Privacy**: photos leave the local network to a third-party API. Fine for a home-inventory app in most cases, worth a beat of thought for anything sensitive.
- **Cost**: trivial for personal use — captioning the whole existing library once is maybe a dollar or two; ongoing use is pennies per item.
- **Graceful degradation**: API calls can fail/time out — captioning should silently no-op on failure, never block or break a photo upload.

## Suggested build order, if picked up later

1. Per-photo captioning + substring search (highest value-to-effort, and lets you feel out real API latency/cost)
2. Title/description suggestion on new-item page
3. AI-powered catalog search — only if substring search actually feels insufficient in practice
