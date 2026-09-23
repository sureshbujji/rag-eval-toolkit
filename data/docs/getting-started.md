# NimbusPay API Quickstart

NimbusPay is a payments API for marketplaces and SaaS platforms. Base URL for all calls is `https://api.nimbuspay.dev/v1`.

To get started, create a sandbox account from the developer dashboard. Sandbox mode uses test card `4242 4242 4242 4242`. Live keys start with `np_live_` and test keys start with `np_test_`.

All timestamps are ISO-8601 in UTC. All amounts are integer cents (e.g. 1999 = $19.99). The default pagination page size is 25 and the maximum is 100.
