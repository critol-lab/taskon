# TaskOn Automation (English)

This repository automates authorized flows on TaskOn: wallet auth/invite, binding Twitter/Discord, entering campaigns, checking winners, and claiming CAPs. It mirrors the original reference structure, with improvements and optional proxies.

- English quickstart (Windows/Linux)
- Configuration and accounts CSV format (proxy optional)
- Running modules (Auth, Bind, Enter campaign, Check winners, Claim CAPs)


## Prerequisites
- Python 3.11
- Git
- Poetry (recommended): https://python-poetry.org/docs/


## Installation
```bash
git clone https://github.com/critol-lab/taskon
cd taskon
poetry install
```

On Windows you can run `INSTALL.bat` instead of the last command.


## First run
On the first run the app will create directories `input/` and `log/` and write `config/config.toml` from defaults.

Start the app:
```bash
poetry run python main.py
```
On Windows you can use `START.bat`.


## Configuration (`config/config.toml`)
Key options:
- `HIDE_SECRETS`: Hide sensitive output in logs (enabled by default).
- `DEFAULT_INVITE_CODE`: Default invite code used when not specified in CSV.
- `ANTICAPTCHA_API_KEY`: API key for Anticaptcha if a campaign requires ReCaptcha.
- `MAX_TASKS`: Global concurrency limit (default 5).
- `DELAY_RANGE`: Min/max delay between accounts sharing the same proxy (default 60–120 sec). When proxies are not used, delay still applies per group.


## Accounts CSV (`input/accounts.csv`)
When the app starts, it creates `input/accounts.csv` with the following columns. Proxy is now optional.

- (optional) Proxy
- (required) Private key
- (optional) Invite code
- (optional) Discord token
- (optional) Twitter token
- (auto) Twitter ct0
- (auto) Site token
- (auto) Discord username
- (auto) Twitter username
- (auto) Invite code

Notes:
- Columns may be reordered but must not be renamed.
- You may add your own columns; the app ignores unknown columns.
- For backward compatibility, the loader still supports a legacy column named `(required) Proxy`. If present, it will be used; otherwise `(optional) Proxy` can be empty.


## Using the app (Modules)
After loading `accounts.csv`, choose a module:

- Auth and Invite: Requests a TaskOn challenge, signs with wallet, submits invite if provided, and stores the auth token.
- Bind Discords / Bind Twitters: Binds SNS using provided tokens.
- Enter campaign: Solves tasks it can, then submits the campaign. If ReCaptcha is required, it uses Anticaptcha. If no proxy is provided for an account, captcha is solved without proxy.
- Check winners: Lists winners for a campaign.
- Claim CAPs: Claims campaign NFT rewards where available.


## Proxies (optional)
- If `(optional) Proxy` is set for an account, that account’s HTTP traffic and ReCaptcha solving will use that proxy.
- If not set, the account runs directly without a proxy. ReCaptcha (when required) will be solved without proxy.
- Accounts are grouped by their proxy (including “no proxy” group) for rate limiting and delays.


## Troubleshooting
- Ensure your private keys are valid and properly formatted (0x-prefixed hex).
- If Anticaptcha is needed, fund your key and set `ANTICAPTCHA_API_KEY` in `config/config.toml`.
- If Twitter/Discord binding is required, fill the respective tokens in the CSV.
- For large batches, tune `MAX_TASKS` and `DELAY_RANGE` to avoid rate limits.


## License
This repository mirrors and adapts an existing open-source structure for interoperability. Review upstream licenses as applicable.
