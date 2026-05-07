#!/usr/bin/env bash
set -euo pipefail
if ! command -v aws >/dev/null 2>&1; then
  echo "AWS CLI introuvable." >&2
  exit 2
fi
echo "=== STS ==="
aws sts get-caller-identity
echo ""
echo "=== OIDC providers ==="
aws iam list-open-id-connect-providers --output json
arns=$(aws iam list-open-id-connect-providers --query 'OpenIDConnectProviderList[].Arn' --output text)
for arn in $arns; do
  echo "--- $arn ---"
  aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$arn" --query Url --output text 2>/dev/null || true
done
