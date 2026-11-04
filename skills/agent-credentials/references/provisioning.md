# Team credential provisioning (human/operator runbook)

This procedure reuses **GitLab CLI**, **OpenShift native RBAC and kubeconfig**, and optionally an organization-approved **1Password/Vault** shared vault. It does not establish a new credential service. This is for *local supervised agents*. CI/CD identities are configured separately.

## Public, versioned namespace registry

In each consuming project, commit `.agent-credentials/namespaces.json` with only public-internal metadata, using `namespaces.example.json` from this skill as a template. Maintain one named entry per namespace (typically 5–10). Never put tokens, client certificates, private keys, CA PEM blobs, passwords, or secret-vault access tokens in this registry. Confirm the expected API server URL and ServiceAccount identity from your cluster administrator.

## OpenShift: team administrator actions

For each namespace, an authorized administrator should:

1. Create or choose a dedicated ServiceAccount, e.g. `research-agent-deployer` (one per namespace, never the `default` ServiceAccount). Use `oc -n <namespace> create serviceaccount research-agent-deployer` if absent.
2. Grant a **minimal namespaced Role and RoleBinding**, restricting verbs/resources needed for research deployment (get/list/watch/update or create/patch where justified). Avoid the cluster-admin role and permissions to read Secrets unless explicitly required. Review `oc auth can-i` for expected actions.
3. Issue a token with `oc -n <namespace> create token research-agent-deployer --duration=8h` **only from the administrator's interactive terminal**. This is a short-lived TokenRequest example, not a promise the server grants eight hours. Establish a renewal process; Kubernetes may issue significantly shorter tokens.
4. Build a named kubeconfig using an approved tool/workflow that sets the **trusted cluster CA**, API endpoint, target namespace and ServiceAccount bearer token. Do this in a trusted admin workspace; avoid writing token values into shell history or terminal logs. Use `oc config --kubeconfig <output> set-cluster`, `set-credentials`, `set-context` and `use-context` as appropriate; review the resulting file *privately* without posting its content. Ensure TLS validation is active. Do not embed an insecure skip-TLS flag.
5. Store that kubeconfig as an encrypted vault attachment, one vault item per approved alias, with access limited to the research team. Record owner, cluster, namespace, SA name, expiration, rotation procedure and revocation plan as *metadata*, not in the repo.

**Token lifetime tradeoff:** GitLab/OpenShift cannot make one static token both conveniently persistent and short-lived. Prefer short-lived credentials and explicit human refresh, or a centrally managed trusted issuance mechanism (e.g. Vault) if refresh frequency becomes painful. A long-lived Secret-backed Kubernetes ServiceAccount token is possible but discouraged and must be consciously approved; shared tokens also reduce per-person audit attribution. Rotating a shared token requires redistributing/replacing it for all researchers.

**Alternative for production-scale credential lifecycle:** use an organization-approved secrets manager with dynamic Kubernetes credentials or an existing OpenShift/Kubernetes auth integration. Don't write your own token issuer. For a small interactive team, human-managed vault distribution is sufficient.

## Researcher: local installation

The team admin shares *access to the vault*, not the token over chat or a Git repository. Each researcher:

1. Checks out the project and its `.agent-credentials/namespaces.json` registry.
2. Authenticates to the team vault personally and downloads only the approved kubeconfigs for relevant aliases. (Do not ask the coding agent to browse the vault.)
3. On macOS/Linux, make the private directory:

   ```sh
   install -d -m 700 "${XDG_CONFIG_HOME:-$HOME/.config}/ron-ds-skills/openshift"
   ```

4. Save each kubeconfig as `${XDG_CONFIG_HOME:-$HOME/.config}/ron-ds-skills/openshift/<alias>.kubeconfig`; set `chmod 600` for each. On Windows, use an equivalently ACL-protected developer directory and document it for the team; the POSIX instructions above do not port verbatim.
5. With `KUBECONFIG` unset, confirm each *specific* identity without revealing tokens:

   ```sh
   oc --kubeconfig "${XDG_CONFIG_HOME:-$HOME/.config}/ron-ds-skills/openshift/<alias>.kubeconfig" --namespace <namespace> whoami
   # Expected: system:serviceaccount:<namespace>:research-agent-deployer
   ```

6. If a file is missing/expired, retrieve a new approved kubeconfig from the vault or ask its administrator. Never use a different user's kubeconfig as a workaround.

## Researcher: personal GitLab credentials

```sh
install -d -m 700 "${XDG_CONFIG_HOME:-$HOME/.config}/ron-ds-skills/glab"
GLAB_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/ron-ds-skills/glab" \
  glab auth login --hostname <approved-gitlab-host> --setup-git-credential-helper
GLAB_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/ron-ds-skills/glab" \
  glab auth status --hostname <approved-gitlab-host>
```

Login is **per researcher**, preferably through OAuth/browser/device login and OS keyring. If local GitLab only allows PATs, each person creates their own limited-scope expiring PAT. `glab` may fall back to plaintext without a keyring: inspect `glab auth status`; fix local credential store rather than accepting plaintext silently. Do not copy your existing global `glab` config or Git SSH keys into the agent's configured path.

## Agent control and limits

The agent only reads the nonsecret alias registry and verifies the *specified* local credential sources. If absent/invalid, it stops and gives the human the above instructions. It must never auto-run issuance/login, use `~/.kube/config`, retry with another context, or inspect unknown credential locations.

**Security limitation:** Markdown/AGENTS instructions alone cannot prevent an agent with unrestricted terminal and filesystem capabilities from ignoring them. To make this technically enforceable, use an agent sandbox with inaccessible ambient secrets, an allowlisted `oc`/`glab` tool wrapper, or a pre-execution policy hook that blocks direct credential access and bare `oc`. Verify against your actual agent harness before claiming enforcement.
