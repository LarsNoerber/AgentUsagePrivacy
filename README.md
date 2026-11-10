# AgentUsagePrivacy

This repository contains only AgentMeter's public privacy/publisher notice and its GitHub Pages source. The app
fetches `policy.json` from this Pages site when the in-app legal screen opens. The page is also available in German
and English. The private `AgentUsageApp` repository contains the Android app source.

To update the notice, edit `policy.json`, change `updatedAt`, and push to `main`. The Pages workflow rebuilds and
publishes the German and English HTML pages and the JSON endpoint from that single file. No Android app release is
needed for text updates.

The public site contains the publisher details required for the app listing. Keep unrelated project files and
credentials out of this repository.

Policy revision 9 additionally describes Android autofill via the chosen device password manager, the local previous-connection flag, and deletion of password-manager entries. It also describes provider and identity requests, persistent GeckoView storage with tracking protection disabled, encrypted API keys for OpenRouter/DeepSeek/Z.ai/Mistral, Claude and Groq readings, MFA session retention, local language preferences, history exports, launcher widgets and optional local notification alerts. Native engine telemetry is disabled; provider pages retain their own processing. No AgentMeter application server does not mean no personal data are transmitted.

Update `policyRevision` when the bundled notice changes materially. The generated public JSON includes both
`privacySections` and the flat `privacy` field read by Android. The site build rejects notices that exceed the
Android schema, length or download limits. In the Android repository, run `python scripts/sync_privacy.py` to
regenerate the exact same bilingual strings, Markdown documents and Android verification fixture. Check all
copies with `python scripts/sync_privacy.py --check`.

Do not publish an address that the publisher has identified as incorrect; obtain its exact replacement first.

AgentMeter 1.2.3 first displays the provider-data notice automatically and waits for explicit feature activation.
The long notice is then available through the information button. Later/Back is not activation; pausing closes
provider sessions and cancels their schedule. This is separate from Android/system traffic and previously started
engine security functions. Earlier development builds may have queried selected providers on opening.
