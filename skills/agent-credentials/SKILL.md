---
name: agent-credentials
description: "Fail-closed credential handling for local coding agents: personal GitLab authentication and team-shared OpenShift ServiceAccounts on a configured NFS. Use before authenticated GitLab or OpenShift operations, including local CI/CD work."
---

# Agent credentials

Use established `glab` and `oc` clients; do not implement another credential manager. GitLab identity is **personal per researcher**. OpenShift identity is **team-shared per namespace**, via kubeconfig files on the approved NFS. Credentials are never copied into the repository, prompts, output, or logs.

## Non-negotiable rules

- Read only the committed, nonsecret `.agent-credentials/config.json` for approved GitLab host, NFS root, and OpenShift namespace mappings; see [example](references/config.example.json). If absent or incomplete, **STOP** and request that the operator configure it.
- Obtain credentials **only** through the source declared below. On missing/invalid/expired credentials or RBAC denial: **STOP** and provide [human setup instructions](references/provisioning.md). Never hunt in other files, environment variables, tokens, home directories, sessions, Git history, mounted paths or network endpoints; never switch to another identity or namespace as fallback.
- Do not perform interactive login, token issuance, permission escalation, secret listing, TLS bypass, or credential repair as the agent. These are human/operator actions.
- This skill is an instruction-level policy, **not** a technical sandbox against unrestricted agents. Where enforcement matters, restrict the agent's filesystem/tools or require allowlisted wrappers.

## GitLab: personal, isolated CLI login

Use the exact `gitlab.host` from the committed config. Require the researcher's personal `glab` login in `${XDG_CONFIG_HOME:-$HOME/.config}/ron-ds-skills/glab` (via `GLAB_CONFIG_DIR`). First run `glab auth status --hostname <configured-host>` with that isolated config and token override variables (`GITLAB_TOKEN`, `GITLAB_ACCESS_TOKEN`, `OAUTH_TOKEN`, `CI_JOB_TOKEN`) removed **without logging their values**. If authentication fails, stop. Subsequent `glab` operations must use the same isolated configuration.

Do not fall back to the user's global `glab` session, SSH keys, Git credential helpers not explicitly configured for this identity, environment tokens, or another host. For Git HTTPS operations, a researcher can configure `glab` as a credential helper interactively.

**Human provisioning:** Install `glab`; run `GLAB_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/ron-ds-skills/glab" glab auth login --hostname <configured-host> --setup-git-credential-helper`, then `glab auth status` with the same config. Use the researcher's personal login or expiring minimal-scope PAT and an OS keyring where supported. If keyring support is unavailable, ask the operator for an approved storage option; do not silently switch to plaintext.

## OpenShift: exact NFS kubeconfig, no fallback

1. Read the namespace alias from `.agent-credentials/config.json`. Resolve **only** `openshift.credentials_root` (an absolute shared NFS directory) plus that alias's explicitly configured `kubeconfig` basename. Reject relative roots, `..`, directory separators in filenames, unknown aliases or unapproved paths.
2. Require that exact file to exist and be readable. Do not search under NFS, inspect nearby files, copy it to local storage, follow a path outside the configured root, or fall back to `~/.kube/config` / an ambient `KUBECONFIG`. An NFS administrator controls permissions; do not attempt to change them as the agent.
3. With `KUBECONFIG` unset, use only `oc --kubeconfig "$FILE" --namespace "$NAMESPACE"`. Verify the selected context's server and namespace against the registry and `oc --kubeconfig "$FILE" whoami` equals `system:serviceaccount:<namespace>:<service_account>`. Reject unexpected identities, inaccessible clusters and TLS failures. Do not expose kubeconfig/token contents in output. Continue with the same explicit file for all operations.

**Human provisioning:** Ask the team admin to populate the **exact configured NFS file** with a kubeconfig bound to that namespace's designated ServiceAccount and trusted cluster CA. The admin configures minimal namespace-specific RBAC and token issuance/rotation. If the file exists but access fails, report the precise alias/path and ask the admin to repair or rotate it; never try a different source. See [provisioning](references/provisioning.md).

## CI/CD distinction

This policy controls **local interactive agent** access. For GitLab CI jobs, use the CI runner's **explicitly approved** identity/injection method: a runner may use NFS kubeconfigs **only if** it has an authorized mount of the same configured path and the environment/protection rules allow it. CI job tokens and protected variables are not substitutes for a researcher's local GitLab login. See [gitlab-cicd](../gitlab-cicd/SKILL.md). Missing runner credentials must fail the job; never scan runner filesystems or borrow local developer credentials.

## Stop response

`<GitLab host / OpenShift alias>: approved credential unavailable or invalid. Expected: <exact configured source>. I did not search other locations or try another identity. To provision: <human instructions>.`

## References

- https://docs.gitlab.com/cli/authentication/
- https://kubernetes.io/docs/reference/access-authn-authz/service-accounts-admin/
