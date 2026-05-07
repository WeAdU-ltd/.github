#!/usr/bin/env bash
# Probe IAM for GitHub OIDC identity provider(s). Requires AWS CLI v2 + credentials.
# Usage: bash scripts/aws_github_oidc_probe.sh

set -euo pipefail

if ! command -v aws >/dev/null 2>&1; then
  printf '%s\n' "AWS CLI introuvable. Installe awscli v2 puis configure les credentials (compte weadu)." >&2
  printf '%s\n' "Doc : https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html" >&2
  exit 2
fi

echo "=== STS identity ==="
aws sts get-caller-identity

echo ""
echo "=== IAM OIDC identity providers (ARN list) ==="
providers_json="$(aws iam list-open-id-connect-providers --output json)"
echo "$providers_json"

arns="$(echo "$providers_json" | python3 -c "
import json,sys
j=json.load(sys.stdin)
for u in j.get('OpenIDConnectProviderList',[]):
    print(u['Arn'])
" 2>/dev/null || true)"

if [[ -z "${arns// }" ]]; then
  echo ""
  echo "Aucun fournisseur OIDC IAM. Créer celui de GitHub (issuer token.actions.githubusercontent.com) une fois."
  exit 0
fi

echo ""
echo "=== Detail per provider (issuer URL) ==="
while IFS= read -r arn; do
  [[ -z "$arn" ]] && continue
  echo "--- $arn ---"
  aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$arn" --query 'Url' --output text 2>/dev/null || echo "(describe failed)"
done <<< "$arns"

echo ""
echo "Si tu vois https://token.actions.githubusercontent.com , OIDC GitHub est présent."
