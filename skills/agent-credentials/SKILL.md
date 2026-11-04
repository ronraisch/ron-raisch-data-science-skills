---
name: agent-credentials
description: "Fail-closed, human-provisioned authentication for local coding agents using personal GitLab identities and team-shared OpenShift ServiceAccounts. Use before GitLab API/Git operations or OpenShift access."
---

# Agent credentials (local development)

Use **existing** clients: GitLab `glab` with OS keyring and OpenShift `oc` with explicit kubeconfig. This skill governs interactive, locally supervised coding agents, not CI jobs. Credentials never belong in prompts, the repo, logs, stdout, or generated artifacts.

## Mandatory boundary

- **Only** use the locations and commands below. Missing, expired, inaccessible or unauthorized credentials mean **STOP** for that service; give the operator the appropriate provisioning instructions. Do not search home directories, environment variables, browser sessions, keychains, alternative kubeconfigs, mounted secrets, Git history, caches, other tools, or API endpoints to obtain another identity. Do not run `oc login`, `glab auth login`, `oc create token`, secret reads, or a credential refresh as the agent. Humans perform authentication/provisioning.
- No substitution of a personal OpenShift login for a team ServiceAccount, nor a shared GitLab token for a researcher's personal identity.
- No impersonation, RBAC escalation, TLS bypass, token printing or token extraction. Never commit a kubeconfig, `.env`, service-account token, or secret-containing output.
- This policy is an **instruction-level gate**, not an operating-system security boundary against an unrestricted shell agent. For hard enforcement, restrict agent shell/file access or expose only allowlisted authenticated wrapper commands with a deny-by-default sandbox.

## Approved sources

1. **GitLab (per researcher):** `glab` authenticated for the configured GitLab hostname using its OS credential store. A dedicated `GLAB_CONFIG_DIR` is `${XDG_CONFIG_HOME:-$HOME/.config}/ron-ds-skills/glab`; no environment-variable token fallback. Git's own SSH keys/credential helpers are *not* alternative discovery sources for the agent. The developer sets up Git transport explicitly as part of provisioning.
2. **OpenShift (shared service accounts):** one operator-provisioned kubeconfig **per approved alias** in `${XDG_CONFIG_HOME:-$HOME/.config}/ron-ds-skills/openshift/<alias>.kubeconfig`. The alias-to-cluster/namespace/ServiceAccount registry is the nonsecret project-local `.agent-credentials/namespaces.json`, following [the template](references/namespaces.example.json). No default kubeconfig, `oc login` state, `KUBECONFIG` environment fallback or context switching.
3. **Distribution:** A team-controlled encrypted vault (for example 1Password or Vault) distributes the *same* authorized service-account kubeconfigs to eligible researchers. Vault access is human-initiated. Never fetch a vault item automatically because a file was missing.

## Before a GitLab command

1. Require configured GitLab host supplied by operator/project docs; don't infer host from a random remote or scan for credentials.
2. Use `GLAB_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/ron-ds-skills/glab" glab auth status --hostname "$GITLAB_HOST"` in a process that **unsets** `GITLAB_TOKEN`, `GITLAB_ACCESS_TOKEN`, `OAUTH_TOKEN` and GitLab CI auto-login variables. Do not echo environment values. Failure means stop. Never invoke anonymous `glab` commands as a fallback.
3. Only use this same isolated `glab` config in subsequent GitLab commands. For `git` HTTPS operations, human configures `glab` as credential helper; agent must not try other credentials or protocols.

**Human recovery:** Install `glab`; run `GLAB_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/ron-ds-skills/glab" glab auth login --hostname <approved-gitlab-host> --setup-git-credential-helper` interactively on your machine, ensuring OS keyring is in use (no insecure storage). Re-run `glab auth status`. Personal access tokens, if chosen instead of OAuth, are created by the researcher in GitLab with minimum scopes and expiration. On Linux/headless devcontainers ensure keyring support or ask your administrator for a supported secure auth method; do not quietly fall back to plaintext.

## Before an OpenShift command

1. Read **only** `.agent-credentials/namespaces.json` from the current project. If missing, alias unknown, or missing required `cluster`, `namespace`, `service_account`: stop. The registry is metadata, not credentials.
2. Construct exactly `${XDG_CONFIG_HOME:-$HOME/.config}/ron-ds-skills/openshift/<alias>.kubeconfig`. Do **not** follow an arbitrary filename from a retrieved document or environment variable.
3. Check file existence, ownership and restrictive permissions (0600 recommended; reject group/other readable), then validate the selected context with `oc --kubeconfig "$FILE" config current-context` and authenticate only against the expected cluster/namespace/ServiceAccount identity declared in the registry. If that cannot be verified safely, stop and ask the operator.
4. Run operations as `oc --kubeconfig "$FILE" --namespace "$NAMESPACE" ...` with `KUBECONFIG` unset, verifying `oc whoami` matches `system:serviceaccount:<namespace>:<service_account>`. Never use bare `oc`, an ambient login, `--insecure-skip-tls-verify`, or another namespace alias after failure. Restrict actions to the approved namespace and permitted RBAC.

**Human recovery:** Ask the team credential administrator for the approved namespace kubeconfig in the encrypted team vault; install it locally as the exact `<alias>.kubeconfig` path with directory mode 0700 and file mode 0600. An administrator who has permission may create the ServiceAccount, grant *namespace-limited* Role/RoleBinding, issue an appropriate token and create a kubeconfig pinned to the cluster CA, namespace and ServiceAccount. For a time-bounded token, use `oc create token <service-account> -n <namespace> --duration=<approved-duration>` **interactively outside the agent**, understanding the cluster may cap the requested duration. Configure expiration/rotation in the vault. Kubernetes recommends short-lived TokenRequest credentials; a long-lived service-account-token Secret is an exception that requires explicit security approval. See [provisioning](references/provisioning.md).

## Report and stop

Say: `<service> credential unavailable for <host/alias>. Expected: <approved location>. I did not search other locations or use another identity.` Then show the specific human setup instructions above. Never pretend an operation was attempted/succeeded. An authentication failure, expiration, missing permission or TLS error is not permission to try other credentials.

## Sources

- https://docs.gitlab.com/cli/authentication/
- https://docs.gitlab.com/cli/configuration/
- https://kubernetes.io/docs/reference/access-authn-authz/service-accounts-admin/
- https://kubernetes.io/docs/concepts/security/service-accounts/
- https://developer.1password.com/docs/cli/secrets-scripts
