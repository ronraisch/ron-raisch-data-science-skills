# Human provisioning: personal GitLab + team OpenShift via shared NFS

The agent must not acquire/repair credentials itself. **No password-manager dependency, token discovery, or individual OpenShift distribution.** Use OpenShift native ServiceAccounts/RBAC and GitLab's `glab` CLI.

## 1. Configure the consuming repository

Copy [config.example.json](config.example.json) to the consuming project's `.agent-credentials/config.json`. Set `gitlab.host`, the **absolute** `openshift.credentials_root` on the team NFS, and the approved namespace aliases. Each alias includes its exact kubeconfig *basename*, expected API server, namespace and ServiceAccount. Commit **only this nonsecret registry**. Never commit kubeconfigs, passwords, tokens, certificate private keys or `.env` files.

Expected layout (example, customize to your actual NFS mount):

```text
/mnt/team-nfs/credentials/openshift/
    research-dev.kubeconfig
    research-staging.kubeconfig
```

The path must resolve identically in each researcher's development environment, including devcontainers. Mount the existing NFS at the configured path; do not add local credential fallback paths. NFS ACLs/modes should authorize only the intended team; agents never widen permissions.

## 2. OpenShift: administrator provisions one ServiceAccount per namespace

For each namespace, a human administrator with appropriate access:

1. Creates or selects the designated ServiceAccount (e.g. `oc -n <namespace> create sa research-agent-deployer` if missing).
2. Assigns a namespace-scoped Role and RoleBinding with only the verbs/resources required for deployment. Avoid `cluster-admin`, broad secret listing or unrelated namespaces.
3. Obtains a token **outside the agent**, e.g. `oc -n <namespace> create token research-agent-deployer --duration=8h`. TokenRequest tokens expire (the API server may cap the duration). For persistent shared NFS workflows, plan renewal **before expiry**. If the organization explicitly accepts a longer-lived, Secret-backed ServiceAccount token, document/authorize that decision and rotation; do not silently use it as a default.
4. Creates a kubeconfig for **that** service account, API server and trusted cluster CA, with a context targeting the expected namespace. Use `oc config --kubeconfig <file> set-cluster`, `set-credentials`, `set-context`, `use-context` in a controlled admin terminal or the organization's normal kubeconfig provisioning tool. Avoid typing token contents into logged commands or shell history; ensure TLS verification is enabled.
5. Stores the result at the exact `credentials_root/<alias kubeconfig basename>` configured in the repo. Restrict read access to authorized team members; write/rotation access to administrators. Replace the NFS file atomically during rotation so no reader sees a partially written config. Do not expose its contents in CI logs or commits.
6. Privately verifies `oc --kubeconfig "<NFS-file>" --namespace <namespace> whoami` is `system:serviceaccount:<namespace>:<service_account>` and checks intended RBAC with `oc auth can-i` using that file.

A shared service-account identity is not a per-researcher audit identity. The team administrator owns token lifecycle, expiration, and revocation. A single short-lived token per namespace will require frequent NFS refresh; document ownership and cadence rather than assuming it never expires.

## 3. Researcher: GitLab remains personal

Each researcher installs `glab` and authenticates **interactively** to the approved GitLab host:

```sh
install -d -m 700 "${XDG_CONFIG_HOME:-$HOME/.config}/ron-ds-skills/glab"
GLAB_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/ron-ds-skills/glab" \
  glab auth login --hostname <approved-gitlab-host> --setup-git-credential-helper
GLAB_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/ron-ds-skills/glab" \
  glab auth status --hostname <approved-gitlab-host>
```

Use OAuth where supported or an expiring personal access token with minimum required scopes. Prefer OS keyring storage. If OS keyring support is unavailable (e.g. headless devcontainer), stop and ask for a team-approved personal authentication method rather than silently saving a plaintext token. Never use a shared GitLab identity.

## 4. Missing or invalid credentials

The coding agent reports the **exact** configured path/host and gives the researcher these steps. It must not search NFS directories, try `~/.kube/config`, read an alternate environment token, ask OpenShift to create a new token, use personal `oc login`, or switch namespace/identity.

For missing OpenShift file, contact the team administrator to create/restore the **configured NFS kubeconfig**. For access denied, check NFS mount/ACL with the admin; for token expiry, ask the admin to rotate it centrally. For missing GitLab login, the **researcher** runs the login above.

## 5. GitLab CI jobs versus local agents

Local agent GitLab authentication is personal and **never copied into CI**. CI pipelines use their designated runner/job identities and GitLab protected variables or permissions. A CI runner can use a team NFS kubeconfig only if that mount and identity are deliberately authorized for the job and protected environment; otherwise configure a CI-specific credential source. Absence must stop deployment, not trigger credential discovery. See [gitlab-cicd](../../gitlab-cicd/SKILL.md).

**Limit:** These markdown instructions are behavioral, not a sandbox boundary. Enforce with shell/tool allowlists and filesystem restrictions if your agent has unrestricted command execution.
