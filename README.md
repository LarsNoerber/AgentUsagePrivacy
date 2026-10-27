# AgentUsagePrivacy

This repository contains only AgentMeter's public privacy/publisher notice and its GitHub Pages source. The app
fetches `policy.json` from this Pages site when the in-app legal screen opens. The page is also available in German
and English. The private `AgentUsageApp` repository contains the Android app source.

To update the notice, edit `policy.json`, change `updatedAt`, and push to `main`. The Pages workflow rebuilds and
publishes the German and English HTML pages and the JSON endpoint from that single file. No Android app release is
needed for text updates.

The public site contains the publisher details required for the app listing. Keep unrelated project files and
credentials out of this repository.
