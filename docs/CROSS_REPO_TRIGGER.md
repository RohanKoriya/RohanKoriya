# Refreshing the profile when another repository changes (optional)

The profile already refreshes **daily**, on **every push** that touches the generator/config,
and on demand. A repository you own can also ask the profile to refresh *immediately*
(for example after a release). GitHub does not do this automatically across repositories, so it
needs one token and one small workflow.

## 1. Create a token (once)
GitHub → Settings → Developer settings → Fine-grained personal access tokens → *Generate new token*
- Resource owner: you · Repository access: **Only select repositories → your profile repo**
- Permissions → Repository → **Contents: Read and write** (this is what permits `repository_dispatch`)
- Copy the token.

## 2. Store it in the *project* repository
Project repo → Settings → Secrets and variables → Actions → **New repository secret**
Name: `PROFILE_DISPATCH_TOKEN`, value: the token.

## 3. Add this workflow to the project repository
`.github/workflows/ping-profile.yml`
```yaml
name: Ping profile
on:
  release:
    types: [published]
  push:
    branches: [main]
permissions: {}
jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - run: |
          curl -fsS -X POST \
            -H "Authorization: Bearer ${{ secrets.PROFILE_DISPATCH_TOKEN }}" \
            -H "Accept: application/vnd.github+json" \
            https://api.github.com/repos/RohanKoriya/RohanKoriya/dispatches \
            -d '{"event_type":"profile-refresh"}'
```
The profile workflow already listens for `repository_dispatch` of type `profile-refresh`.
Note: `repository_dispatch` and `schedule` only run from the profile repo's **default branch**.

## Good to know
- GitHub pauses scheduled workflows in a public repo after 60 days without repository activity.
  The daily commit keeps it alive because contribution numbers change; if you ever see the
  schedule stop, press **Run workflow** once.
- Contribution counts follow GitHub's own rules; private contributions only appear if you use a
  token with `read:user` (classic) *and* enabled "Private contributions" on your profile.
