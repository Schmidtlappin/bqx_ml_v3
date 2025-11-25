#!/usr/bin/env python3
"""
Generate gh CLI commands to set all GitHub secrets
"""

import json
import os

# Load the secrets file
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
    data = json.load(f)

repo = data['repository']
secrets = data['secrets']

# Output file for commands
output_file = '/home/micha/bqx_ml_v3/scripts/set_github_secrets.sh'

with open(output_file, 'w') as f:
    f.write("#!/bin/bash\n")
    f.write("# Generated GitHub Secrets Setup Commands\n")
    f.write(f"# Repository: {repo}\n\n")
    f.write("set -e  # Exit on error\n\n")
    f.write("echo '=========================================================================='\n")
    f.write("echo 'BQX ML V3 - SETTING GITHUB SECRETS'\n")
    f.write("echo '=========================================================================='\n\n")

    count = 0
    for secret_name, secret_data in secrets.items():
        if isinstance(secret_data, dict):
            value = secret_data.get('value')
            description = secret_data.get('description', '')
        else:
            value = secret_data
            description = ''

        if value:
            # Handle different value types
            if isinstance(value, dict):
                # JSON value - stringify it
                value_str = json.dumps(value)
                f.write(f"# {secret_name}: {description}\n")
                f.write(f"echo '{value_str}' | gh secret set {secret_name} --repo {repo}\n")
            elif isinstance(value, str):
                f.write(f"# {secret_name}: {description}\n")
                f.write(f"echo '{value}' | gh secret set {secret_name} --repo {repo}\n")
            else:
                f.write(f"# {secret_name}: {description}\n")
                f.write(f"echo '{value}' | gh secret set {secret_name} --repo {repo}\n")

            f.write(f"echo '  ✅ {secret_name}'\n\n")
            count += 1

    f.write("echo ''\n")
    f.write(f"echo '✅ Successfully set {count} GitHub secrets'\n")
    f.write("echo 'Verify at: https://github.com/{}/settings/secrets/actions'\n".format(repo))

# Make executable
os.chmod(output_file, 0o755)

print(f"✅ Generated {output_file}")
print(f"📊 Total secrets to set: {count}")
print("\n📋 Next steps:")
print("1. Authenticate with GitHub: gh auth login")
print(f"2. Run the script: bash {output_file}")
print(f"3. Verify secrets at: https://github.com/{repo}/settings/secrets/actions")
